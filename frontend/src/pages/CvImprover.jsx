"use client"

import { useState } from "react"
import MarkdownViewer from "../components/MarkdownViewer.jsx"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE

const CvImprover = () => {
  const [file, setFile] = useState(null)
  const [jobDesc, setJobDesc] = useState("")
  const [loading, setLoading] = useState(false)
  const [markdown, setMarkdown] = useState("")
  const [error, setError] = useState("")

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setMarkdown("")

    if (!file) {
      setError("Silakan upload CV (PDF) terlebih dahulu.")
      return
    }
    if (jobDesc.trim().length < 30) {
      setError("Job description terlalu pendek. Tambahkan minimal 30 karakter.")
      return
    }

    const formData = new FormData()
    formData.append("file", file)
    formData.append("job_desc", jobDesc)

    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/analyze-gap`, {
        method: "POST",
        body: formData,
      })

      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || "Terjadi kesalahan")
      }

      setMarkdown(data.markdown || "")
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="page-section">
      <div className="section-header">
        <h2>CV Improver</h2>
        <p>Upload CV dan job description target. AI akan menganalisis gap dan memberi saran perbaikan.</p>
      </div>

      <form onSubmit={handleSubmit} className="form-card">
        <div className="form-group">
          <label>CV (PDF)</label>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files[0] || null)}
            className="file-input"
          />
          {file && <p className="file-name">{file.name}</p>}
        </div>

        <div className="form-group">
          <label>Job Description Target</label>
          <textarea
            rows={6}
            placeholder="Tempelkan job description dari lowongan yang kamu incar..."
            value={jobDesc}
            onChange={(e) => setJobDesc(e.target.value)}
            className="textarea-input"
          />
        </div>

        {error && <div className="error-box">{error}</div>}

        <button type="submit" disabled={loading} className="btn btn-primary">
          {loading ? "Menganalisis..." : "Analisis Gap & Saran CV"}
        </button>
      </form>

      {markdown && <MarkdownViewer content={markdown} />}

      {!loading && !error && !markdown && (
        <div className="empty-state">
          <p>Hasil analisis akan muncul di sini setelah kamu submit.</p>
        </div>
      )}
    </section>
  )
}

export default CvImprover
