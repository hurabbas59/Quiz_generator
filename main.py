from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import Response
from typing import List

from models import (
    GenerationResponse, 
    QuizConfig, 
    AssignmentConfig,
    DownloadRequest,
    OCRDownloadRequest
)
from services.generation_service import GenerationService
from services.document_service import DocumentService
from services.ocr_service import OCRService
from vectordb.vector_ops import PineconeVectorDB
from utils.logger import log_step, log_success, log_error, logger

app = FastAPI(title="Quiz Generator API")
service = GenerationService()

# ============== GENERATION ENDPOINTS ==============

@app.post("/generate", response_model=GenerationResponse)
async def generate_quiz_and_assignments(
    files: List[UploadFile] = File(...),
    num_quizzes: int = Form(default=1),
    num_assignments: int = Form(default=0),
    mcq_count: int = Form(default=5),
    fill_blanks_count: int = Form(default=3),
    true_false_count: int = Form(default=2),
    quiz_difficulty: str = Form(default="medium"),
    assignment_questions: int = Form(default=5),
    assignment_difficulty: str = Form(default="medium"),
    delete_index_after: bool = Form(default=True)
):
    """Generate quizzes and assignments from uploaded documents."""
    log_step("API: /generate", f"Files: {len(files)}, Quizzes: {num_quizzes}, Assignments: {num_assignments}")
    
    try:
        # service = GenerationService()
        
        log_step("Processing files", f"Uploading {len(files)} files")
        chunks_count = await service.process_uploaded_files(files)
        log_success(f"Processed {chunks_count} chunks")
        
        quiz_config = QuizConfig(
            mcq_count=mcq_count,
            fill_blanks_count=fill_blanks_count,
            true_false_count=true_false_count,
            difficulty=quiz_difficulty
        )
        
        assignment_config = AssignmentConfig(
            num_questions=assignment_questions,
            difficulty=assignment_difficulty
        )
        
        log_step("Generating content", f"Quizzes: {num_quizzes}, Assignments: {num_assignments}")
        result = service.generate_all(
            num_quizzes=num_quizzes,
            num_assignments=num_assignments,
            quiz_config=quiz_config,
            assignment_config=assignment_config,
            delete_after=delete_index_after
        )
        
        log_success(f"Generated {len(result['quizzes'])} quizzes and {len(result['assignments'])} assignments")
        
        return GenerationResponse(
            success=True,
            message=f"Processed {chunks_count} chunks. Generated {num_quizzes} quizzes and {num_assignments} assignments. Index: {result['index_name']} (deleted: {result['index_deleted']})",
            quizzes=result["quizzes"],
            assignments=result["assignments"],
            total_quizzes=num_quizzes,
            total_assignments=num_assignments
        )
    
    except Exception as e:
        log_error("Generation failed", e)
        return GenerationResponse(
            success=False,
            message=str(e),
            quizzes=[],
            assignments=[]
        )


# ============== DOCUMENT DOWNLOAD ENDPOINTS ==============

@app.post("/download/quiz")
async def download_quiz_document(request: DownloadRequest):
    """Generate and download quiz as Word document."""
    log_step("API: /download/quiz", f"Quizzes: {len(request.quizzes)}")
    
    try:
        doc_bytes = DocumentService.create_quiz_document(request.quizzes)
        log_success("Quiz document generated")
        
        return Response(
            content=doc_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=quizzes.docx"}
        )
    except Exception as e:
        log_error("Quiz document generation failed", e)
        return {"success": False, "error": str(e)}


@app.post("/download/assignment")
async def download_assignment_document(request: DownloadRequest):
    """Generate and download assignment as Word document."""
    log_step("API: /download/assignment", f"Assignments: {len(request.assignments)}")
    
    try:
        doc_bytes = DocumentService.create_assignment_document(request.assignments)
        log_success("Assignment document generated")
        
        return Response(
            content=doc_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=assignments.docx"}
        )
    except Exception as e:
        log_error("Assignment document generation failed", e)
        return {"success": False, "error": str(e)}


@app.post("/download/combined")
async def download_combined_document(request: DownloadRequest):
    """Generate and download combined quiz and assignment as Word document."""
    log_step("API: /download/combined", f"Quizzes: {len(request.quizzes)}, Assignments: {len(request.assignments)}")
    
    try:
        doc_bytes = DocumentService.create_combined_document(request.quizzes, request.assignments)
        log_success("Combined document generated")
        
        return Response(
            content=doc_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=quiz_assignment_package.docx"}
        )
    except Exception as e:
        log_error("Combined document generation failed", e)
        return {"success": False, "error": str(e)}


# ============== OCR ENDPOINTS ==============

@app.post("/ocr/extract")
async def extract_answers_from_files(
    files: List[UploadFile] = File(...)
):
    """Extract handwritten answers from uploaded PDF/image files.
    Returns each file's answers separately.
    """
    log_step("API: /ocr/extract", f"Files: {len(files)}")
    
    try:
        ocr_service = OCRService()
        result = await ocr_service.process_multiple_files(files)
        log_success(f"Extracted {result['total_answers']} answers from {result['total_files']} files")
        return result
    except Exception as e:
        log_error("OCR extraction failed", e)
        return {"success": False, "error": str(e)}


@app.post("/ocr/extract-url")
async def extract_answers_from_url(
    drive_url: str = Form(...)
):
    """Extract handwritten answers from Google Drive URL (file or folder).
    Returns each file's answers separately.
    """
    log_step("API: /ocr/extract-url", f"URL: {drive_url[:50]}...")
    
    try:
        ocr_service = OCRService()
        result = ocr_service.process_google_drive_link(drive_url)
        log_success(f"Extracted {result['total_answers']} answers from {result['total_files']} files")
        return result
    except Exception as e:
        log_error("OCR URL extraction failed", e)
        return {"success": False, "error": str(e)}


@app.post("/ocr/download")
async def download_ocr_results(request: OCRDownloadRequest):
    """Download OCR results as ZIP of Word documents (one per file/student)."""
    log_step("API: /ocr/download", f"Files: {len(request.files_data)}")
    
    try:
        zip_bytes = DocumentService.create_all_student_documents(request.files_data)
        log_success(f"Created ZIP with {len(request.files_data)} Word documents")
        
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=student_answers.zip"}
        )
    except Exception as e:
        log_error("OCR download failed", e)
        return {"success": False, "error": str(e)}


# ============== INDEX MANAGEMENT ENDPOINTS ==============

@app.get("/indexes")
async def list_indexes():
    """List all active Pinecone indexes."""
    log_step("API: /indexes", "Listing all indexes")
    
    try:
        indexes = PineconeVectorDB.list_all_indexes()
        log_success(f"Found {len(indexes)} indexes")
        return {"success": True, "indexes": indexes, "count": len(indexes)}
    except Exception as e:
        log_error("Failed to list indexes", e)
        return {"success": False, "error": str(e)}


@app.delete("/indexes/{index_name}")
async def delete_index(index_name: str):
    """Delete a specific Pinecone index."""
    log_step("API: /indexes/delete", f"Index: {index_name}")
    
    try:
        PineconeVectorDB.delete_index_by_name(index_name)
        log_success(f"Index '{index_name}' deleted")
        return {"success": True, "message": f"Index '{index_name}' deleted"}
    except Exception as e:
        log_error(f"Failed to delete index '{index_name}'", e)
        return {"success": False, "error": str(e)}


# ============== HEALTH CHECK ==============

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Quiz Generator API"}


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀quiz Starting Quiz Generator API on port 8004")
    uvicorn.run(app, host="0.0.0.0", port=8004)
