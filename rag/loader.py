"""
Document loader and chunking utilities for RAG ingestion.
"""

from __future__ import annotations

from pathlib import Path
import docx
import pypdf

from utils.logger import logger


class DocumentLoader:
    """
    Parses PDF and DOCX files and extracts overlapping text chunks.
    """

    def __init__(
        self,
        chunk_size: int = 300,
        chunk_overlap: int = 50,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_text_from_pdf(self, file_path: str | Path) -> str:
        """
        Extract raw text from a PDF file using pypdf.
        """
        text_content = []
        try:
            reader = pypdf.PdfReader(str(file_path))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content.append(extracted)
            return "\n".join(text_content)
        except Exception as error:
            logger.exception("Failed to parse PDF file %s: %s", file_path, error)
            raise

    def load_text_from_docx(self, file_path: str | Path) -> str:
        """
        Extract raw text from a DOCX file using python-docx.
        """
        try:
            doc = docx.Document(str(file_path))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n".join(paragraphs)
        except Exception as error:
            logger.exception("Failed to parse DOCX file %s: %s", file_path, error)
            raise

    def load_document_text(self, file_path: str | Path) -> str:
        """
        Load raw text based on file extension.
        """
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == ".pdf":
            return self.load_text_from_pdf(path)
        elif ext in [".docx", ".doc"]:
            return self.load_text_from_docx(path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def chunk_text(self, text: str) -> list[str]:
        """
        Split raw text into sliding window word chunks with configured overlap.
        """
        cleaned_text = text.strip()
        if not cleaned_text:
            return []

        words = cleaned_text.split()
        if not words:
            return []

        chunks = []
        step = max(1, self.chunk_size - self.chunk_overlap)

        for i in range(0, len(words), step):
            chunk_words = words[i : i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            if chunk_text:
                chunks.append(chunk_text)

        return chunks