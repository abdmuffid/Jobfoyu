"use client"

const JobCard = ({ job, onAnalyzeGap }) => {
  return (
    <div className="job-card">
      <div className="job-card-header">
        <div className="job-info">
          <h3>{job.title}</h3>
          <p className="job-company">
            {job.company} • {job.location}
          </p>
          {job.is_remote && <span className="badge badge-remote">Remote</span>}
        </div>

        <div className="match-badge">
          <div className="match-percentage">{job.match_percentage}%</div>
          <div className="match-label">cocok</div>
        </div>
      </div>

      <div className="job-card-footer">
        {job.job_url && (
          <a href={job.job_url} target="_blank" rel="noopener noreferrer" className="link-button">
            Lihat Detail ↗
          </a>
        )}

        {onAnalyzeGap && (
          <button type="button" onClick={onAnalyzeGap} className="btn btn-secondary btn-small">
            Analisis Gap
          </button>
        )}
      </div>
    </div>
  )
}

export default JobCard
