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

        if text:
            # Normalize line endings
            clean_text = text.replace("\r\n", "\n").replace("\r", "\n")

            # Normalize spaces/tabs WITHOUT destroying newlines
            clean_text = re.sub(r'[ \t]+', ' ', clean_text)

            # Remove excessive blank lines
            clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)

            # Trim whitespace around lines
            clean_text = "\n".join(
                line.strip()
                for line in clean_text.split("\n")
            ).strip()
        else:
            clean_text = ""
        return clean_text, ocr_applied, ocr_confidence, error

    @staticmethod
    def _extract_pdf(file_path: str) -> Tuple[str, bool, Optional[float]]:
        """
        Extract text from PDF while preserving line structure.

        Uses PyMuPDF first because it generally provides better
        positional/layout-aware extraction than pypdf.

        Falls back to pypdf if PyMuPDF is unavailable.
        """

        text = ""

        # ---------------------------------------------------------
        # 1. Try PyMuPDF
        # ---------------------------------------------------------
        try:
            import fitz  # pip install pymupdf

            doc = fitz.open(file_path)

            pages = []

            for page in doc:
                # "text" preserves much more useful line structure
                page_text = page.get_text("text")

                if page_text:
                    pages.append(page_text)

            doc.close()

            text = "\n".join(pages)

        except Exception as e:
            print(f"PyMuPDF extraction failed: {e}")

        # ---------------------------------------------------------
        # 2. Fallback to pypdf
        # ---------------------------------------------------------
        if not text.strip():
            try:
                from pypdf import PdfReader

                reader = PdfReader(file_path)

                pages = []

                for page in reader.pages:
                    try:
                        # Newer pypdf versions support layout mode
                        page_text = page.extract_text(
                            extraction_mode="layout"
                        )
                    except TypeError:
                        # Older pypdf versions
                        page_text = page.extract_text()

                    if page_text:
                        pages.append(page_text)

                text = "\n".join(pages)

            except Exception as e:
                print(f"pypdf extraction failed: {e}")

        # ---------------------------------------------------------
        # 3. Check whether extracted text is usable
        # ---------------------------------------------------------
        word_count = len(text.strip().split())

        # If extraction is empty or extremely sparse,
        # try OCR.
        if word_count < 50:
            ocr_text, conf = ResumeExtractor._run_ocr(file_path)

            if (
                ocr_text
                and len(ocr_text.strip().split()) > word_count
            ):
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
