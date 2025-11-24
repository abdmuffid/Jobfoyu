"use client"

import { useState } from "react"
import JobMatcher from "./pages/JobMatcher.jsx"
import CvImprover from "./pages/CvImprover.jsx"
import "./index.css"

const tabs = [
  { id: "matcher", label: "Job Matcher" },
  { id: "improver", label: "CV Improver" },
]

const App = () => {
  const [activeTab, setActiveTab] = useState("matcher")

  return (
    <div className="app-container">
      <header className="header header-centered">
        <div className="header-content">
          <h1 className="header-title">Jobfoyu</h1>
          <p className="header-subtitle">Discover your perfect IT role and see what skills you need to upgrade!</p>
          <nav className="tab-nav">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`tab-btn ${activeTab === tab.id ? "tab-active" : ""}`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="main-content">{activeTab === "matcher" ? <JobMatcher /> : <CvImprover />}</main>
    </div>
  )
}

export default App
