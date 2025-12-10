"""
Configuration management for the application.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Central configuration class for the application.
    """
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Pinecone Configuration
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "quiz-generator")
    
    # Application Settings
    MAX_QUIZ_COUNT = int(os.getenv("MAX_QUIZ_COUNT", 10))
    DEFAULT_CHUNK_SIZE = int(os.getenv("DEFAULT_CHUNK_SIZE", 800))
    DEFAULT_CHUNK_OVERLAP = int(os.getenv("DEFAULT_CHUNK_OVERLAP", 100))
    
    # File Upload Settings
    UPLOAD_FOLDER = "uploads"
    TEMP_FOLDER = "temp"
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
    
    @classmethod
    def validate(cls):
        """
        Validate that all required configuration is present.
        """
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required in .env file")
        
        if not cls.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY is required in .env file")
        
        # Create necessary directories
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(cls.TEMP_FOLDER, exist_ok=True)


# Validate configuration on import
Config.validate()
