"""
=============================================================================
CHECKING PAPERS PROMPTS
=============================================================================

This file contains all the prompts (instructions) we send to the AI (GPT)
for the paper checking service.

WHAT THIS FILE DOES:
- Contains text templates that tell the AI how to:
  1. Extract student name and roll number from papers
  2. Grade assignment answers (long answers)
  3. Grade quiz answers (MCQ, True/False, Fill in blanks)
  4. Parse/read the answer key document

WHY WE NEED THIS:
- The AI needs clear instructions to do its job properly
- These prompts tell the AI exactly what format to return data in (JSON)
- They also tell the AI HOW to grade (semantically, not word-by-word)
=============================================================================
"""


class CheckingPapersPrompts:
    """
    A class that holds all the prompt templates for paper checking.
    
    Think of prompts as "instructions" we give to the AI.
    Each prompt tells the AI what task to do and how to do it.
    """
    
    # =========================================================================
    # SYSTEM PROMPT - This is the "personality" of the AI grader
    # =========================================================================
    # This prompt is sent with EVERY request to set up how the AI should behave
    
    SYSTEM = """You are an expert academic evaluator specialized in grading student answers.

Your role is to:
- Extract student information (name, roll number) from documents
- Compare student answers against answer keys semantically
- Grade based on understanding and meaning, NOT word-for-word matching
- Be fair and consistent in scoring
- Provide brief feedback for each answer

CRITICAL RULES:
- Focus on semantic correctness - the meaning matters, not exact wording
- Partial marks are allowed based on understanding demonstrated
- Be lenient with minor spelling/grammar if concept is correct
- Award full marks if the core concept is correctly explained"""

    # =========================================================================
    # EXTRACT STUDENT INFO PROMPT
    # =========================================================================
    # Used with GPT Vision to read the first page of student paper
    # and find their name and roll number (even if handwritten)
    
    EXTRACT_STUDENT_INFO = """Extract student information from this document image.

Look for:
- Student Name (may be handwritten or typed)
- Roll Number / Student ID / Registration Number
- Any other identifying information

Return in JSON format:
{
    "student_name": "Name or 'Unknown' if not found",
    "roll_number": "Roll number or 'Unknown' if not found",
    "confidence": "high/medium/low",
    "additional_info": "Any other relevant info"
}

Extract now:"""

    # =========================================================================
    # GRADE ASSIGNMENT ANSWERS PROMPT
    # =========================================================================
    # Used for grading long/descriptive answers (assignments)
    # 
    # HOW IT WORKS:
    # - We give the AI the correct answers (answer key)
    # - We give the AI the student's answers
    # - AI compares them SEMANTICALLY (meaning-based, not exact word match)
    # - AI gives marks based on understanding shown
    # - AI can give partial marks if answer is partially correct
    #
    # PLACEHOLDERS (filled in by code via str.replace — safe if JSON contains { }):
    # - [[[ANSWER_KEY_JSON]]], [[[STUDENT_ANSWERS_JSON]]], [[[TOTAL_QUESTIONS]]]
    
    GRADE_ASSIGNMENT_ANSWERS = """Grade the following student answers against the answer key.

ANSWER KEY (Correct Answers):
[[[ANSWER_KEY_JSON]]]

STUDENT ANSWERS:
[[[STUDENT_ANSWERS_JSON]]]

TOTAL QUESTIONS: [[[TOTAL_QUESTIONS]]]
MARKS PER QUESTION: Use the marks specified in the answer key for each question.

GRADING INSTRUCTIONS:
1. Compare each student answer with the corresponding answer key SEMANTICALLY
2. Award marks based on understanding, not exact word matching
3. If a student explains the concept correctly in their own words, award full marks
4. Award partial marks if the answer is partially correct
5. Award 0 marks if the answer is completely wrong or missing

Return in JSON format:
{
    "evaluations": [
        {
            "question_number": 1,
            "max_marks": 10,
            "obtained_marks": 8,
            "feedback": "Brief feedback about the answer"
        }
    ],
    "total_obtained": 0,
    "total_max": 0,
    "overall_feedback": "General comment about performance"
}

Grade now:"""

    # =========================================================================
    # GRADE QUIZ ANSWERS PROMPT
    # =========================================================================
    # Used for grading quiz-type answers (MCQ, True/False, Fill in blanks)
    #
    # HOW IT WORKS:
    # - For MCQ: Check if selected option (A/B/C/D) matches correct answer
    # - For True/False: Check if answer matches
    # - For Fill in Blanks: Check meaning (synonyms are OK)
    # - Usually full marks or zero (no partial marks for MCQ/True-False)
    #
    # PLACEHOLDERS: [[[ANSWER_KEY_JSON]]], [[[STUDENT_ANSWERS_JSON]]]
    
    GRADE_QUIZ_ANSWERS = """Grade the following quiz answers against the answer key.

ANSWER KEY (Correct Answers):
[[[ANSWER_KEY_JSON]]]

STUDENT ANSWERS:
[[[STUDENT_ANSWERS_JSON]]]

GRADING INSTRUCTIONS:
1. For MCQ - check if selected option matches correct answer
2. For True/False - check if answer matches
3. For Fill in Blanks - check semantic correctness (synonyms are acceptable)
4. Award full marks for correct, 0 for incorrect

Return in JSON format:
{
    "evaluations": [
        {
            "question_number": 1,
            "question_type": "mcq/true_false/fill_blank",
            "max_marks": 1,
            "obtained_marks": 1,
            "correct_answer": "B",
            "student_answer": "B",
            "is_correct": true
        }
    ],
    "total_obtained": 0,
    "total_max": 0,
    "correct_count": 0,
    "total_questions": 0
}

Grade now:"""

    # =========================================================================
    # PARSE ANSWER KEY PROMPT
    # =========================================================================
    # Used to read and understand the answer key document
    #
    # WHAT IT DOES:
    # - Takes the raw text from answer key PDF
    # - Identifies each question and its correct answer
    # - Determines if it's a quiz or assignment
    # - Extracts marks for each question
    #
    # PLACEHOLDER (str.replace): [[[DOCUMENT_CONTENT]]]
    
    PARSE_ANSWER_KEY = """Parse this answer key document and extract all correct answers.

DOCUMENT CONTENT:
[[[DOCUMENT_CONTENT]]]

Extract all questions and their correct answers. Preserve identifiers as printed.
Set assessment_type:
- "quiz" if predominantly objective (MCQ / True-False / short blanks)
- "assignment" if predominantly descriptive / long answers
- "mixed" if there is a clear mix of objective and descriptive items

Return in JSON format:
{
    "assessment_type": "quiz/assignment/mixed",
    "total_marks": 0,
    "questions": [
        {
            "question_number": 1,
            "question_id": "Same label as on the paper if visible, else string of question_number",
            "section_id": "A/B/Part-II or null",
            "section_title": "Section heading if inferable, else null",
            "question_text": "The question text...",
            "correct_answer": "The correct answer or rubric anchor...",
            "marks": 2,
            "question_type": "mcq/true_false/fill_blank/short_answer/long_answer/descriptive",
            "options": ["A", "B", "C", "D"]
        }
    ]
}

Parse now:"""

    # =========================================================================
    # UNIFIED GRADING (objective + descriptive + blanks)
    # =========================================================================

    GRADE_UNIFIED = """You are grading student work against an answer key for a modern exam pattern.

ANSWER KEY (JSON array of questions with question_number, question_id, question_type, marks, correct_answer, section fields):
[[[ANSWER_KEY_JSON]]]

STUDENT RESPONSES (JSON array; each item has question_id and/or question_number, student_answer, answer_type, optional section fields):
[[[STUDENT_ANSWERS_JSON]]]

RULES — apply per question using its question_type from the ANSWER KEY:
1) Match student responses to key questions primarily by question_id when present, else by question_number. If a response cannot be matched, treat as missing (0 marks) and note this in feedback.
2) mcq / true_false: normalize case and whitespace; accept clear letter/word equivalents (e.g. "Option B", "b", "B."). Must match the keyed correct option; no partial marks unless the key explicitly allows multiple correct selections.
3) fill_blank: allow minor formatting differences; accept synonyms and equivalent numeric forms; multi-blank: award partial marks per blank proportionally to marks when obvious from the answer key.
4) short_answer: concise correctness — allow paraphrase; award partial marks for incomplete but directionally correct responses.
5) long_answer / descriptive: semantic match first; reward correct concepts and structure; award partial marks generously when partly right; consider clarity and explanation quality in borderline cases.
6) Avoid double-counting: if two student entries map to the same key question, use the best-supported combined response.
7) Keep feedback brief and actionable.

Return JSON ONLY:
{
    "evaluations": [
        {
            "question_number": 1,
            "question_id": "string or null",
            "question_type": "from key",
            "max_marks": 0,
            "obtained_marks": 0,
            "correct_answer": "string",
            "student_answer": "string",
            "is_correct": true,
            "feedback": "short rationale referencing matching rule"
        }
    ],
    "total_obtained": 0,
    "total_max": 0,
    "overall_feedback": "one short paragraph",
    "correct_count": 0,
    "total_questions": 0
}

Grade now:"""
