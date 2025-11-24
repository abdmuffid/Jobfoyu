# app/main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.cv_parser import extract_text_from_pdf
from app.job_recommender import recommender
from app.gemini_service import analyze_cv_gap

app = FastAPI(title="Job Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://jobfoyu.vercel.app"],  # di production sebaiknya spesifik domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/match-jobs")
async def match_jobs(
    file: UploadFile = File(..., description="CV dalam format PDF"),
    top_n: int = Form(10),
    location_filter: str | None = Form(None),
    remote_only: bool = Form(False),
):
    """
    Halaman 1: Job Matcher
    - Upload CV (PDF)
    - Cocokkan dengan dataset job
    - Return list job dengan match_percentage + description
    """
    filename = file.filename.lower()
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Hanya file PDF yang didukung untuk saat ini.")

    file_bytes = await file.read()
    cv_text = extract_text_from_pdf(file_bytes)

    if not cv_text or len(cv_text) < 50:
        raise HTTPException(
            status_code=400,
            detail="Teks CV terlalu pendek atau gagal diekstrak. Pastikan PDF dapat di-copy text-nya."
        )

    results = recommender.recommend(
        cv_text=cv_text,
        top_n=top_n,
        location_filter=location_filter,
        remote_only=remote_only,
    )

    return {
        "status": "success",
        "total": len(results),
        "recommendations": results,
    }


@app.post("/analyze-gap")
async def analyze_gap(
    file: UploadFile = File(..., description="CV dalam format PDF"),
    job_desc: str = Form(..., description="Job description target"),
):
    """
    Dipakai oleh:
    - Halaman CV Improver
    - Tombol "Analisis Gap CV vs Job ini" di Job Matcher

    Flow:
    - Upload CV (PDF)
    - Kirim job_desc (bisa dari input user, bisa dari description job)
    - AI balas dengan analisis gap dalam Markdown, gaya ngobrol.
    """
    filename = file.filename.lower()
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Hanya file PDF yang didukung untuk saat ini.")

    file_bytes = await file.read()
    cv_text = extract_text_from_pdf(file_bytes)

    if not cv_text or len(cv_text) < 50:
        raise HTTPException(
            status_code=400,
            detail="Teks CV terlalu pendek atau gagal diekstrak. Pastikan PDF dapat di-copy text-nya."
        )

    if len(job_desc.strip()) < 30:
        raise HTTPException(
            status_code=400,
            detail="Job description terlalu pendek. Tambahkan detail tugas dan kualifikasi."
        )

    analysis_md = analyze_cv_gap(cv_text, job_desc)

    return {
        "status": "success",
        "markdown": analysis_md,
    }
