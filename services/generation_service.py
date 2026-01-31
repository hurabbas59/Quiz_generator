"""
Generation Service - Quiz and Assignment generation with parallel processing.
"""
from typing import List, Dict
import json
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import UploadFile

from llm_models.llm_models import llm
from vectordb.vector_ops import PineconeVectorDB
from vectordb.chunking import DocumentChunker
from prompts.generation_prompts import GenerationPrompts
from models import QuizConfig, AssignmentConfig, Quiz, Assignment, QuizQuestion, AssignmentQuestion
from utils.logger import log_step, log_success, log_error, log_debug


class GenerationService:
    """Service for generating quizzes and assignments with parallel processing."""
    
    def __init__(self, index_name: str = None):
        self.index_name = index_name or PineconeVectorDB.generate_unique_index_name()
        self.vector_db = None
        self.chunker = DocumentChunker()
        self.llm = llm
        self.namespace = "docs"
        log_step("GenerationService initialized", f"Index: {self.index_name}")
    
    async def process_uploaded_files(self, files: List[UploadFile]) -> int:
        """Process and chunk uploaded files."""
        log_step("Processing uploaded files", f"Files: {[f.filename for f in files]}")
        file_paths = []
        
        for file in files:
            suffix = os.path.splitext(file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await file.read()
                tmp.write(content)
                file_paths.append(tmp.name)
        
        log_step("Chunking documents", f"Processing {len(file_paths)} files")
        chunks = self.chunker.process_multiple_files(file_paths)
        
        if not chunks:
            log_error("No content extracted from documents")
            raise ValueError("No content extracted from documents")
        
        log_success(f"Created {len(chunks)} chunks")
        
        # Create vector DB
        log_step("Creating vector database", f"Index: {self.index_name}")
        self.vector_db = PineconeVectorDB(index_name=self.index_name)
        self.vector_db.add_documents(chunks, namespace=self.namespace)
        log_success(f"Added {len(chunks)} chunks to Pinecone")
        
        # Cleanup temp files
        for path in file_paths:
            os.unlink(path)
        
        return len(chunks)
    
    def _get_content(self, query: str = None, k: int = 10) -> str:
        """Retrieve content from vector DB."""
        search_query = "Generate Questions Covering these topics: " + query or "Generate questions covering all topics"
        log_debug(f"Retrieving content with query: {search_query}")
        
        docs = self.vector_db.similarity_search(
            query=search_query,
            k=k,
            namespace=self.namespace
        )
        return "\n\n".join([doc.page_content for doc in docs])
    
    def _parse_json(self, response: str) -> List[Dict]:
        """Parse JSON from LLM response."""
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        return json.loads(response.strip())
    
    def generate_quiz(self, config: QuizConfig, quiz_number: int) -> Quiz:
        """Generate a single quiz."""
        difficulty = getattr(config, 'difficulty', 'medium')
        topic_prompt = getattr(config, 'topic_prompt', None)
        log_step(f"Generating Quiz {quiz_number}", f"Difficulty: {difficulty}, Topic: {topic_prompt or 'All'}")
        
        total_questions = config.mcq_count + config.fill_blanks_count + config.true_false_count
        if total_questions == 0:
            total_questions = 10
            config.mcq_count, config.fill_blanks_count, config.true_false_count = 5, 3, 2
        
        content = self._get_content(query=topic_prompt, k=total_questions * 2)
        
        # Build question types string
        question_types = []
        if config.mcq_count > 0:
            question_types.append(f"{config.mcq_count} MCQ")
        if config.fill_blanks_count > 0:
            question_types.append(f"{config.fill_blanks_count} Fill in the blanks")
        if config.true_false_count > 0:
            question_types.append(f"{config.true_false_count} True/False")
        
        prompt = GenerationPrompts.QUIZ.format(
            total_questions=total_questions,
            difficulty=difficulty.upper(),
            content=content,
            question_types=', '.join(question_types)
        )
        
        messages = [
            {"role": "system", "content": GenerationPrompts.SYSTEM},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm.invoke(messages)
        questions_data = self._parse_json(response.content)
        
        questions = [QuizQuestion(**q) for q in questions_data]
        total_marks = sum(q.marks for q in questions)
        
        log_success(f"Quiz {quiz_number}: {len(questions)} questions, {total_marks} marks")
        return Quiz(quiz_number=quiz_number, questions=questions, total_marks=total_marks)
    
    def generate_assignment(self, config: AssignmentConfig, assignment_number: int) -> Assignment:
        """Generate a single assignment."""
        difficulty = config.difficulty
        topic_prompt = getattr(config, 'topic_prompt', None)
        log_step(f"Generating Assignment {assignment_number}", f"Difficulty: {difficulty}, Topic: {topic_prompt or 'All'}")
        
        content = self._get_content(query=topic_prompt, k=config.num_questions * 3)
        
        prompt = GenerationPrompts.ASSIGNMENT.format(
            num_questions=config.num_questions,
            difficulty=difficulty.upper(),
            content=content
        )
        
        messages = [
            {"role": "system", "content": GenerationPrompts.SYSTEM},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm.invoke(messages)
        questions_data = self._parse_json(response.content)
        
        questions = [AssignmentQuestion(**q) for q in questions_data]
        total_marks = sum(q.marks for q in questions)
        
        log_success(f"Assignment {assignment_number}: {len(questions)} questions, {total_marks} marks")
        return Assignment(assignment_number=assignment_number, questions=questions, total_marks=total_marks)
    
    def generate_all(
        self,
        num_quizzes: int,
        num_assignments: int,
        quiz_config: QuizConfig,
        assignment_config: AssignmentConfig,
        delete_after: bool = True
    ) -> Dict:
        """Generate all quizzes and assignments with parallel processing."""
        log_step("Generate All (Parallel)", f"Quizzes: {num_quizzes}, Assignments: {num_assignments}")
        
        quizzes = []
        assignments = []
        
        # Use parallel processing for faster generation
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks
            quiz_futures = {
                executor.submit(self.generate_quiz, quiz_config, i + 1): i + 1
                for i in range(num_quizzes)
            }
            assignment_futures = {
                executor.submit(self.generate_assignment, assignment_config, i + 1): i + 1
                for i in range(num_assignments)
            }
            
            # Collect quiz results
            quiz_results = {}
            for future in as_completed(quiz_futures):
                quiz_num = quiz_futures[future]
                try:
                    quiz_results[quiz_num] = future.result()
                except Exception as e:
                    log_error(f"Quiz {quiz_num} failed", e)
            
            # Collect assignment results
            assignment_results = {}
            for future in as_completed(assignment_futures):
                assign_num = assignment_futures[future]
                try:
                    assignment_results[assign_num] = future.result()
                except Exception as e:
                    log_error(f"Assignment {assign_num} failed", e)
        
        # Sort by number
        quizzes = [quiz_results[i] for i in sorted(quiz_results.keys())]
        assignments = [assignment_results[i] for i in sorted(assignment_results.keys())]
        
        # Cleanup
        if delete_after and self.vector_db:
            log_step("Cleanup", f"Deleting index: {self.index_name}")
            self.vector_db.delete_index()
            log_success(f"Index deleted")
        
        log_success(f"Complete: {len(quizzes)} quizzes, {len(assignments)} assignments")
        
        return {
            "quizzes": quizzes,
            "assignments": assignments,
            "index_name": self.index_name,
            "index_deleted": delete_after
        }
