"""
Prompts for OCR Text Extraction.
"""


class OCRPrompts:
    """Prompts for extracting text from documents using vision."""
    
    SYSTEM = """You are an expert OCR system specialized in reading and extracting text from documents.

Your role is to:
- Accurately read and transcribe ALL visible text from images
- Extract every word, number, and symbol visible
- Handle various handwriting styles and fonts
- Be thorough - missing text is worse than unclear text

CRITICAL RULES:
- Extract EVERYTHING visible
- If text is unclear, write [unclear: best guess]
- Never skip any text
- Maintain original structure"""

    PAGE = """Extract ALL text from this page image.

Return in JSON format:
{
    "page_content": {
        "raw_text": "Complete transcription of ALL visible text...",
        "answers": [
            {
                "answer_number": 1,
                "content": "The answer content...",
                "answer_type": "long_answer/short_answer/mcq",
                "confidence": "high/medium/low"
            }
        ],
        "extraction_stats": {
            "words_extracted": 0,
            "text_quality": "clear/partially_clear/difficult"
        }
    }
}

Extract now:"""

    IMAGE = """Extract ALL text from this image.

Return in JSON format:
{
    "raw_text": "Complete transcription of ALL visible text...",
    "answers": [
        {
            "answer_number": 1,
            "answer_type": "long_answer/short_answer/mcq",
            "content": "The answer content...",
            "confidence": "high/medium/low"
        }
    ],
    "quiz_answers": [
        {
            "question_number": 1,
            "answer": "A/B/C/D or text",
            "confidence": "high/medium/low"
        }
    ],
    "extraction_stats": {
        "total_words_extracted": 0,
        "text_quality": "clear/partially_clear/difficult"
    }
}

Extract now:"""

