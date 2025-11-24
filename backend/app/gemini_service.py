# app/gemini_service.py
from google import genai
from app.config import settings


def _get_client() -> genai.Client:
    """
    Membuat client Gemini SDK baru.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY belum diset. Tambahkan ke file .env di folder backend.")

    client = genai.Client(api_key=api_key)
    return client


def analyze_cv_gap(cv_text: str, job_description: str) -> str:
    try:
        client = _get_client()
    except RuntimeError as e:
        return f"Error konfigurasi Gemini: {e}"

    prompt = f"""
Konteks:
Kamu berperan sebagai career coach profesional yang empatik, realistis, dan memahami industri teknologi di Indonesia.
Tugasmu adalah menganalisis kecocokan antara **CV kandidat** dan **Job Description** secara mendalam.

Gaya komunikasi:
- santai, hangat, dan menggunakan kata "kamu",
- tidak menggurui, tapi tetap jujur,
- tidak membual atau memberi pujian berlebihan,
- fokus pada insight yang berguna dan actionable,
- hindari angka atau skor evaluasi.

Model berpikir:
- jelaskan kekuatan kandidat secara spesifik (berbasis bukti yang muncul di CV),
- jelaskan gap secara objektif, tanpa menakut-nakuti,
- arahkan kandidat supaya tahu apa yang bisa ia lakukan setelah membaca feedback.

Tujuan akhir:
Kandidat bisa memahami — tanpa merasa kecil hati — apakah ia sudah cocok untuk posisi ini, bagian mana yang kuat, apa yang kurang, dan apa langkah paling realistis untuk meningkatkan peluang diterima.

CV KANDIDAT:
----------------
{cv_text[:6000]}

JOB DESCRIPTION:
----------------
{job_description[:3000]}

Tolong berikan jawaban dalam format **Markdown** dengan struktur berikut:

### 1. Gambaran umum kecocokan kamu
- Jelaskan seberapa relevan CV kamu dengan posisi ini secara jujur tapi menenangkan.
- Jangan memakai skor angka.

### 2. Bagian CV kamu yang sudah kuat
- Sebutkan poin-poin kekuatan yang benar-benar muncul dari CV.
- Hubungkan kekuatan itu dengan kebutuhan di JD.

### 3. Area yang perlu kamu tingkatkan
- Sebutkan gap yang paling signifikan.
- Fokus pada skill teknis, tools, sertifikasi, pengalaman project, atau soft skill.
- Hindari kalimat yang merendahkan.

### 4. Rekomendasi perbaikan yang bisa kamu lakukan
- Berikan panduan yang benar-benar bisa dieksekusi (realistic & specific).
- Contoh yang diperbolehkan: jenis proyek portfolio yang bisa dibuat, skill yang layak dipelajari duluan, atau cara meng-highlight pengalaman di CV.

### 5. Contoh "Professional Summary" yang bisa kamu pasang di CV
- Buat 2–3 kalimat dalam bahasa Indonesia atau bahasa inggris sesuai cv yang diunggah user,
- sesuai dengan gaya industri,
- mencerminkan kelebihan kandidat dan posisi di JD.

Catatan akhir:
- Tidak perlu memotivasi secara berlebihan.
- Cukup akhiri dengan nada optimis dan realistis.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Terjadi error saat menghubungi AI: {e}"
