"use client"

import { useState, useEffect } from "react"
import JobCard from "../components/JobCard.jsx"
import MarkdownViewer from "../components/MarkdownViewer.jsx"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE

const JobMatcher = () => {
  const [file, setFile] = useState(null)
  const [location, setLocation] = useState("")
  const [remoteOnly, setRemoteOnly] = useState(false)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState([])
  const [error, setError] = useState("")

  const [gapLoading, setGapLoading] = useState(false)
  const [gapError, setGapError] = useState("")
  const [gapMarkdown, setGapMarkdown] = useState("")
  const [gapJobTitle, setGapJobTitle] = useState("")

  useEffect(() => {
    if (file && results.length > 0) {
      console.log("[v0] Remote filter or location changed, re-fetching jobs...")
      handleSubmit({ preventDefault: () => {} })
    }
  }, [remoteOnly, location])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setResults([])
    setGapMarkdown("")
    setGapError("")
    setGapJobTitle("")

    if (!file) {
      setError("Silakan upload CV kamu (format PDF).")
      return
    }

    const formData = new FormData()
    formData.append("file", file)
    formData.append("top_n", "10")
    if (location) formData.append("location_filter", location)
    formData.append("remote_only", remoteOnly ? "true" : "false")

    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/match-jobs`, {
        method: "POST",
        body: formData,
      })

      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || "Terjadi kesalahan.")
      }

      setResults(data.recommendations || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyzeGap = async (job) => {
    setGapError("")
    setGapMarkdown("")

    if (!file) {
      setGapError("Silakan upload CV terlebih dahulu.")
      return
    }

    setGapJobTitle(`${job.title} @ ${job.company}`)
    setGapLoading(true)

    const formData = new FormData()
    formData.append("file", file)
    formData.append("job_desc", job.description || "")

    try {
      const res = await fetch(`${API_BASE}/analyze-gap`, {
        method: "POST",
        body: formData,
      })
      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || "Terjadi kesalahan.")
      }

      setGapMarkdown(data.markdown || "")
    } catch (err) {
      setGapError(err.message)
    } finally {
      setGapLoading(false)
    }
  }

  return (
    <section className="page-section">
      <div className="section-header">
        <h2>Job Matcher</h2>
        <p>Upload CV kamu, sistem akan mencari job IT yang paling cocok untuk profil kamu.</p>
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

        <div className="form-row">
          <div className="form-group flex-1">
            <label>Lokasi (Opsional)</label>
            <input
              type="text"
              placeholder="Jakarta, Bandung, Remote..."
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="text-input"
            />
          </div>

          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input type="checkbox" checked={remoteOnly} onChange={(e) => setRemoteOnly(e.target.checked)} />
              Hanya Remote
            </label>
          </div>
        </div>

        {error && <div className="error-box">{error}</div>}

        <button type="submit" disabled={loading} className="btn btn-primary">
          {loading ? "Mencari job..." : "Cari Job yang Cocok"}
        </button>
      </form>

      {results.length > 0 && (
        <div className="results-section">
          <h3>{results.length} Job Ditemukan</h3>
          <div className="jobs-grid">
            {results.map((job, idx) => (
              <JobCard key={idx} job={job} onAnalyzeGap={() => handleAnalyzeGap(job)} />
            ))}
          </div>
        </div>
      )}

      {!loading && results.length === 0 && !error && (
        <div className="empty-state">
          <p>Upload CV kamu untuk melihat rekomendasi job yang cocok.</p>
        </div>
      )}

      <div className="gap-panel">
        <h3>Analisis Gap CV vs Job</h3>

        {gapJobTitle && (
          <p className="gap-job-info">
            Posisi: <strong>{gapJobTitle}</strong>
          </p>
        )}

        {gapError && <div className="error-box">{gapError}</div>}

        {gapLoading && (
          <div className="loading-state">
            <p>Menganalisis CV dan job description...</p>
          </div>
        )}

        {gapMarkdown && <MarkdownViewer content={gapMarkdown} />}

        {!gapLoading && !gapMarkdown && !gapError && (
          <p className="helper-text">
            Pilih salah satu job di atas, lalu klik "Analisis Gap" untuk melihat analisis detail.
          </p>
        )}
      </div>
    </section>
  )
}

export default JobMatcher
