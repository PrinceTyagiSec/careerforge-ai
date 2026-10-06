# 🚀 CareerForge AI

> **Local-first, India-focused AI Career Operating System**

CareerForge AI is a local-first career management platform built for the Indian technology job ecosystem.

It brings job discovery, resume intelligence, evidence-backed matching, ATS analysis, AI-assisted resume tailoring, fact-aware cover letters, application tracking, and scheduled job monitoring into a single application.

---

## ✨ Why CareerForge AI?

Modern job searching often requires switching between multiple tools for finding jobs, analyzing resumes, tailoring applications, tracking applications, and monitoring new opportunities.

CareerForge AI brings these workflows together while keeping the core application **local-first**.

### Core principles

* 🏠 **Local-first** — Core application data is stored locally.
* 🧠 **AI-assisted** — Local AI can be used through Ollama.
* 🔎 **Evidence-backed** — Matching exposes matched skills, gaps, and supporting evidence.
* 🛡️ **Fact-aware** — AI-assisted career content is grounded in verified resume information.
* 👤 **Human-in-the-loop** — Users review proposed resume changes before accepting them.
* 🇮🇳 **India-focused** — Designed around the Indian technology job market.
* 🔌 **Multi-provider** — Supports multiple job discovery sources.

---

## 📸 Screenshots

> Add application screenshots here.

Recommended screenshots:

* Dashboard
* Job discovery
* Job match & skill-gap analysis
* Resume analysis
* Resume tailoring
* ATS analysis
* Application tracking

Example:

```markdown
![CareerForge AI Dashboard](docs/images/dashboard.png)
```

---

# 🌟 Features

## 🔎 Job Discovery

Discover jobs from multiple sources through a unified ingestion pipeline.

Supported sources:

* Adzuna
* Jooble
* User imports

User imports can include:

* Job URLs
* Job description text
* Manual job entries

The ingestion pipeline supports:

* Retries
* Caching
* Rate limiting
* Exponential backoff

---

## 🧹 Job Normalization & Quality

Job listings are normalized and processed before being presented to the user.

### Deduplication signals

* Canonical URL
* Company + title + location hash
* Description similarity

### Job freshness

| State                | Description                  |
| -------------------- | ---------------------------- |
| `Fresh`            | Fresh job listing            |
| `Recently Updated` | Recently updated listing     |
| `Possibly Stale`   | Potentially outdated listing |
| `Expired`          | Expired listing              |
| `Unavailable`      | Listing is unavailable       |

---

## 🎯 Hybrid Job Matching

CareerForge AI combines two matching approaches:

### Deterministic Matching

Structured, rule-based matching logic.

### AI-Assisted Matching

AI-assisted interpretation of candidate and job information.

Matching results can include:

* Match evidence
* Matched skills
* Skill gaps
* Job requirements
* Candidate evidence

Example workflow:

```text
Candidate Resume
       +
Job Description
       ↓
Hybrid Matching
       ↓
Matched Skills
       +
Skill Gaps
       +
Match Evidence
```

---

## 🛡️ Factual Integrity

CareerForge AI uses structured claims and evidence to keep AI-assisted career content grounded in verified candidate information.

The factuality workflow applies to:

* Resume tailoring
* Resume bullet points
* Match evidence
* Matched skills
* Cover letters

The system is designed around a **claim-grounded approach** rather than unrestricted generation.

Generated career content should remain traceable to verified candidate information.

---

## 👤 Human-in-the-Loop Resume Review

AI-assisted resume tailoring does not have to be accepted automatically.

Users can:

* Approve proposed changes
* Reject proposed changes
* Edit proposed changes

This provides a review step before proposed resume content is accepted.

---

# 📄 Resume Intelligence

CareerForge AI supports resume input from:

* PDF
* DOCX
* TXT
* Images

Document processing uses:

* PyPDF
* python-docx
* Pillow
* pytesseract
* ReportLab

OCR can be used as a fallback for supported document-processing workflows.

---

# 📊 Resume Quality Analysis

The resume quality engine analyzes areas including:

* Content
* Readability
* ATS compatibility
* Completeness

This analysis can be used before job-specific resume tailoring.

---

# 🤖 AI-Assisted Resume Tailoring

Resume tailoring combines:

```text
Candidate Resume
       ↓
Verified Claims
       +
Job Description
       +
Match Evidence
       ↓
AI-Assisted Tailoring
       ↓
Human Review
       ↓
Approve / Reject / Edit
```

The goal is to improve job relevance while keeping proposed content grounded in the candidate's existing information.

---

# 📈 ATS Analysis

CareerForge AI provides ATS and keyword analysis for target jobs.

Capabilities include:

* ATS analysis
* Keyword analysis
* Keyword coverage
* Keyword Coverage Gauge

This helps users inspect how their resume aligns with a target job description.

---

# 💌 Fact-Aware Cover Letters

Generate job-specific cover letters using verified candidate information.

The workflow is designed to keep generated claims grounded in available resume evidence rather than introducing unsupported candidate experience.

---

# 📤 Resume Export

Supported export formats:

* PDF
* DOCX
* Markdown
* TXT

CareerForge AI currently includes **7 resume templates**:

| Template                    | Focus                                                     |
| --------------------------- | --------------------------------------------------------- |
| **ATS Simple**        | Clean single-column resume                                |
| **Modern**            | Modern layout with balanced spacing                       |
| **Technical**         | Technical skills and engineering emphasis                 |
| **Software Engineer** | Engineering projects, contributions, and technology stack |
| **Cybersecurity**     | Security certifications, tools, and standards             |
| **Minimal**           | Concise, high-whitespace layout                           |
| **Academic**          | Research, publications, projects, and education           |

---

# 📋 Application Management

Track job applications throughout the application lifecycle.

Supported functionality includes:

* Recording applications
* Duplicate application warnings
* Status progression
* Chronological application events

This provides a centralized history of application activity.

---

# 🔔 Scheduled Job Monitoring

CareerForge AI supports scheduled monitoring of saved searches.

The workflow can:

1. Execute saved searches
2. Retrieve job listings
3. Normalize and deduplicate listings
4. Score relevance
5. Process matching results
6. Send Telegram notifications

Telegram functionality can include:

* Duplicate suppression
* Quiet hours
* Interview reminders

---

# 🇮🇳 India Technology Market Focus

CareerForge AI is designed around the Indian technology job ecosystem.

The platform supports:

* INR / ₹ salary representation
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

# 🔄 End-to-End Workflow

```text
1. Upload Resume
   PDF / DOCX / TXT / Image
          ↓
2. Document Processing & OCR Fallback
          ↓
3. Extract & Protect Verified Claims
          ↓
4. Discover Jobs
   Adzuna + Jooble + User Imports
          ↓
5. Normalize & Deduplicate
          ↓
6. Track Job Freshness
          ↓
7. Hybrid Job Matching
          ↓
8. Inspect Match Evidence & Skill Gaps
          ↓
9. Analyze Resume Quality
          ↓
10. Tailor Resume
          ↓
11. Human Review
    Approve / Reject / Edit
          ↓
12. ATS & Keyword Analysis
          ↓
13. Generate Fact-Aware Cover Letter
          ↓
14. Export Resume
          ↓
15. Record Application
          ↓
16. Track Application Status
          ↓
17. Scheduled Job Monitoring
          ↓
18. Telegram Notifications
          ↓
19. Interview Reminders
```

---

# 🏗️ Architecture

```text
┌──────────────────────────────────────────────┐
│              React Frontend                  │
│       React + TypeScript + Vite              │
│              Vanilla CSS                     │
└───────────────────────┬──────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────┐
│              FastAPI Backend                 │
├──────────────────────────────────────────────┤
│ Resume Intelligence                          │
│ Document Processing                          │
│ Job Discovery                                │
│ Job Normalization                            │
│ Job Deduplication                            │
│ Freshness Tracking                           │
│ Job Matching                                 │
│ Match Evidence                               │
│ Skill Gap Analysis                           │
│ Resume Quality Analysis                      │
│ ATS Analysis                                 │
│ Resume Tailoring                             │
│ Cover Letters                                │
│ Application Management                       │
│ Scheduled Job Monitoring                     │
└───────────────┬───────────────────┬──────────┘
                │                   │
                ▼                   ▼
        ┌──────────────┐    ┌──────────────┐
        │    SQLite    │    │    Ollama    │
        │   Database   │    │   Local AI   │
        └──────────────┘    └──────────────┘
                │
                ▼
        ┌──────────────────┐
        │ External Services│
        │ Adzuna / Jooble  │
        │ Telegram         │
        └──────────────────┘
```

---

# 🛠️ Technology Stack

## Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic v2

## Document Processing

* PyPDF
* python-docx
* Pillow
* pytesseract
* ReportLab

## Frontend

* React
* TypeScript
* Vite
* Vanilla CSS
* Lucide React

## Local AI

* Ollama
* Llama 3
* Mistral
* Deterministic fallback functionality

## Job Providers

* Adzuna
* Jooble
* User Imports

## Notifications

* Telegram Bot API
* Duplicate suppression
* Quiet hours
* Interview reminders

---

# ⚡ Quick Start

## Requirements

CareerForge AI requires:

* Python 3.14+
* Node.js
* npm
* Git

Optional integrations require their respective provider credentials.

> Make sure the versions above match the current project configuration before installation.

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

# 🧑‍💻 Manual Startup

## Backend

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Frontend

Open another terminal:

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

---

# ⚙️ Configuration

External integrations may require environment variables or provider credentials.

Depending on the enabled functionality, configuration may include:

* Adzuna credentials
* Jooble credentials
* Telegram Bot API token
* Ollama configuration

Keep secrets in local environment configuration.

**Never commit:**

* API keys
* Telegram bot tokens
* Passwords
* Private keys
* `.env` files containing secrets
* Personal resume data
* Local databases containing private information

---

# 🧪 Testing

## Unit Tests

```bash
cd backend
python -m pytest tests -v
```

## End-to-End Verification

CareerForge AI includes an integration verification workflow.

Run:

```bash
cd backend
python tests/verify_end_to_end.py
```

---

# 🤖 Local AI with Ollama

CareerForge AI supports local AI through Ollama.

The project currently references:

* Llama 3
* Mistral

Ollama provides the local AI component while deterministic fallback functionality can support supported offline workflows.

---

# 🔐 Data & Privacy

CareerForge AI follows a local-first architecture using SQLite for local application data.

The core application does not require:

* A mandatory cloud database
* A mandatory cloud LLM subscription

However, external integrations such as job providers and Telegram involve third-party services.

Users should review the applicable provider requirements and privacy policies before enabling external integrations.

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

Cybersecurity-focused developer and creator of CareerForge AI.

**Focus areas:**

* Cybersecurity
* Network Security
* Penetration Testing
* Security Research
* Security Tooling
* Software Development

### Connect

* GitHub: [@PrinceTyagi](https://github.com/PrinceTyagiSec)
* LinkedIn: [Prince Tyagi](https://www.linkedin.com/in/prince-tyagi1/)
* Portfolio: [prince-tyagi.netlify.app](https://prince-tyagi.netlify.app/)

---

# 📜 License

Copyright © 2026 **Prince Tyagi**

CareerForge AI is distributed under a **Personal and Non-Commercial Source-Available License**.

The software may be used for personal, educational, research, and other non-commercial purposes subject to the terms of the license.

**Commercial use requires written permission from the copyright holder.**

See [`LICENSE`](LICENSE) for the complete license terms.

---

## ⭐ CareerForge AI

**Local-first career intelligence for the Indian technology ecosystem.**

If you find the project useful, consider starring the repository, reporting bugs, improving documentation, or contributing code.
