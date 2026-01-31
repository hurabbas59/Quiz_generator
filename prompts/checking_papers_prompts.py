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
    # PLACEHOLDERS (filled in by code):
    # - {answer_key} = The correct answers from teacher
    # - {student_answers} = What the student wrote
    # - {total_questions} = How many questions there are
    
    GRADE_ASSIGNMENT_ANSWERS = """Grade the following student answers against the answer key.

ANSWER KEY (Correct Answers):
{answer_key}

STUDENT ANSWERS:
{student_answers}

TOTAL QUESTIONS: {total_questions}
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
    # PLACEHOLDERS:
    # - {answer_key} = Correct answers
    # - {student_answers} = Student's selected options
    
    GRADE_QUIZ_ANSWERS = """Grade the following quiz answers against the answer key.

ANSWER KEY (Correct Answers):
{answer_key}

STUDENT ANSWERS:
{student_answers}

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
    # PLACEHOLDER:
    # - {content} = Raw text extracted from answer key document
    
    PARSE_ANSWER_KEY = """Parse this answer key document and extract all correct answers.

DOCUMENT CONTENT:
{content}

Extract all questions and their correct answers. Identify the type of assessment:
- If mostly MCQ/True-False/Fill-blanks = "quiz"
- If mostly long/descriptive answers = "assignment"

Return in JSON format:
{
    "assessment_type": "quiz/assignment",
    "total_marks": 0,
    "questions": [
        {
            "question_number": 1,
            "question_text": "The question text...",
            "correct_answer": "The correct answer...",
            "marks": 2,
            "question_type": "mcq/true_false/fill_blank/short_answer/long_answer",
            "options": ["A", "B", "C", "D"]  // only for MCQ
        }
    ]
}

Parse now:"""
