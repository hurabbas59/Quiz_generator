# 📚 Complete Guide: Quiz Generator System

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    QUIZ GENERATOR SYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │  Streamlit   │────────▶│   FastAPI    │                  │
│  │     UI       │  HTTP   │   Backend    │                  │
│  │  (Port 8501) │         │  (Port 8004) │                  │
│  └──────────────┘         └──────────────┘                  │
│                                    │                          │
│                                    ▼                          │
│  ┌──────────────────────────────────────────────┐            │
│  │           SERVICES LAYER                      │            │
│  ├──────────────────────────────────────────────┤            │
│  │ • GenerationService    (Quiz/Assignment)     │            │
│  │ • OCRService           (Text Extraction)     │            │
│  │ • CheckingPapersService (Grading)            │            │
│  │ • DocumentService      (Word/Excel Export)   │            │
│  └──────────────────────────────────────────────┘            │
│                                    │                          │
│                                    ▼                          │
│  ┌──────────────────────────────────────────────┐            │
│  │         EXTERNAL SERVICES                      │            │
│  ├──────────────────────────────────────────────┤            │
│  │ • OpenAI GPT-4o-mini    (Text Generation)     │            │
│  │ • OpenAI GPT-4o        (Vision/OCR)           │            │
│  │ • OpenAI Embeddings    (Vector Embeddings)    │            │
│  │ • Pinecone             (Vector Database)      │            │
│  └──────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
QUIZ GENERATOR/
├── main.py                          # FastAPI app with all endpoints
├── streamlit_app.py                 # Streamlit UI frontend
├── models.py                        # Pydantic models (request/response)
├── requirements.txt                 # Python dependencies
│
├── services/                        # Business logic services
│   ├── generation_service.py        # Quiz/Assignment generation
│   ├── ocr_service.py              # OCR text extraction
│   ├── checking_papers_service.py   # Paper grading service
│   └── document_service.py          # Word/Excel document generation
│
├── prompts/                          # AI prompts
│   ├── generation_prompts.py        # Quiz generation prompts
│   ├── ocr_prompts.py               # OCR extraction prompts
│   └── checking_papers_prompts.py   # Grading prompts
│
├── llm_models/                      # LLM configuration
│   └── llm_models.py                # OpenAI models setup
│
├── vectordb/                        # Vector database operations
│   ├── vector_ops.py               # Pinecone operations
│   └── chunking.py                  # Document chunking
│
├── utils/                           # Utilities
│   └── logger.py                    # Logging utilities
│
└── config/                         # Configuration
    └── config.py                    # Environment variables
```

---

## 🔄 How Each Service Works

### 1️⃣ **Generation Service** (`services/generation_service.py`)

**Purpose:** Generate quizzes and assignments from uploaded documents

**Flow:**
```
1. Upload PDF/DOCX files
   ↓
2. Chunk documents into smaller pieces (DocumentChunker)
   ↓
3. Create embeddings (OpenAI text-embedding-3-large)
   ↓
4. Store in Pinecone vector database
   ↓
5. Retrieve relevant chunks based on query
   ↓
6. Send to GPT-4o-mini with prompts
   ↓
7. Parse JSON response → Quiz/Assignment objects
   ↓
8. Return structured data
```

**Key Functions:**
- `process_uploaded_files()` - Chunk and store documents
- `generate_quiz()` - Generate one quiz
- `generate_assignment()` - Generate one assignment
- `generate_all()` - Generate multiple quizzes/assignments in parallel

**API Endpoint:** `POST /generate`

---

### 2️⃣ **OCR Service** (`services/ocr_service.py`)

**Purpose:** Extract handwritten/typed text from PDFs/images

**Flow:**
```
1. Upload PDF/image files
   ↓
2. Convert PDF pages to images (PyMuPDF)
   ↓
3. Process images in parallel (ThreadPoolExecutor)
   ↓
4. Send each image to GPT-4o Vision API
   ↓
5. AI extracts text and structures answers
   ↓
6. Consolidate answers across pages
   ↓
7. Return structured answer data
```

**Key Functions:**
- `process_uploaded_file()` - Process single file
- `process_multiple_files()` - Process multiple files
- `process_google_drive_link()` - Download from Google Drive
- `_pdf_to_images()` - Convert PDF to images
- `_process_pages_parallel()` - Parallel processing

**API Endpoints:**
- `POST /ocr/extract` - Upload files
- `POST /ocr/extract-url` - Google Drive URL
- `POST /ocr/download` - Download as Word docs ZIP

---

### 3️⃣ **Checking Papers Service** (`services/checking_papers_service.py`)

**Purpose:** Grade student papers against answer key semantically

**Flow:**
```
1. Upload answer key PDF
   ↓
2. Extract text from answer key (OCR Service)
   ↓
3. Parse answer key structure (GPT-4o-mini)
   - Identify questions
   - Extract correct answers
   - Determine assessment type (quiz/assignment)
   ↓
4. For each student paper:
   a. Extract student name/roll number (GPT-4o Vision)
   b. Extract student answers (OCR Service)
   c. Compare with answer key semantically (GPT-4o-mini)
   d. Award marks based on understanding
   ↓
5. Compile all results
   ↓
6. Generate Excel spreadsheet
```

**Key Functions:**
- `process_answer_key()` - Parse answer key
- `_extract_student_info_from_image()` - Get name/roll number
- `_grade_answers()` - Semantic grading
- `_process_single_student()` - Process one student
- `check_papers_from_uploads()` - Upload method
- `check_papers_from_drive()` - Google Drive method
- `generate_results_excel()` - Create Excel file

**API Endpoints:**
- `POST /check-papers/upload` - Upload files
- `POST /check-papers/drive` - Google Drive
- `POST /check-papers/download-excel` - Download Excel

---

### 4️⃣ **Document Service** (`services/document_service.py`)

**Purpose:** Generate Word documents and Excel files

**Key Functions:**
- `create_quiz_document()` - Quiz Word doc
- `create_assignment_document()` - Assignment Word doc
- `create_combined_document()` - Combined Word doc
- `create_student_answer_document()` - Student answer Word doc
- `create_all_student_documents()` - ZIP of Word docs

**Uses:** `python-docx` library for Word, `openpyxl` for Excel

---

## 🔌 Complete API Reference

### **Base URL:** `http://localhost:8004`

---

### 📝 **Generation APIs**

#### `POST /generate`
Generate quizzes and assignments from documents.

**Request:**
- **Method:** POST
- **Content-Type:** multipart/form-data
- **Parameters:**
  - `files` (File[]): PDF/DOCX documents
  - `num_quizzes` (int): Number of quizzes (default: 1)
  - `num_assignments` (int): Number of assignments (default: 0)
  - `mcq_count` (int): MCQs per quiz (default: 5)
  - `fill_blanks_count` (int): Fill blanks per quiz (default: 3)
  - `true_false_count` (int): True/False per quiz (default: 2)
  - `quiz_difficulty` (str): "easy"/"medium"/"hard" (default: "medium")
  - `assignment_questions` (int): Questions per assignment (default: 5)
  - `assignment_difficulty` (str): "easy"/"medium"/"hard" (default: "medium")
  - `delete_index_after` (bool): Delete Pinecone index after (default: true)

**Response:**
```json
{
  "success": true,
  "message": "Processed 45 chunks. Generated 2 quizzes...",
  "quizzes": [...],
  "assignments": [...],
  "total_quizzes": 2,
  "total_assignments": 1
}
```

---

#### `POST /download/quiz`
Download quizzes as Word document.

**Request:**
```json
{
  "quizzes": [...],  // From /generate response
  "assignments": []
}
```

**Response:** Word document (.docx) file

---

#### `POST /download/assignment`
Download assignments as Word document.

**Request:**
```json
{
  "quizzes": [],
  "assignments": [...]  // From /generate response
}
```

**Response:** Word document (.docx) file

---

#### `POST /download/combined`
Download quizzes + assignments as single Word document.

**Request:**
```json
{
  "quizzes": [...],
  "assignments": [...]
}
```

**Response:** Word document (.docx) file

---

### 📷 **OCR APIs**

#### `POST /ocr/extract`
Extract handwritten answers from uploaded files.

**Request:**
- **Method:** POST
- **Content-Type:** multipart/form-data
- **Parameters:**
  - `files` (File[]): PDF or image files

**Response:**
```json
{
  "success": true,
  "files_data": [
    {
      "filename": "student1.pdf",
      "pages_processed": 3,
      "raw_text": "...",
      "answers": [...],
      "quiz_answers": [...],
      "total_answers": 5
    }
  ],
  "total_files": 1,
  "total_pages": 3,
  "total_answers": 5
}
```

---

#### `POST /ocr/extract-url`
Extract answers from Google Drive URL.

**Request:**
- **Method:** POST
- **Content-Type:** multipart/form-data
- **Parameters:**
  - `drive_url` (str): Google Drive folder/file URL

**Response:** Same as `/ocr/extract`

---

#### `POST /ocr/download`
Download OCR results as ZIP of Word documents.

**Request:**
```json
{
  "files_data": [...]  // From /ocr/extract response
}
```

**Response:** ZIP file containing Word documents

---

### ✅ **Paper Checking APIs**

#### `POST /check-papers/upload`
Grade student papers from file uploads.

**Request:**
- **Method:** POST
- **Content-Type:** multipart/form-data
- **Parameters:**
  - `answer_key` (File): Answer key PDF/DOCX
  - `student_papers` (File[]): Student paper PDFs

**Response:**
```json
{
  "success": true,
  "assessment_type": "assignment",
  "total_students": 3,
  "successful": 3,
  "failed": 0,
  "answer_key_info": {
    "total_questions": 5,
    "total_marks": 50
  },
  "results": [
    {
      "filename": "student1.pdf",
      "student_name": "Ali Khan",
      "roll_number": "2021-CS-101",
      "total_obtained": 42,
      "total_max": 50,
      "grading": {
        "evaluations": [...],
        "total_obtained": 42,
        "total_max": 50
      }
    }
  ]
}
```

---

#### `POST /check-papers/drive`
Grade student papers from Google Drive.

**Request:**
- **Method:** POST
- **Content-Type:** multipart/form-data
- **Parameters:**
  - `answer_key` (File): Answer key PDF/DOCX
  - `drive_url` (str): Google Drive folder URL

**Response:** Same as `/check-papers/upload`

---

#### `POST /check-papers/download-excel`
Download grading results as Excel.

**Request:**
```json
{
  "checking_results": {...}  // Full response from /check-papers/*
}
```

**Response:** Excel file (.xlsx)

---

### 🗂️ **Index Management APIs**

#### `GET /indexes`
List all Pinecone indexes.

**Response:**
```json
{
  "success": true,
  "indexes": [...],
  "count": 5
}
```

---

#### `DELETE /indexes/{index_name}`
Delete a specific Pinecone index.

**Response:**
```json
{
  "success": true,
  "message": "Index 'quiz-abc123' deleted"
}
```

---

### ❤️ **Health Check**

#### `GET /health`
Check if API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "Quiz Generator API"
}
```

---

## 🧪 How to Test

### **Prerequisites**

1. **Install Dependencies:**
```bash
cd "/home/hur-abbas/Documents/Ahmer project/QUIZ GENERATOR"
source myenv/bin/activate
pip install -r requirements.txt
```

2. **Set Up Environment Variables:**
Create `.env` file:
```
OPENAI_API_KEY=your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here
```

3. **Start FastAPI Server:**
```bash
python main.py
# OR
uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

4. **Start Streamlit UI (Optional):**
```bash
streamlit run streamlit_app.py --server.port 8501
```

---

### **Testing Methods**

### **Method 1: Streamlit UI (Easiest)** ⭐

1. **Start both servers:**
   ```bash
   # Terminal 1: FastAPI
   python main.py
   
   # Terminal 2: Streamlit
   streamlit run streamlit_app.py
   ```

2. **Open browser:** http://localhost:8501

3. **Test each tab:**
   - **Tab 1:** Generate Quiz/Assignment
     - Upload documents
     - Configure settings
     - Click "Generate"
     - Download Word documents
   
   - **Tab 2:** OCR - Extract Answers
     - Upload student papers
     - Extract answers
     - Download Word documents ZIP
   
   - **Tab 3:** Check Papers ⭐ NEW
     - Upload answer key
     - Upload student papers (or Google Drive link)
     - Click "Check Papers"
     - View results
     - Download Excel

---

### **Method 2: Swagger UI (Interactive API Docs)**

1. **Start FastAPI:**
   ```bash
   python main.py
   ```

2. **Open browser:** http://localhost:8004/docs

3. **Test endpoints:**
   - Click on any endpoint
   - Click "Try it out"
   - Fill in parameters
   - Click "Execute"
   - See response

---

### **Method 3: cURL (Command Line)**

#### Test Health:
```bash
curl http://localhost:8004/health
```

#### Test Generation:
```bash
curl -X POST http://localhost:8004/generate \
  -F "files=@document.pdf" \
  -F "num_quizzes=1" \
  -F "mcq_count=5"
```

#### Test OCR:
```bash
curl -X POST http://localhost:8004/ocr/extract \
  -F "files=@student_answers.pdf"
```

#### Test Paper Checking:
```bash
curl -X POST http://localhost:8004/check-papers/upload \
  -F "answer_key=@answer_key.pdf" \
  -F "student_papers=@student1.pdf" \
  -F "student_papers=@student2.pdf"
```

---

### **Method 4: Python Script**

Create `test_api.py`:

```python
import requests

API_URL = "http://localhost:8004"

# Test 1: Health Check
response = requests.get(f"{API_URL}/health")
print("Health:", response.json())

# Test 2: Generate Quiz
with open("document.pdf", "rb") as f:
    files = {"files": ("document.pdf", f, "application/pdf")}
    data = {
        "num_quizzes": 1,
        "mcq_count": 5
    }
    response = requests.post(f"{API_URL}/generate", files=files, data=data)
    print("Generation:", response.json())

# Test 3: Check Papers
with open("answer_key.pdf", "rb") as ak, open("student1.pdf", "rb") as sp:
    files = {
        "answer_key": ("answer_key.pdf", ak, "application/pdf"),
        "student_papers": ("student1.pdf", sp, "application/pdf")
    }
    response = requests.post(f"{API_URL}/check-papers/upload", files=files)
    result = response.json()
    print("Checking Results:", result)
    
    # Download Excel
    excel_response = requests.post(
        f"{API_URL}/check-papers/download-excel",
        json={"checking_results": result}
    )
    with open("results.xlsx", "wb") as excel_file:
        excel_file.write(excel_response.content)
    print("Excel saved!")
```

Run:
```bash
python test_api.py
```

---

## 🔍 Testing Checklist

### ✅ **Basic Functionality**

- [ ] FastAPI server starts without errors
- [ ] Streamlit UI loads (if using)
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Swagger docs accessible at `/docs`

### ✅ **Generation Service**

- [ ] Upload PDF/DOCX files
- [ ] Generate quiz with custom settings
- [ ] Generate assignment
- [ ] Download quiz Word document
- [ ] Download assignment Word document
- [ ] Download combined document

### ✅ **OCR Service**

- [ ] Upload PDF/image files
- [ ] Extract handwritten text
- [ ] Extract from Google Drive
- [ ] Download Word documents ZIP
- [ ] Verify extracted answers are structured

### ✅ **Paper Checking Service** ⭐ NEW

- [ ] Upload answer key PDF
- [ ] Upload student papers
- [ ] Check papers from Google Drive
- [ ] Verify student name/roll number extraction
- [ ] Verify semantic grading (not word-for-word)
- [ ] Download Excel spreadsheet
- [ ] Verify Excel format (Name | Roll No | A1 | A2 | ... | Total)

---

## 🐛 Common Issues & Solutions

### **Issue: "Cannot connect to API"**
- **Solution:** Make sure FastAPI is running on port 8004
- **Check:** `curl http://localhost:8004/health`

### **Issue: "OPENAI_API_KEY not found"**
- **Solution:** Create `.env` file with your API key
- **Check:** `cat .env`

### **Issue: "Pinecone index error"**
- **Solution:** Check Pinecone API key in `.env`
- **Note:** Indexes are auto-created, no manual setup needed

### **Issue: "openpyxl not installed"**
- **Solution:** `pip install openpyxl`
- **Note:** Already in requirements.txt

### **Issue: "Port already in use"**
- **Solution:** Change port in `main.py` or use `--port 8005`
- **Or:** Kill process using port: `lsof -ti:8004 | xargs kill`

### **Issue: "Student name shows Unknown"**
- **Normal:** If name/roll number can't be detected from first page
- **Grading still works**, just without student info

---

## 📊 Data Flow Examples

### **Example 1: Generate Quiz**

```
User uploads document.pdf
    ↓
GenerationService.process_uploaded_files()
    ↓
DocumentChunker chunks the PDF
    ↓
Create embeddings (OpenAI)
    ↓
Store in Pinecone
    ↓
Retrieve relevant chunks
    ↓
Send to GPT-4o-mini with prompt
    ↓
Parse JSON response
    ↓
Return Quiz objects
    ↓
User downloads Word document
```

### **Example 2: Check Papers**

```
Teacher uploads answer_key.pdf
    ↓
OCR extracts text
    ↓
GPT-4o-mini parses structure
    ↓
Answer key ready: {questions: [...], correct_answers: [...]}
    ↓
For each student paper:
    ↓
  Extract name/roll (GPT-4o Vision)
    ↓
  Extract answers (OCR)
    ↓
  Compare semantically (GPT-4o-mini)
    ↓
  Award marks
    ↓
Compile all results
    ↓
Generate Excel spreadsheet
    ↓
Teacher downloads Excel
```

---

## 🎯 Key Features Explained

### **Semantic Grading**
- **What:** Compares meaning, not exact words
- **Example:** "H2O" = "water" = "two hydrogen atoms and one oxygen" ✅
- **Benefit:** Fair grading even if student uses different wording

### **Parallel Processing**
- **Where:** OCR page processing, quiz generation
- **Benefit:** Faster processing (3-5 files at once)

### **Vector Database (Pinecone)**
- **Purpose:** Store document chunks for retrieval
- **Why:** Efficient similarity search for relevant content
- **Auto-cleanup:** Indexes deleted after generation (optional)

### **Vision AI (GPT-4o)**
- **Purpose:** Read handwritten text and extract student info
- **Why:** Handwriting is hard for regular OCR

---

## 📝 Quick Start Commands

```bash
# 1. Activate environment
source myenv/bin/activate

# 2. Start FastAPI
python main.py

# 3. (Optional) Start Streamlit in new terminal
streamlit run streamlit_app.py

# 4. Test health
curl http://localhost:8004/health

# 5. Open Swagger UI
# Browser: http://localhost:8004/docs

# 6. Open Streamlit UI
# Browser: http://localhost:8501
```

---

## 🎓 Summary

**This system has 3 main services:**

1. **Generation** - Create quizzes/assignments from documents
2. **OCR** - Extract handwritten answers from papers
3. **Checking** - Grade papers semantically against answer keys

**All services:**
- Use AI (OpenAI GPT models)
- Support file uploads and Google Drive
- Generate downloadable documents (Word/Excel)
- Have both API endpoints and Streamlit UI

**Testing:**
- **Easiest:** Use Streamlit UI (http://localhost:8501)
- **API Testing:** Use Swagger UI (http://localhost:8004/docs)
- **Automated:** Write Python scripts with `requests` library

---

## 🚀 Ready to Test!

1. **Start servers:**
   ```bash
   python main.py  # Terminal 1
   streamlit run streamlit_app.py  # Terminal 2
   ```

2. **Open Streamlit:** http://localhost:8501

3. **Try the new "Check Papers" tab!** ⭐

---

**Need help?** Check the logs in terminal or use Swagger UI for detailed API testing.
