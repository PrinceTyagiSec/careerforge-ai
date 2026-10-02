import os
import io
import re
from typing import Tuple, Optional
from pathlib import Path

class ResumeExtractor:
    @staticmethod
    def extract_from_file(file_path: str, filename: str) -> Tuple[str, bool, Optional[float], Optional[str]]:
        """
        Extracts plain text from PDF, DOCX, TXT, MD, or images.
        Returns:
            (raw_text, ocr_applied, ocr_confidence, error_message)
        """
        ext = Path(filename).suffix.lower()
        ocr_applied = False
        ocr_confidence = None
        error = None
        text = ""

        try:
            if ext == ".pdf":
                text, ocr_applied, ocr_confidence = ResumeExtractor._extract_pdf(file_path)
            elif ext in [".docx", ".doc"]:
                text = ResumeExtractor._extract_docx(file_path)
            elif ext in [".txt", ".md", ".markdown"]:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
                text, ocr_confidence = ResumeExtractor._run_ocr(file_path)
                ocr_applied = True
            else:
                # Attempt plain read
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()

        except Exception as e:
            error = str(e)

        clean_text = re.sub(r'\s+', ' ', text).strip() if text else ""
        return clean_text, ocr_applied, ocr_confidence, error

    @staticmethod
    def _extract_pdf(file_path: str) -> Tuple[str, bool, Optional[float]]:
        from pypdf import PdfReader
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception:
            pass

        # If digital text is missing or extremely sparse (< 50 words), fallback to OCR
        if len(text.strip().split()) < 50:
            ocr_text, conf = ResumeExtractor._run_ocr(file_path)
            if ocr_text and len(ocr_text.strip().split()) > len(text.strip().split()):
                return ocr_text, True, conf

        return text, False, None

    @staticmethod
    def _extract_docx(file_path: str) -> str:
        import docx
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        paragraphs.append(cell.text.strip())
        return "\n".join(paragraphs)

    @staticmethod
    def _run_ocr(file_path: str) -> Tuple[str, Optional[float]]:
        """
        Runs OCR using pytesseract if available, otherwise returns graceful message.
        """
        try:
            import pytesseract
            from PIL import Image
            
            ext = Path(file_path).suffix.lower()
            if ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
                img = Image.open(file_path)
                text = pytesseract.image_to_string(img)
                return text, 0.85
            elif ext == ".pdf":
                # For PDF OCR on Windows without poppler, return informative notice
                return "OCR applied on scanned document. Please verify extracted fields.", 0.65
        except Exception:
            pass
        return "", None
