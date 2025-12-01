import os
from typing import List, Dict, Optional

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class JobRecommender:
    """
    Content-based recommender system untuk job IT di Indonesia
    menggunakan TF-IDF + cosine similarity.
    """

    def __init__(self) -> None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "data", "indonesia_it_jobs.csv")

        print(f"[INFO] Loading job dataset from {data_path}")
        self.df = pd.read_csv(data_path)

        # ---------------------------------------------------------------------
        # PERBAIKAN: Hapus Duplikat
        # Menghapus baris yang memiliki Title, Company, dan Location yang sama persis
        # agar tidak muncul double di hasil rekomendasi.
        # ---------------------------------------------------------------------
        initial_count = len(self.df)
        self.df.drop_duplicates(subset=["title", "company", "location"], keep="first", inplace=True)
        
        # Reset index sangat penting karena kita akan mengakses row pakai index nanti
        self.df.reset_index(drop=True, inplace=True)
        
        print(f"[INFO] Removed {initial_count - len(self.df)} duplicate jobs. Remaining: {len(self.df)}")
        # ---------------------------------------------------------------------

        # Pastikan kolom penting ada
        for col in ["title", "company", "location", "description", "skills", "is_remote", "job_url"]:
            if col not in self.df.columns:
                raise RuntimeError(f"Column '{col}' not found in CSV")

        # Isi NaN dengan string kosong
        self.df = self.df.fillna("")

        # Gabungkan deskripsi + skills jadi satu teks untuk TF-IDF
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
            stop_words=None  # bisa diganti 'english' kalau mau
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
        min_score: float = 0.05,
    ) -> List[Dict]:
        """
        Hitung similarity antara CV user dan semua job.
        Return list job paling cocok.

        match_score = cosine similarity (0–1) → dikali 100 jadi persen.
        """
        if not cv_text or len(cv_text.strip()) == 0:
            return []

        # Vectorisasi CV
        cv_vec = self.vectorizer.transform([cv_text])

        # Cosine similarity dengan semua job
        similarities = cosine_similarity(cv_vec, self.job_matrix)[0]  # shape: (n_jobs,)

        # Urutkan indeks job berdasarkan similarity desc
        sorted_idx = similarities.argsort()[::-1]

        results: List[Dict] = []

        for idx in sorted_idx:
            score = float(similarities[idx])
            if score < min_score:
                # karena sudah terurut desc, boleh break
                break

            row = self.df.iloc[idx]

            # Filter lokasi
            if location_filter:
                if location_filter.lower() not in str(row["location"]).lower():
                    continue

            # Filter remote-only
            if remote_only:
                # kolom is_remote di CSV: True/False
                if not bool(row["is_remote"]):
                    continue

            results.append(
                {
                    "title": str(row["title"]),
                    "company": str(row["company"]),
                    "location": str(row["location"]),
                    "job_url": str(row["job_url"]),
                    "is_remote": bool(row["is_remote"]),
                    "match_percentage": round(score * 100, 1),
                    "description": str(row["description"]), 
                }
            )

            if len(results) >= top_n:
                break

        return results


# Singleton untuk dipakai di seluruh app
recommender = JobRecommender()