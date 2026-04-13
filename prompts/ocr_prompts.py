"""
Prompts for OCR Text Extraction — aligned with structured exam answer patterns.
"""


class OCRPrompts:
    """Prompts for extracting text from documents using vision."""

    SYSTEM = """You are an expert OCR system specialized in reading student exam papers and worksheets.

Your role is to:
- Accurately read and transcribe ALL visible text from images
- Map responses to questions and sections when those labels appear on the page
- Classify each student response by answer type
- Be thorough — missing text is worse than unclear text

CRITICAL RULES:
- Extract EVERYTHING visible
- If text is unclear, write [unclear: best guess]
- Never skip any text
- Preserve question identifiers exactly as printed (e.g. Q1, 1(a), Sec-B-Q3)
- Use one entry per question in "answers" (split sub-parts if clearly separate questions)"""

    PAGE = """Extract ALL text from this exam / worksheet page image.

Return JSON:
{
    "page_content": {
        "raw_text": "Complete transcription of ALL visible text...",
        "answers": [
            {
                "question_id": "Q1 or 2(b) — identifier as on paper",
                "section_id": "A / B / Part-I — if shown, else null",
                "section_title": "Section heading if visible, else null",
                "student_answer": "The student's response text",
                "answer_type": "descriptive|short_answer|fill_blank|mcq|true_false|unknown",
                "confidence": "high|medium|low"
            }
        ],
        "quiz_answers": [
            {
                "question_id": "1",
                "student_answer": "A / B / True / exact bubble text",
                "answer_type": "mcq|true_false",
                "confidence": "high|medium|low"
            }
        ],
        "extraction_stats": {
            "words_extracted": 0,
            "text_quality": "clear|partially_clear|difficult"
        }
    }
}

Guidance:
- descriptive: paragraph-style / essay
- short_answer: a few words or one sentence
- fill_blank: blanks filled in situ; put the completed phrase or blank values in student_answer
- mcq / true_false: also list in quiz_answers when the item is clearly objective
- If the same question continues on the next line, merge into one answers[] entry

Extract now:"""

    IMAGE = """Extract ALL text from this exam / worksheet image.

Return JSON:
{
    "raw_text": "Complete transcription of ALL visible text...",
    "answers": [
        {
            "question_id": "string",
            "section_id": "string or null",
            "section_title": "string or null",
            "student_answer": "string",
            "answer_type": "descriptive|short_answer|fill_blank|mcq|true_false|unknown",
            "confidence": "high|medium|low"
        }
    ],
    "quiz_answers": [
        {
            "question_id": "string",
            "student_answer": "string",
            "answer_type": "mcq|true_false",
            "confidence": "high|medium|low"
        }
    ],
    "extraction_stats": {
        "total_words_extracted": 0,
        "text_quality": "clear|partially_clear|difficult"
    }
}

Extract now:"""
