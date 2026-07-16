from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile

from docx import Document as DocxDocument
from docx.opc.exceptions import PackageNotFoundError
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.core.errors import AppError, document_content_not_extractable


def extract_text(filename: str, content: bytes) -> str:
    """Extract indexable text from one V0.2-supported document format."""
    try:
        file_type = Path(filename).suffix.lower()
        if file_type in {".txt", ".md"}:
            text = content.decode("utf-8-sig")
        elif file_type == ".docx":
            text = "\n".join(
                paragraph.text
                for paragraph in DocxDocument(BytesIO(content)).paragraphs
            )
        elif file_type == ".pdf":
            text = "\n".join(
                page.extract_text() or "" for page in PdfReader(BytesIO(content)).pages
            )
        else:
            raise document_content_not_extractable()
    except AppError:
        raise
    except (
        BadZipFile,
        OSError,
        PackageNotFoundError,
        PdfReadError,
        UnicodeDecodeError,
        ValueError,
    ):
        raise document_content_not_extractable() from None

    if not text.strip():
        raise document_content_not_extractable()
    return text
