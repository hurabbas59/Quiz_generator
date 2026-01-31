# 🧪 Testing Paper Checking Service

## ✅ Server Status
- **Server is running** at: http://localhost:8004
- **Swagger Docs**: http://localhost:8004/docs
- **Health Check**: http://localhost:8004/health

---

## 🚀 Quick Test Methods

### Method 1: Using Swagger UI (Easiest)

1. Open browser: http://localhost:8004/docs
2. Find the endpoint: **`POST /check-papers/upload`**
3. Click "Try it out"
4. Upload:
   - `answer_key`: Your answer key PDF/DOCX
   - `student_papers`: One or more student paper PDFs
5. Click "Execute"
6. See the results!

---

### Method 2: Using cURL (Command Line)

#### Test with File Uploads:
```bash
curl -X POST http://localhost:8004/check-papers/upload \
  -F "answer_key=@/path/to/answer_key.pdf" \
  -F "student_papers=@/path/to/student1.pdf" \
  -F "student_papers=@/path/to/student2.pdf"
```

#### Test with Google Drive:
```bash
curl -X POST http://localhost:8004/check-papers/drive \
  -F "answer_key=@/path/to/answer_key.pdf" \
  -F "drive_url=https://drive.google.com/drive/folders/YOUR_FOLDER_ID"
```

---

### Method 3: Using Python Script

Create a test file `test_checking.py`:

```python
import requests

# Test endpoint
url = "http://localhost:8004/check-papers/upload"

# Prepare files
files = {
    'answer_key': open('answer_key.pdf', 'rb'),
    'student_papers': [
        open('student1.pdf', 'rb'),
        open('student2.pdf', 'rb')
    ]
}

# Send request
response = requests.post(url, files=files)
print(response.json())

# Close files
for f in files.values():
    if isinstance(f, list):
        for file in f:
            file.close()
    else:
        f.close()
```

---

## 📋 What You Need to Test

### 1. Answer Key File
- **Format**: PDF or DOCX
- **Content**: Should contain questions with correct answers
- **Example structure**:
  ```
  Question 1: What is photosynthesis?
  Answer: The process by which plants convert sunlight into energy.
  Marks: 10
  
  Question 2: Explain the water cycle.
  Answer: The continuous movement of water on Earth...
  Marks: 15
  ```

### 2. Student Papers
- **Format**: PDF (with handwritten or typed answers)
- **Should contain**: Student name, roll number, and answers
- **Multiple files**: You can upload multiple student papers at once

---

## 🎯 Expected Response Format

```json
{
  "success": true,
  "assessment_type": "assignment",
  "total_students": 2,
  "successful": 2,
  "failed": 0,
  "answer_key_info": {
    "total_questions": 3,
    "total_marks": 50
  },
  "results": [
    {
      "filename": "student1.pdf",
      "student_name": "Ali Khan",
      "roll_number": "2021-CS-101",
      "answers_extracted": 3,
      "total_obtained": 42,
      "total_max": 50,
      "grading": {
        "evaluations": [
          {
            "question_number": 1,
            "max_marks": 10,
            "obtained_marks": 8,
            "feedback": "Good answer but missed one point"
          }
        ],
        "total_obtained": 42,
        "total_max": 50
      },
      "success": true
    }
  ]
}
```

---

## 📊 Download Excel Results

After getting results, download Excel:

```python
import requests

# First, get checking results
checking_results = {...}  # From previous API call

# Download Excel
response = requests.post(
    "http://localhost:8004/check-papers/download-excel",
    json={"checking_results": checking_results}
)

# Save Excel file
with open("grading_results.xlsx", "wb") as f:
    f.write(response.content)
```

---

## 🐛 Troubleshooting

### Error: "Could not extract text from answer key"
- **Solution**: Make sure answer key PDF is readable (not scanned image only)
- Try converting to text-based PDF

### Error: "No files found in Google Drive link"
- **Solution**: Make sure Google Drive folder is shared publicly or accessible
- Check the URL format

### Error: "openpyxl not installed"
- **Solution**: Already installed! ✅

### Student name shows "Unknown"
- **Normal**: If name/roll number can't be detected from first page
- The grading will still work, just without student info

---

## 📝 Test Checklist

- [ ] Server is running (http://localhost:8004/health)
- [ ] Answer key file ready
- [ ] Student paper(s) ready
- [ ] Test `/check-papers/upload` endpoint
- [ ] Check response has grading results
- [ ] Test `/check-papers/download-excel` endpoint
- [ ] Verify Excel file downloads correctly

---

## 🎉 Ready to Test!

Open Swagger UI: **http://localhost:8004/docs**

Find `POST /check-papers/upload` and click "Try it out"!

