"""
Prompts for Quiz and Assignment Generation.
"""


class GenerationPrompts:
    """Prompts for generating quizzes and assignments."""
    
    SYSTEM = """You are an expert educational content creator specializing in quiz and assignment generation. 

Your role is to:
- Analyze educational content and create high-quality assessment questions
- Generate questions that test comprehension, application, and critical thinking
- Ensure questions are clear, unambiguous, and pedagogically sound
- Create diverse question types appropriate for the content
- Match the specified difficulty level exactly"""

    QUIZ = """Generate exactly {total_questions} {difficulty} level quiz questions from the content below.

CONTENT:
{content}

REQUIREMENTS:
- {question_types}
- All questions must be {difficulty} difficulty

Return as JSON array:
[
    {{
        "question_number": 1,
        "question_text": "...",
        "question_type": "mcq/fill_blank/true_false",
        "marks": 1,
        "options": ["A", "B", "C", "D"],
        "correct_answer": "...",
        "explanation": "...",
        "difficulty_level": "{difficulty}",
        "topic": "..."
    }}
]"""

    ASSIGNMENT = """Generate {num_questions} {difficulty} level assignment questions from the content below.

CONTENT:
{content}

REQUIREMENTS:
- All questions must be {difficulty} difficulty
- Questions should be descriptive/analytical (long answer type)

Return as JSON array:
[
    {{
        "question_number": 1,
        "question_text": "...",
        "question_type": "long_answer",
        "marks": 10,
        "expected_length": "300-500 words",
        "key_points": ["point1", "point2"],
        "difficulty_level": "{difficulty}",
        "topic": "..."
    }}
]"""

