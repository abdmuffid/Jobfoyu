# app/gemini_service.py
import google.generativeai as genai
from app.config import settings


def configure_gemini():
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set. Please configure it in .env")

    genai.configure(api_key=settings.GEMINI_API_KEY)


def analyze_cv_gap(cv_text: str, job_desc: str) -> str:
    """
    Analisis gap antara CV dan Job Description menggunakan Gemini.
    Output: Markdown (biar gampang dirender di frontend).
    """
    configure_gemini()
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
Konteks:
Kamu berperan sebagai career coach profesional yang empatik, realistis, dan memahami industri teknologi di Indonesia.
Tugasmu adalah menganalisis kecocokan antara **CV kandidat** dan **Job Description** secara mendalam.

Gaya komunikasi:
- santai, hangat, pakai kata "kamu",
- jujur tapi tidak menusuk,
- tidak memberikan pujian berlebihan,
- fokus pada insight yang actionable dan relevan,
- hindari angka dalam penilaian.

Model berpikir:
- jelaskan kekuatan kandidat dengan merujuk bukti nyata dari CV,
- jelaskan gap secara objektif,
- berikan arahan jelas agar kandidat tahu apa yang bisa ditingkatkan.

INPUT:
----------------
CV KANDIDAT:
----------------
{cv_text[:6000]}

JOB DESCRIPTION:
----------------
{job_desc[:3000]}

OUTPUT (Gunakan format Markdown):

### 1. Gambaran umum kecocokan kamu
- Ringkas tingkat cocoknya secara jujur dan menenangkan.

### 2. Bagian CV kamu yang sudah kuat
- Jelaskan kekuatan dengan spesifik + relevansinya dengan JD.

### 3. Area yang perlu kamu tingkatkan
- Sebutkan gap tanpa mengecilkan kandidat.
- Fokus pada skill, pengalaman, tools, soft skill, atau portfolio.

### 4. Rekomendasi perbaikan yang bisa kamu lakukan
- Berikan langkah-langkah riil dan bisa dieksekusi.
- Misal: proyek portfolio, skill prioritas, cara menulis ulang poin CV.

### 5. Contoh Professional Summary yang bisa kamu pasang di CV
- 2–3 kalimat tajam dan profesional.
- Sesuaikan dengan role pada JD.
- Langsung siap dipakai.

Akhiri dengan tone optimis namun realistis.
"""

    try:
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"Terjadi error saat menghubungi AI: {e}"
