"""
OCR Service for extracting handwritten answers from documents using GPT Vision.
"""
import os
import re
import json
import base64
import tempfile
import shutil
import asyncio
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import UploadFile
import fitz  # PyMuPDF
from PIL import Image
import io
import gdown

from llm_models.llm_models import call_vision_api, process_images_parallel
from prompts.ocr_prompts import OCRPrompts
from utils.logger import log_step, log_success, log_error, log_debug


class OCRService:
    """Service for extracting text from documents using GPT Vision."""
    
    def __init__(self):
        self.max_concurrent = 5  # Max parallel API calls
    
    # ============== IMAGE ENCODING ==============
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image file to base64."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def _pil_to_base64(self, pil_image: Image.Image) -> str:
        """Convert PIL Image to base64."""
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # ============== PDF PROCESSING ==============
    
    def _pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """Convert PDF pages to images using PyMuPDF."""
        log_step("Converting PDF to images", pdf_path)
        
        images = []
        pdf = fitz.open(pdf_path)
        
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            images.append(image)
        
        pdf.close()
        log_success(f"Converted {len(images)} pages")
        return images
    
    # ============== JSON PARSING ==============
    
    def _parse_json(self, response: str) -> Dict:
        """Parse JSON from API response."""
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            return {"raw_text": response, "answers": [], "error": "JSON parse failed"}
    
    # ============== GOOGLE DRIVE ==============
    
    def _is_folder_url(self, url: str) -> bool:
        """Check if URL is a Google Drive folder."""
        return '/folders/' in url
    
    def _download_from_google_drive(self, drive_url: str) -> List[str]:
        """Download files from Google Drive (file or folder)."""
        log_step("Downloading from Google Drive", drive_url[:50])
        
        temp_dir = tempfile.mkdtemp(prefix="gdrive_")
        downloaded_files = []
        
        try:
            if self._is_folder_url(drive_url):
                # Download folder
                gdown.download_folder(url=drive_url, output=temp_dir, quiet=True)
                
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        ext = os.path.splitext(file)[1].lower()
                        if ext in ['.pdf', '.png', '.jpg', '.jpeg', '.webp']:
                            downloaded_files.append(file_path)
            else:
                # Download single file
                match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', drive_url)
                if not match:
                    match = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', drive_url)
                
                if match:
                    file_id = match.group(1)
                    output = os.path.join(temp_dir, "downloaded")
                    gdown.download(f"https://drive.google.com/uc?id={file_id}", output, quiet=True, fuzzy=True)
                    
                    for file in os.listdir(temp_dir):
                        downloaded_files.append(os.path.join(temp_dir, file))
            
            log_success(f"Downloaded {len(downloaded_files)} files")
            return downloaded_files
            
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e
    
    # ============== PARALLEL PAGE PROCESSING ==============
    
    def _process_pages_parallel(self, images: List[Image.Image]) -> List[Dict]:
        """Process multiple pages in parallel using ThreadPoolExecutor."""
        log_step("Processing pages in parallel", f"{len(images)} pages")
        
        def process_single_page(args):
            idx, image = args
            try:
                base64_img = self._pil_to_base64(image)
                response = call_vision_api(
                    base64_img,
                    OCRPrompts.PAGE,
                    OCRPrompts.SYSTEM
                )
                return (idx, self._parse_json(response), None)
            except Exception as e:
                return (idx, None, str(e))
        
        results = [None] * len(images)
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            futures = {
                executor.submit(process_single_page, (i, img)): i 
                for i, img in enumerate(images)
            }
            
            for future in as_completed(futures):
                idx, data, error = future.result()
                if error:
                    log_error(f"Page {idx + 1} failed: {error}")
                    results[idx] = {"error": error, "page": idx + 1}
                else:
                    results[idx] = {"data": data, "page": idx + 1}
                    log_debug(f"Page {idx + 1} processed")
        
        log_success(f"Processed {len(images)} pages")
        return results
    
    # ============== FILE PROCESSING ==============
    
    def _process_file(self, file_path: str, suffix: str) -> Dict:
        """Process a single file and extract text."""
        log_step("Processing file", f"Type: {suffix}")
        
        all_answers = []
        all_raw_text = []
        extraction_stats = []
        pages_processed = 0
        
        if suffix == '.pdf':
            images = self._pdf_to_images(file_path)
            
            # Process all pages in parallel
            page_results = self._process_pages_parallel(images)
            
            for result in page_results:
                page_num = result["page"]
                
                if "error" in result:
                    all_raw_text.append(f"=== PAGE {page_num} === [Error: {result['error']}]")
                    pages_processed += 1
                    continue
                
                data = result["data"]
                page_content = data.get('page_content', data)
                
                # Extract raw text
                raw_text = page_content.get('raw_text', '')
                if raw_text:
                    all_raw_text.append(f"=== PAGE {page_num} ===\n{raw_text}")
                
                # Extract answers
                for answer in page_content.get('answers', []):
                    answer['page'] = page_num
                    all_answers.append(answer)
                
                # Stats
                stats = page_content.get('extraction_stats', {})
                if stats:
                    stats['page'] = page_num
                    extraction_stats.append(stats)
                
                pages_processed += 1
        
        elif suffix in ['.png', '.jpg', '.jpeg', '.webp']:
            base64_img = self._encode_image(file_path)
            response = call_vision_api(
                base64_img,
                OCRPrompts.IMAGE,
                OCRPrompts.SYSTEM
            )
            
            data = self._parse_json(response)
            all_raw_text.append(data.get('raw_text', ''))
            all_answers = data.get('answers', [])
            extraction_stats = [data.get('extraction_stats', {})]
            pages_processed = 1
        
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        # Consolidate answers
        consolidated = self._consolidate_answers(all_answers)
        
        return {
            "success": True,
            "pages_processed": pages_processed,
            "raw_text": "\n\n".join(all_raw_text),
            "answers": consolidated,
            "quiz_answers": [],
            "total_answers": len(consolidated),
            "extraction_stats": extraction_stats
        }
    
    def _consolidate_answers(self, answers: List[Dict]) -> List[Dict]:
        """Consolidate answers that span multiple pages."""
        grouped = {}
        
        for answer in answers:
            num = str(answer.get('answer_number', 'unknown'))
            if num not in grouped:
                grouped[num] = {
                    "answer_number": num,
                    "content": answer.get('content', ''),
                    "answer_type": answer.get('answer_type', 'unknown'),
                    "pages": [answer.get('page', 1)],
                    "confidence": answer.get('confidence', 'medium')
                }
            else:
                grouped[num]['content'] += "\n" + answer.get('content', '')
                if answer.get('page'):
                    grouped[num]['pages'].append(answer.get('page'))
        
        return list(grouped.values())
    
    # ============== PUBLIC METHODS ==============
    
    async def process_uploaded_file(self, file: UploadFile) -> Dict:
        """Process a single uploaded file."""
        log_step("Processing uploaded file", file.filename)
        
        suffix = os.path.splitext(file.filename)[1].lower()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            return self._process_file(tmp_path, suffix)
        finally:
            os.unlink(tmp_path)
    
    def process_google_drive_link(self, drive_url: str) -> Dict:
        """Process files from Google Drive link."""
        log_step("Processing Google Drive", drive_url[:50])
        
        file_paths = self._download_from_google_drive(drive_url)
        temp_dir = os.path.dirname(file_paths[0]) if file_paths else None
        
        try:
            return self._process_multiple_files_sync(file_paths)
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _process_multiple_files_sync(self, file_paths: List[str]) -> Dict:
        """Process multiple files with parallel processing."""
        log_step("Processing multiple files", f"{len(file_paths)} files")
        
        files_data = []
        total_pages = 0
        total_answers = 0
        
        # Process files in parallel
        def process_one(file_path):
            filename = os.path.basename(file_path)
            suffix = os.path.splitext(file_path)[1].lower()
            try:
                result = self._process_file(file_path, suffix)
                return {
                    "filename": filename,
                    "pages_processed": result['pages_processed'],
                    "raw_text": result.get('raw_text', ''),
                    "answers": result['answers'],
                    "quiz_answers": result.get('quiz_answers', []),
                    "total_answers": result['total_answers'],
                    "extraction_stats": result.get('extraction_stats', []),
                    "success": True
                }
            except Exception as e:
                log_error(f"Failed: {filename}", e)
                return {
                    "filename": filename,
                    "error": str(e),
                    "success": False,
                    "raw_text": "",
                    "answers": [],
                    "quiz_answers": [],
                    "extraction_stats": []
                }
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(process_one, file_paths))
        
        for result in results:
            files_data.append(result)
            if result.get('success'):
                total_pages += result.get('pages_processed', 0)
                total_answers += result.get('total_answers', 0)
        
        log_success(f"Processed {len(files_data)} files, {total_answers} answers")
        
        return {
            "success": True,
            "files_data": files_data,
            "total_files": len(files_data),
            "total_pages": total_pages,
            "total_answers": total_answers
        }
    
    async def process_multiple_files(self, files: List[UploadFile]) -> Dict:
        """Process multiple uploaded files."""
        log_step("Processing multiple uploads", f"{len(files)} files")
        
        files_data = []
        total_pages = 0
        total_answers = 0
        
        for file in files:
            result = await self.process_uploaded_file(file)
            
            files_data.append({
                "filename": file.filename,
                "pages_processed": result['pages_processed'],
                "raw_text": result.get('raw_text', ''),
                "answers": result['answers'],
                "quiz_answers": result.get('quiz_answers', []),
                "total_answers": result['total_answers'],
                "extraction_stats": result.get('extraction_stats', []),
                "success": True
            })
            
            total_pages += result['pages_processed']
            total_answers += result['total_answers']
        
        return {
            "success": True,
            "files_data": files_data,
            "total_files": len(files_data),
            "total_pages": total_pages,
            "total_answers": total_answers
        }
