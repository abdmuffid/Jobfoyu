# app/cv_parser.py
import io
import pdfplumber


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Ekstrak teks dari file PDF.
    Mengembalikan string teks (gabungan semua halaman).
    """
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[ERROR] Failed to parse PDF: {e}")
        return ""

    return text.strip()
