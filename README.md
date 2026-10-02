# CareerForge AI

> **Local-First, India-Focused AI Career Operating System**
> Production-Quality Job Discovery + Resume Intelligence + Application Management

---

## 1. Product Overview

**CareerForge AI** is a complete, local-first career operating system engineered specifically for the Indian tech ecosystem. Unlike conventional resume builders or superficial chatbots, CareerForge AI unites real-world multi-provider job discovery, deterministic & AI matching, factual claim protection, ATS optimization, and application lifecycle tracking into a single unified platform.

---

## 2. Core Architectural Principles

- **Local-First & Offline-Safe**: Runs locally with SQLite, SQLAlchemy, FastAPI, and React. Zero mandatory cloud database or cloud LLM subscription.
- **Pluggable Multi-Provider Ingestion**: Aggregates real-world jobs from **Adzuna**, **Jooble**, and **User Imports** (URLs, text, manual entry) with retries, caching, rate limiting, and exponential backoff.
- **Dedicated Job Quality Pipeline**: Multi-signal deduplication (canonical URL, company + title + location hash, description Jaccard similarity) and real-time freshness tracking (`Fresh`, `Recently Updated`, `Possibly Stale`, `Expired`, `Unavailable`).
- **India Tech Market Focus**: Native support for INR (₹), major tech hubs (Bengaluru, Noida, Gurugram, Hyderabad, Pune, Mumbai, Chennai, etc.), Remote India, and regional salary conventions.
- **Strict Factual Integrity Layer**: Zero hallucination policy. Every tailored bullet point, matched skill, and cover letter claim is traceable to verified candidate resume statements (`Claim` & `MatchEvidence`).
- **Human-in-the-Loop Review**: Users review, approve, reject, or edit every proposed resume change.
- **Automated Saved Search Monitoring**: Scheduled background task runner executes searches, dedupes listings, scores relevance, and notifies via Telegram.

---

## 3. Technology Stack

- **Backend**: Python 3.14+, FastAPI, SQLAlchemy, SQLite, Pydantic v2
- **Document Processing**: PyPDF, python-docx, Pillow, pytesseract (OCR fallback), ReportLab
- **Frontend**: React 19, TypeScript, Vite, Vanilla CSS Design System, Lucide React
- **Local AI**: Ollama (Llama 3 / Mistral) with seamless deterministic fallback when offline
- **Alerts**: Telegram Bot API integration with duplicate suppression and quiet hours

---

## 4. End-to-End User Workflow

```text
1. Upload Resume (PDF / DOCX / TXT / Image)
      ↓
2. OCR Fallback & Entity Parsing
      ↓
3. Atomic Factual Claims Generated & Protected
      ↓
4. Discover Jobs from Adzuna + Jooble + User Imports
      ↓
5. Normalize, Deduplicate & Validate Freshness
      ↓
6. Hybrid Deterministic & Evidence-Backed Matching
      ↓
7. Inspect Traceable Match Evidence & Skill Gaps
      ↓
8. Resume Quality Engine Analysis (Content, Readability, ATS, Completeness)
      ↓
9. Tailor Resume with Zero Hallucination
      ↓
10. Human Review (Approve / Reject / Edit proposed bullets)
      ↓
11. Run ATS Analysis & Keyword Coverage Gauge
      ↓
12. Generate Fact-Protected Cover Letter
      ↓
13. Export Resume (PDF, DOCX, Markdown, TXT across 7 ATS templates)
      ↓
14. Record Application & Check Duplicate Warning
      ↓
15. Track Status Progression & Chronological Events
      ↓
16. Receive Scheduled Telegram Alerts & Interview Reminders
```

---

## 5. Quick Start & Execution

### 1. Launch Both Backend & Frontend
Double-click `run_all.bat` or run:

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Access the UI at: **`http://127.0.0.1:5173`**  
Backend API Documentation: **`http://127.0.0.1:8000/docs`**

---

## 6. Running Test Suites

### Unit Tests
```bash
cd backend
python -m pytest tests -v
```

### Full 19-Step Integration Verification
```bash
cd backend
python tests/verify_end_to_end.py
```

---

## 7. Supported Resume Templates

1. **ATS Simple**: Single-column, clean serif/sans typography, 100% parseable by legacy ATS.
2. **Modern**: Elegant slate accents, balanced section spacing.
3. **Technical**: Focus on technical skills matrix and system architecture impact.
4. **Software Engineer**: Emphasizes git contributions, scalability metrics, and stack.
5. **Cybersecurity**: Focuses on certifications, audit standards, and infosec tools.
6. **Minimal**: Ultra-concise, high white-space ratio.
7. **Academic**: Extensive research publications, projects, and educational credentials.
