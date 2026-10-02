# CareerForge AI

> **Local-First, India-Focused AI Career Operating System**
> **Production-Quality Job Discovery + Resume Intelligence + Application Management**

CareerForge AI is a **local-first career operating system engineered for the Indian technology ecosystem**.

It brings together real-world multi-provider job discovery, deterministic and AI-assisted matching, factual claim protection, resume quality analysis, ATS optimization, AI-assisted resume tailoring, cover-letter generation, application lifecycle tracking, and scheduled job monitoring into a unified platform.

---

## 📌 Product Overview

CareerForge AI is designed to address the fragmented workflow involved in modern job searching.

Instead of managing job discovery, resume tailoring, ATS analysis, cover letters, and application tracking separately, CareerForge AI brings these capabilities together in one local-first application.

The platform combines:

* Multi-provider job discovery
* Job normalization and deduplication
* Job freshness tracking
* Deterministic and AI-assisted matching
* Match evidence and skill-gap analysis
* Resume quality analysis
* ATS analysis and keyword coverage
* Factual claim protection
* Human-in-the-loop resume review
* AI-assisted resume tailoring
* Fact-protected cover letters
* Resume export
* Application lifecycle tracking
* Scheduled saved-search monitoring
* Telegram notifications and reminders

---

# ✨ Core Architectural Principles

## 🏠 Local-First & Offline-Safe

CareerForge AI runs locally using:

* SQLite
* SQLAlchemy
* FastAPI
* React

There is **no mandatory cloud database or mandatory cloud LLM subscription**.

Local AI functionality is supported through Ollama, with deterministic fallback functionality when offline.

---

## 🔌 Pluggable Multi-Provider Job Ingestion

CareerForge AI supports job discovery from:

* **Adzuna**
* **Jooble**
* **User Imports**

User imports support:

* URLs
* Job description text
* Manual entry

The ingestion pipeline includes:

* Retries
* Caching
* Rate limiting
* Exponential backoff

---

## 🧹 Dedicated Job Quality Pipeline

Job listings are processed through normalization, deduplication, and freshness tracking.

### Deduplication signals include:

* Canonical URL
* Company + title + location hash
* Description Jaccard similarity

### Job freshness states:

| State              | Description                  |
| ------------------ | ---------------------------- |
| `Fresh`            | Fresh job listing            |
| `Recently Updated` | Recently updated listing     |
| `Possibly Stale`   | Potentially outdated listing |
| `Expired`          | Expired listing              |
| `Unavailable`      | Listing is unavailable       |

---

## 🇮🇳 India Tech Market Focus

CareerForge AI is designed specifically for the Indian technology job ecosystem.

The platform supports:

* INR / ₹
* Major Indian technology hubs
* Bengaluru
* Noida
* Gurugram
* Hyderabad
* Pune
* Mumbai
* Chennai
* Remote India
* Regional salary conventions

---

## 🛡️ Factual Integrity Layer

CareerForge AI includes a dedicated factual integrity layer.

The system uses structured:

* `Claim`
* `MatchEvidence`

to maintain traceability between candidate resume information and AI-assisted career outputs.

The factual integrity workflow applies to:

* Tailored resume bullet points
* Matched skills
* Matching evidence
* Cover-letter claims

The project is designed around a **zero-hallucination objective for career content**, with generated claims tied to verified candidate resume statements.

---

## 👤 Human-in-the-Loop Review

CareerForge AI keeps the user involved in the resume-tailoring process.

Users can:

* Approve proposed resume changes
* Reject proposed changes
* Edit proposed changes

This provides human review before proposed resume content is accepted.

---

# 📄 Resume Intelligence

CareerForge AI supports resume input in:

* PDF
* DOCX
* TXT
* Image

The document-processing stack includes:

* PyPDF
* python-docx
* Pillow
* pytesseract

OCR is available as a fallback for supported document-processing workflows.

---

# 🎯 Hybrid Job Matching

CareerForge AI combines:

### Deterministic Matching

Rule-based and structured matching logic.

### AI-Assisted Matching

AI-assisted interpretation of job and candidate information.

The matching workflow is **evidence-backed**, allowing users to inspect:

* Match evidence
* Matched skills
* Skill gaps

---

# 🧩 Skill Gap Analysis

CareerForge AI provides skill-gap information as part of the job-matching workflow.

This allows users to inspect the relationship between:

```text
Candidate Resume
       +
Job Requirements
       ↓
Job Match
       ↓
Matched Skills + Skill Gaps
```

---

# 📊 Resume Quality Engine

CareerForge AI includes a resume quality engine covering:

* Content
* Readability
* ATS
* Completeness

This analysis forms part of the resume preparation workflow before job-specific tailoring and ATS analysis.

---

# 🤖 AI-Assisted Resume Tailoring

CareerForge AI can tailor resume content against a target job using the factual integrity layer.

The workflow is:

```text
Candidate Resume
       ↓
Verified Claims
       +
Job Description
       +
Match Evidence
       ↓
Resume Tailoring
       ↓
Human Review
       ↓
Approve / Reject / Edit
```

The system is designed to keep tailored content traceable to verified candidate resume statements.

---

# 📈 ATS Analysis

CareerForge AI includes ATS analysis and keyword coverage analysis.

The ATS workflow includes:

* ATS analysis
* Keyword analysis
* Keyword coverage
* Keyword Coverage Gauge

This allows users to examine how their resume aligns with the target job.

---

# 💌 Fact-Protected Cover Letters

CareerForge AI supports job-specific cover-letter generation.

Cover-letter claims are processed through the factual integrity approach using verified candidate resume information.

---

# 📤 Resume Export

CareerForge AI supports exporting resumes in:

* PDF
* DOCX
* Markdown
* TXT

The application includes **7 ATS-oriented resume templates**.

### Supported Templates

| Template              | Description                                                     |
| --------------------- | --------------------------------------------------------------- |
| **ATS Simple**        | Single-column resume with clean serif/sans typography           |
| **Modern**            | Modern layout with balanced section spacing                     |
| **Technical**         | Technical skills matrix and system architecture emphasis        |
| **Software Engineer** | Git contributions, scalability metrics, and technology stack    |
| **Cybersecurity**     | Certifications, audit standards, and information-security tools |
| **Minimal**           | Ultra-concise layout with high white-space ratio                |
| **Academic**          | Research publications, projects, and educational credentials    |

---

# 📋 Application Lifecycle Management

CareerForge AI includes application management functionality.

The application workflow supports:

* Recording applications
* Duplicate application warnings
* Status progression
* Chronological application events

This provides a centralized record of application activity throughout the job-search process.

---

# 🔔 Automated Saved Search Monitoring

CareerForge AI includes a scheduled background task runner for saved searches.

The monitoring workflow:

1. Executes saved searches
2. Retrieves job listings
3. Deduplicates listings
4. Scores relevance
5. Processes matching results
6. Sends notifications through Telegram

Telegram integration also supports:

* Duplicate suppression
* Quiet hours
* Interview reminders

---

# 🔄 End-to-End Workflow

```text
1. Upload Resume
   PDF / DOCX / TXT / Image
              ↓
2. OCR Fallback & Entity Parsing
              ↓
3. Atomic Factual Claims Generated & Protected
              ↓
4. Discover Jobs
   Adzuna + Jooble + User Imports
              ↓
5. Normalize, Deduplicate & Validate Freshness
              ↓
6. Hybrid Deterministic & Evidence-Backed Matching
              ↓
7. Inspect Match Evidence & Skill Gaps
              ↓
8. Resume Quality Engine Analysis
   Content + Readability + ATS + Completeness
              ↓
9. Tailor Resume with Factual Protection
              ↓
10. Human Review
    Approve / Reject / Edit
              ↓
11. ATS Analysis & Keyword Coverage Gauge
              ↓
12. Generate Fact-Protected Cover Letter
              ↓
13. Export Resume
    PDF / DOCX / Markdown / TXT
    7 ATS Templates
              ↓
14. Record Application
    Duplicate Warning
              ↓
15. Track Status Progression
    Chronological Events
              ↓
16. Scheduled Telegram Alerts
    & Interview Reminders
```

---

# 🛠️ Technology Stack

## Backend

* **Python 3.14+**
* **FastAPI**
* **SQLAlchemy**
* **SQLite**
* **Pydantic v2**

## Document Processing

* **PyPDF**
* **python-docx**
* **Pillow**
* **pytesseract**
* **ReportLab**

## Frontend

* **React 19**
* **TypeScript**
* **Vite**
* **Vanilla CSS Design System**
* **Lucide React**

## Local AI

* **Ollama**
* **Llama 3**
* **Mistral**
* Deterministic fallback functionality

## Job Providers

* **Adzuna**
* **Jooble**
* User Imports

## Notifications

* **Telegram Bot API**
* Duplicate suppression
* Quiet hours

---

# 🏗️ Architecture

```text
┌───────────────────────────────────────────────┐
│                 React Frontend                │
│          React 19 + TypeScript + Vite        │
│                Vanilla CSS                   │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│                 FastAPI Backend               │
├───────────────────────────────────────────────┤
│ Resume Intelligence                           │
│ Document Processing                           │
│ Job Discovery                                 │
│ Job Normalization                             │
│ Job Deduplication                             │
│ Freshness Tracking                            │
│ Job Matching                                  │
│ Match Evidence                                │
│ Skill Gap Analysis                            │
│ Resume Quality Analysis                       │
│ ATS Analysis                                  │
│ Resume Tailoring                              │
│ Cover Letters                                 │
│ Application Management                        │
│ Scheduled Job Monitoring                      │
└───────────────┬───────────────────┬───────────┘
                │                   │
                ▼                   ▼
        ┌──────────────┐    ┌──────────────┐
        │    SQLite    │    │    Ollama    │
        │   Database   │    │  Local AI    │
        └──────────────┘    └──────────────┘
```

---

# ⚡ Quick Start

## Requirements

CareerForge AI requires:

* **Python 3.14+**
* **Node.js**
* **npm**

Git is recommended for cloning and version control.

Optional integrations require their respective provider credentials.

---

## 1. Clone the Repository

```bash
git clone https://github.com/PrinceTyagiSec/careerforge-ai.git
cd careerforge-ai
```

---

## 2. Run Setup

On Windows:

```bat
setup.bat
```

The setup script prepares the local backend and frontend development environment.

---

## 3. Start CareerForge AI

Run:

```bat
run_all.bat
```

The application starts the backend and frontend locally.

### Frontend

```text
http://127.0.0.1:5173
```

### Backend

```text
http://127.0.0.1:8000
```

### Swagger API Documentation

```text
http://127.0.0.1:8000/docs
```

---

## Manual Startup

### Backend

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend

Open another terminal:

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

---

# 🧪 Testing

## Unit Tests

```bash
cd backend
python -m pytest tests -v
```

---

## Full Integration Verification

CareerForge AI includes a **19-step integration verification**.

Run:

```bash
cd backend
python tests/verify_end_to_end.py
```

---

# 🤖 Ollama

CareerForge AI supports local AI through **Ollama**.

The project currently references:

* Llama 3
* Mistral

Ollama provides the local AI component while deterministic fallback functionality is available for supported offline workflows.

---

# 🔐 Data & Privacy

CareerForge AI follows a local-first architecture using SQLite for local application data.

The project does not require a mandatory cloud database or mandatory cloud LLM subscription.

External job providers and Telegram functionality involve external services and should be configured according to their respective requirements and privacy policies.

Users should avoid committing:

* API credentials
* Telegram bot tokens
* Passwords
* Private keys
* Personal resume data
* Local databases containing private information

to source control.

---

# 🧭 Design Principles

### Local First

The core application is designed to run locally.

### Evidence Backed

Matching and career-content generation are designed around candidate resume evidence.

### Human in the Loop

Users review proposed resume changes before accepting them.

### Multi Provider

Job discovery is not limited to a single provider.

### India Focused

The product is designed around the Indian technology job ecosystem.

### Traceable Matching

Matching provides evidence and skill-gap information as part of the workflow.

---

# 🗺️ Roadmap

The roadmap is intentionally limited to improvements around the existing system:

* [ ] Additional job providers
* [ ] Improvements to job matching
* [ ] Expanded resume parsing
* [ ] Improved OCR processing
* [ ] Additional resume templates
* [ ] Expanded ATS analysis
* [ ] Further notification improvements
* [ ] Expanded automated testing
* [ ] Further application-management improvements

> Roadmap items are future development ideas and are **not currently available features**.

---

# 🤝 Contributing

Contributions, bug reports, documentation improvements, and feature suggestions are welcome.

Before submitting a change:

1. Create a feature branch.
2. Make your changes.
3. Run the relevant tests.
4. Verify the application starts correctly.
5. Do not commit secrets or personal data.
6. Submit a pull request with a clear description.

Example:

```bash
git checkout -b feature/your-feature
```

```bash
git add .
git commit -m "Add your feature"
git push origin feature/your-feature
```

---

# ⚠️ Disclaimer

CareerForge AI is a career-management and productivity tool.

It does not guarantee:

* Employment
* Interviews
* Job offers
* ATS acceptance
* Accuracy of third-party job listings
* Accuracy of AI-generated content

Users should independently verify important information before submitting applications or making career decisions.

---

# 👨‍💻 Author

## Prince Tyagi

Cybersecurity enthusiast and developer focused on:

* Cybersecurity
* Network Security
* Penetration Testing
* Security Research
* Security Tooling
* Software Development

### Connect

* **GitHub:** [@PrinceTyagiSec](https://github.com/PrinceTyagiSec/)
* **LinkedIn:** [Prince Tyagi](https://www.linkedin.com/in/prince-tyagi1/)
* **Portfolio:** [prince-tyagi.netlify.app](https://prince-tyagi.netlify.app/)

---

# 📜 License

Copyright © 2026 **Prince Tyagi**

CareerForge AI is distributed under a **Personal and Non-Commercial Source-Available License**.

The software may be used for personal, educational, research, and other non-commercial purposes subject to the terms of the license.

**Commercial use requires written permission from the copyright holder.**

See [`LICENSE`](LICENSE) for the complete license terms.

---

# ⭐ CareerForge AI

If you find CareerForge AI useful, consider:

* ⭐ Starring the repository
* 🐛 Reporting bugs
* 💡 Suggesting improvements
* 🔧 Contributing code
* 📖 Improving documentation

<p align="center">

**CareerForge AI**
*Local-first career intelligence for the Indian technology ecosystem.*

</p>
