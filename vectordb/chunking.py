"""
Document chunking for PDFs and Word documents using LangChain.

This file handles:
- Loading PDF and Word documents
- Splitting documents into chunks using RecursiveCharacterTextSplitter
- Returning chunks ready for embedding
"""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_core.documents import Document
from config.config import Config
import os



class DocumentChunker:
    """
    Class for loading and chunking documents (PDFs and Word docs).
    """
    
    def __init__(
        self, 
        chunk_size: int = None, 
        chunk_overlap: int = None
    ):
        """
        Initialize the document chunker with specified chunk size and overlap.
        
        Args:
            chunk_size: Size of each chunk (default from Config)
            chunk_overlap: Overlap between chunks (default from Config)
        """
        self.chunk_size = chunk_size or Config.DEFAULT_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Config.DEFAULT_CHUNK_OVERLAP
        
        # Initialize the text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_document(self, file_path: str) -> List[Document]:
        """
        Load a document based on its file extension.
        
        Args:
            file_path: Path to the document file
        
        Returns:
            List of LangChain Document objects
        
        Raises:
            ValueError: If file type is not supported
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            loader = PyPDFLoader(file_path)
        elif file_extension in ['.docx', '.doc']:
            loader = Docx2txtLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        documents = loader.load()
        return documents
    
    def chunk_document(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.
        
        Args:
            documents: List of LangChain Document objects
        
        Returns:
            List of chunked Document objects
        """
        chunks = self.text_splitter.split_documents(documents)
        return chunks
    
    def process_file(self, file_path: str) -> List[Document]:
        """
        Load and chunk a document file in one step.
        
        Args:
            file_path: Path to the document file
        
        Returns:
            List of chunked Document objects with metadata
        """
        # Load the document
        documents = self.load_document(file_path)
        
        # Add source metadata
        for doc in documents:
            doc.metadata['source'] = file_path
            doc.metadata['filename'] = os.path.basename(file_path)
        
        # Chunk the documents
        chunks = self.chunk_document(documents)
        
        # Add chunk index to metadata
        for idx, chunk in enumerate(chunks):
            chunk.metadata['chunk_index'] = idx
            chunk.metadata['total_chunks'] = len(chunks)
        
        return chunks
    
    def process_multiple_files(self, file_paths: List[str]) -> List[Document]:
        """
        Process multiple files and return all chunks.
        
        Args:
            file_paths: List of paths to document files
        
        Returns:
            List of all chunked Document objects from all files
        """
        all_chunks = []
        
        for file_path in file_paths:
            try:
                chunks = self.process_file(file_path)
                all_chunks.extend(chunks)
                print(f"✓ Processed {file_path}: {len(chunks)} chunks")
            except Exception as e:
                print(f"✗ Error processing {file_path}: {str(e)}")
        
        return all_chunks
    
    def get_chunk_texts(self, chunks: List[Document]) -> List[str]:
        """
        Extract just the text content from chunks.
        
        Args:
            chunks: List of Document objects
        
        Returns:
            List of text strings
        """
        return [chunk.page_content for chunk in chunks]
    
    def get_chunk_metadata(self, chunks: List[Document]) -> List[dict]:
        """
        Extract metadata from chunks.
        
        Args:
            chunks: List of Document objects
        
        Returns:
            List of metadata dictionaries
        """
        return [chunk.metadata for chunk in chunks]


# Convenience function for quick usage
def chunk_documents(
    file_paths: List[str], 
    chunk_size: int = None, 
    chunk_overlap: int = None
) -> List[Document]:
    """
    Convenience function to chunk one or more documents.
    
    Args:
        file_paths: Path(s) to document file(s)
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
    
    Returns:
        List of chunked Document objects
    """
    chunker = DocumentChunker(chunk_size, chunk_overlap)
    
    if isinstance(file_paths, str):
        file_paths = [file_paths]
    
    return chunker.process_multiple_files(file_paths)

