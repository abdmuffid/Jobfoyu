# app/job_recommender.py
import os
from typing import List, Dict, Optional

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class JobRecommender:
    """
    Content-based recommender system untuk job IT di Indonesia
    menggunakan TF-IDF + cosine similarity.

    - Membaca indonesia_it_jobs.csv
    - Menghapus duplikat job (berdasarkan kombinasi title, company, location, job_url)
    - Membangun TF-IDF matrix dari title + description + skills
    """

    def __init__(self) -> None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "data", "indonesia_it_jobs.csv")

        print(f"[INFO] Loading job dataset from {data_path}")
        df = pd.read_csv(data_path)

        # Kolom yang wajib ada
        required_cols = [
            "title",
            "company",
            "location",
            "description",
            "skills",
            "is_remote",
            "job_url",
        ]
        for col in required_cols:
            if col not in df.columns:
                raise RuntimeError(
                    f"Column '{col}' not found in CSV. Pastikan struktur indonesia_it_jobs.csv sesuai."
                )

        # Isi NaN dengan string kosong
        df = df.fillna("")

        # 🔴 HAPUS DUPLIKAT JOB (identitas unik = title + company + location + job_url)
        df["job_identity"] = (
            df["title"].astype(str).str.strip().str.lower()
            + " | "
            + df["company"].astype(str).str.strip().str.lower()
            + " | "
            + df["location"].astype(str).str.strip().str.lower()
            + " | "
            + df["job_url"].astype(str).str.strip().str.lower()
        )

        before = df.shape[0]
        df = df.drop_duplicates(subset=["job_identity"], keep="first").reset_index(drop=True)
        after = df.shape[0]
        print(f"[INFO] Removed {before - after} duplicate jobs. Remaining: {after}")

        self.df = df

        # Gabungkan teks untuk TF-IDF
        self.df["combined_text"] = (
            self.df["title"].astype(str)
            + " "
            + self.df["description"].astype(str)
            + " "
            + self.df["skills"].astype(str)
        )

        # Inisialisasi dan fit TF-IDF
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            max_features=50000,
            stop_words="english",
        )

        print("[INFO] Fitting TF-IDF vectorizer...")
        self.job_matrix = self.vectorizer.fit_transform(self.df["combined_text"])
        print("[INFO] TF-IDF ready. Total jobs:", self.df.shape[0])

    def recommend(
        self,
        cv_text: str,
        top_n: int = 10,
        location_filter: Optional[str] = None,
        remote_only: bool = False,
        min_score: float = 0.02,
    ) -> List[Dict]:
        """
        Hitung similarity antara CV kamu dan semua job.
        Mengembalikan list job paling relevan, dengan match_percentage (0–100%).

        match_score = cosine similarity (0–1) → dikali 100 jadi persen.
        """
        if not cv_text or len(cv_text.strip()) == 0:
            return []

        # 1. Vectorisasi CV
        cv_vec = self.vectorizer.transform([cv_text])

        # 2. Cosine similarity dengan semua job
        similarities = cosine_similarity(cv_vec, self.job_matrix)[0]  # shape: (n_jobs,)

        # 3. Masukkan similarity ke DataFrame supaya mudah difilter
        df_scores = self.df.copy()
        df_scores["similarity"] = similarities

        # 4. Filter lokasi (kalau ada)
        if location_filter:
            mask_loc = df_scores["location"].str.lower().str.contains(location_filter.lower())
            df_scores = df_scores[mask_loc]

        # 5. Filter remote-only (kalau diminta)
        if remote_only:
            df_scores = df_scores[df_scores["is_remote"].astype(bool)]

        # 6. Sort berdasarkan similarity, descending
        df_scores = df_scores.sort_values(by="similarity", ascending=False)

        # 7. Jaga-jaga kalau masih ada duplikat lagi (misal setelah filter lokasi)
        df_scores = df_scores.drop_duplicates(
            subset=["title", "company", "location", "job_url"],
            keep="first",
        )

        # 8. Terapkan threshold minimal
        df_above = df_scores[df_scores["similarity"] >= min_score]

        if df_above.empty:
            print("[INFO] Tidak ada job di atas threshold, pakai top-N tanpa threshold.")
            df_selected = df_scores.head(top_n)
        else:
            df_selected = df_above.head(top_n)

        # 9. Bentuk hasil akhir (dengan match_percentage)
        results: List[Dict] = []
        for _, row in df_selected.iterrows():
            score = float(row["similarity"])
            results.append(
                {
                    "title": str(row["title"]),
                    "company": str(row["company"]),
                    "location": str(row["location"]),
                    "job_url": str(row["job_url"]),
                    "is_remote": bool(row["is_remote"]),
                    "match_percentage": round(score * 100, 1),
                    # penting: ini dipakai buat analisis gap dari job matcher
                    "description": str(row["description"]),
                }
            )

        return results


# Singleton
recommender = JobRecommender()
