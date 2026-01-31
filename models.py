from pydantic import BaseModel
from typing import List, Optional


class QuizConfig(BaseModel):
    mcq_count: int = 0
    fill_blanks_count: int = 0
    true_false_count: int = 0
    difficulty: str = "medium"  # easy, medium, hard


class AssignmentConfig(BaseModel):
    num_questions: int = 5
    difficulty: str = "medium"  # easy, medium, hard


class GenerationRequest(BaseModel):
    num_quizzes: int = 1
    num_assignments: int = 0
    quiz_config: Optional[QuizConfig] = None
    assignment_config: Optional[AssignmentConfig] = None


class QuizQuestion(BaseModel):
    question_number: int
    question_text: str
    question_type: str
    marks: int
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    difficulty_level: str
    topic: Optional[str] = None


class AssignmentQuestion(BaseModel):
    question_number: int
    question_text: str
    question_type: str
    marks: int
    expected_length: Optional[str] = None
    key_points: Optional[List[str]] = None
    difficulty_level: str
    topic: Optional[str] = None


class Quiz(BaseModel):
    quiz_number: int
    questions: List[QuizQuestion]
    total_marks: int


class Assignment(BaseModel):
    assignment_number: int
    questions: List[AssignmentQuestion]
    total_marks: int


class GenerationResponse(BaseModel):
    success: bool
    message: str
    quizzes: List[Quiz] = []
    assignments: List[Assignment] = []
    total_quizzes: int = 0
    total_assignments: int = 0


# ============== REQUEST MODELS ==============

class DownloadRequest(BaseModel):
    """Request model for downloading quiz/assignment documents."""
    quizzes: List[dict] = []
    assignments: List[dict] = []


class OCRDownloadRequest(BaseModel):
    """Request model for downloading OCR results as Word documents."""
    files_data: List[dict]  # Each file's data with filename, answers, quiz_answers


# ============== OCR RESPONSE MODELS ==============

class ExtractedAnswer(BaseModel):
    """Model for a single extracted answer."""
    answer_number: str
    content: str
    answer_type: str = "unknown"
    confidence: str = "medium"
    pages: List[int] = []


class FileExtractionResult(BaseModel):
    """Model for extraction results from a single file."""
    filename: str
    pages_processed: int = 0
    raw_text: str = ""
    answers: List[dict] = []
    quiz_answers: List[dict] = []
    total_answers: int = 0
    extraction_stats: List[dict] = []
    success: bool = True
    error: Optional[str] = None


class OCRExtractionResponse(BaseModel):
    """Response model for OCR extraction."""
    success: bool
    files_data: List[FileExtractionResult] = []
    total_files: int = 0
    total_pages: int = 0
    total_answers: int = 0
    error: Optional[str] = None


# ============== CHECKING PAPERS MODELS ==============

class AnswerEvaluation(BaseModel):
    """Model for a single answer evaluation."""
    question_number: int
    max_marks: float
    obtained_marks: float
    feedback: Optional[str] = None
    is_correct: Optional[bool] = None  # For quiz type
    correct_answer: Optional[str] = None
    student_answer: Optional[str] = None


class StudentGradingResult(BaseModel):
    """Model for a single student's grading result."""
    filename: str
    student_name: str = "Unknown"
    roll_number: str = "Unknown"
    answers_extracted: int = 0
    total_obtained: float = 0
    total_max: float = 0
    evaluations: List[AnswerEvaluation] = []
    overall_feedback: Optional[str] = None
    success: bool = True
    error: Optional[str] = None


class CheckingPapersResponse(BaseModel):
    """Response model for paper checking."""
    success: bool
    assessment_type: str = "assignment"  # "quiz" or "assignment"
    total_students: int = 0
    successful: int = 0
    failed: int = 0
    answer_key_info: dict = {}
    results: List[dict] = []
    error: Optional[str] = None


class CheckPapersRequest(BaseModel):
    """Request model for checking papers from Google Drive."""
    answer_key_text: str  # Raw text of answer key
    drive_url: str  # Google Drive URL with student papers


class ExcelDownloadRequest(BaseModel):
    """Request model for downloading grading results as Excel."""
    checking_results: dict  # Full checking results from /check-papers endpoint
