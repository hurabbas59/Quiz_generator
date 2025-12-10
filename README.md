# Quiz Generator API

A FastAPI backend service for generating quizzes and assignments from documents, with OCR support for extracting handwritten answers.

---

## 🚀 How to Run

### Step 1: Navigate to the project folder
```your folder directory
```

### Step 2: Create a virtual environment (first time only)
```bash
python3 -m venv myenv
```

### Step 3: Activate the virtual environment
```bash
source myenv/bin/activate
```

### Step 4: Install dependencies (first time only)
```bash
pip install -r requirements.txt
```

### Step 5: Set up environment variables
Create a `.env` file in the root folder with your API keys:
```
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
```

### Step 6: Run the server
```bash
python main.py
```
or
```bash
uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

The API will be available at: **http://localhost:8004**

📖 **Swagger Docs**: http://localhost:8004/docs

---

## 📌 API Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate` | POST | Generate quizzes & assignments from documents |
| `/download/quiz` | POST | Download quizzes as Word document |
| `/download/assignment` | POST | Download assignments as Word document |
| `/download/combined` | POST | Download both as single Word document |
| `/ocr/extract` | POST | Extract answers from uploaded files |
| `/ocr/extract-url` | POST | Extract answers from Google Drive URL |
| `/ocr/download` | POST | Download OCR results as ZIP of Word docs |
| `/indexes` | GET | List all Pinecone indexes |
| `/indexes/{name}` | DELETE | Delete a specific index |
| `/health` | GET | Health check |

---

## 🔥 Main Services

---

### 1️⃣ Generation Service (`POST /generate`)

Generates quizzes and assignments from uploaded PDF/DOCX files.

#### Request (Form Data + Files)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `files` | File[] | **required** | PDF or DOCX documents to process |
| `num_quizzes` | int | 1 | Number of quizzes to generate |
| `num_assignments` | int | 0 | Number of assignments to generate |
| `mcq_count` | int | 5 | MCQs per quiz |
| `fill_blanks_count` | int | 3 | Fill-in-the-blank questions per quiz |
| `true_false_count` | int | 2 | True/False questions per quiz |
| `quiz_difficulty` | string | "medium" | "easy", "medium", or "hard" |
| `assignment_questions` | int | 5 | Questions per assignment |
| `assignment_difficulty` | string | "medium" | "easy", "medium", or "hard" |
| `delete_index_after` | bool | true | Delete vector index after generation |

#### Example Request (JavaScript/Fetch)
```javascript
const formData = new FormData();
formData.append('files', file1);
formData.append('files', file2);
formData.append('num_quizzes', 2);
formData.append('num_assignments', 1);
formData.append('mcq_count', 5);
formData.append('fill_blanks_count', 3);
formData.append('true_false_count', 2);
formData.append('quiz_difficulty', 'medium');

const response = await fetch('http://localhost:8004/generate', {
  method: 'POST',
  body: formData
});
```

#### Response
```json
{
  "success": true,
  "message": "Processed 45 chunks. Generated 2 quizzes and 1 assignments. Index: quiz-abc123 (deleted: true)",
  "quizzes": [
    {
      "quiz_number": 1,
      "total_marks": 20,
      "questions": [
        {
          "question_number": 1,
          "question_text": "What is the main purpose of...?",
          "question_type": "MCQ",
          "marks": 2,
          "options": ["Option A", "Option B", "Option C", "Option D"],
          "correct_answer": "Option B",
          "explanation": "Because...",
          "difficulty_level": "medium",
          "topic": "Introduction"
        },
        {
          "question_number": 2,
          "question_text": "The process of ___ is called photosynthesis.",
          "question_type": "Fill in the Blank",
          "marks": 2,
          "options": null,
          "correct_answer": "converting sunlight to energy",
          "explanation": null,
          "difficulty_level": "easy",
          "topic": "Biology"
        },
        {
          "question_number": 3,
          "question_text": "Water boils at 100°C at sea level.",
          "question_type": "True/False",
          "marks": 1,
          "options": null,
          "correct_answer": "True",
          "explanation": "At standard atmospheric pressure...",
          "difficulty_level": "easy",
          "topic": "Physics"
        }
      ]
    }
  ],
  "assignments": [
    {
      "assignment_number": 1,
      "total_marks": 50,
      "questions": [
        {
          "question_number": 1,
          "question_text": "Explain the concept of...",
          "question_type": "Long Answer",
          "marks": 10,
          "expected_length": "500-800 words",
          "key_points": ["Point 1", "Point 2", "Point 3"],
          "difficulty_level": "medium",
          "topic": "Core Concepts"
        }
      ]
    }
  ],
  "total_quizzes": 2,
  "total_assignments": 1
}
```

---

### 2️⃣ OCR Extract Service (`POST /ocr/extract`)

Extracts handwritten answers from uploaded PDF/image files.

#### Request (Form Data + Files)

| Field | Type | Description |
|-------|------|-------------|
| `files` | File[] | **required** | PDF or image files (PNG, JPG) containing handwritten answers |

#### Example Request (JavaScript/Fetch)
```javascript
const formData = new FormData();
formData.append('files', studentFile1);
formData.append('files', studentFile2);

const response = await fetch('http://localhost:8004/ocr/extract', {
  method: 'POST',
  body: formData
});
```

#### Response
```json
{
  "success": true,
  "files_data": [
    {
      "filename": "student1_answers.pdf",
      "pages_processed": 3,
      "raw_text": "Full extracted text...",
      "answers": [
        {
          "answer_number": "1",
          "content": "The student's handwritten answer text...",
          "answer_type": "long_answer",
          "confidence": "high",
          "pages": [1]
        },
        {
          "answer_number": "2",
          "content": "Another answer...",
          "answer_type": "short_answer",
          "confidence": "medium",
          "pages": [1, 2]
        }
      ],
      "quiz_answers": [
        {
          "question_number": "1",
          "selected_option": "B",
          "confidence": "high"
        }
      ],
      "total_answers": 5,
      "extraction_stats": [...],
      "success": true,
      "error": null
    }
  ],
  "total_files": 1,
  "total_pages": 3,
  "total_answers": 5
}
```

---

### 3️⃣ OCR Extract from URL (`POST /ocr/extract-url`)

Extracts answers from Google Drive link (file or folder).

#### Request (Form Data)

| Field | Type | Description |
|-------|------|-------------|
| `drive_url` | string | **required** | Google Drive file or folder URL |

#### Example Request
```javascript
const formData = new FormData();
formData.append('drive_url', 'https://drive.google.com/drive/folders/xxxxx');

const response = await fetch('http://localhost:8004/ocr/extract-url', {
  method: 'POST',
  body: formData
});
```

#### Response
Same structure as `/ocr/extract`

---

### 4️⃣ Download Endpoints

#### Download Quiz (`POST /download/quiz`)
```javascript
const response = await fetch('http://localhost:8004/download/quiz', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    quizzes: [...] // Array of quiz objects from /generate response
  })
});

// Response is a .docx file blob
const blob = await response.blob();
```

#### Download Assignment (`POST /download/assignment`)
```javascript
const response = await fetch('http://localhost:8004/download/assignment', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    assignments: [...] // Array of assignment objects from /generate response
  })
});
```

#### Download Combined (`POST /download/combined`)
```javascript
const response = await fetch('http://localhost:8004/download/combined', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    quizzes: [...],
    assignments: [...]
  })
});
```

#### Download OCR Results (`POST /ocr/download`)
```javascript
const response = await fetch('http://localhost:8004/ocr/download', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    files_data: [...] // Array from /ocr/extract response
  })
});

// Response is a .zip file containing Word documents
const blob = await response.blob();
```

---

## ⚡ Quick Test with cURL

### Test Health
```bash
curl http://localhost:8004/health
```

### Generate Quiz
```bash
curl -X POST http://localhost:8004/generate \
  -F "files=@document.pdf" \
  -F "num_quizzes=1" \
  -F "mcq_count=5"
```

### OCR Extract
```bash
curl -X POST http://localhost:8004/ocr/extract \
  -F "files=@student_answers.pdf"
```

---

## 🛠 Troubleshooting

1. **Port already in use**: Change port in `main.py` or use `--port 8005`
2. **API key errors**: Make sure `.env` file has valid `OPENAI_API_KEY` and `PINECONE_API_KEY`
3. **File upload fails**: Ensure files are PDF or DOCX (for generation) or PDF/images (for OCR)

---

## 📞 Support

If you have issues, check the Swagger docs at `http://localhost:8004/docs` for interactive API testing.

