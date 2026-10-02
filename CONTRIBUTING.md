# Contributing to CareerForge AI

Thank you for your interest in contributing to **CareerForge AI**.

CareerForge AI is a local-first, India-focused AI career operating system focused on job discovery, resume intelligence, ATS optimization, and application management.

Contributions such as bug fixes, improvements, documentation, testing, and new features are welcome.

---

## Before You Contribute

Please read the project's [`LICENSE`](LICENSE) before contributing.

CareerForge is distributed under a **Personal and Non-Commercial Source-Available License**.

Contributing to the project does not grant permission for commercial use of CareerForge or CareerForge AI. Commercial use requires a separate commercial license from the copyright holder.

---

## Getting Started

### 1. Fork the Repository

Create your own fork of the CareerForge AI repository on GitHub.

### 2. Clone Your Fork

```powershell
git clone https://github.com/PrinceTyagiSec/careerforge-ai.git
cd careerforge-ai
```

Replace the repository URL with your own fork URL when necessary.

### 3. Create a Branch

Use a descriptive branch name:

```powershell
git checkout -b feature/my-feature
```

Examples:

```text
feature/job-import
feature/resume-analysis
feature/ats-analysis
fix/job-deduplication
fix/resume-export
docs/setup-guide
```

---

## Development Requirements

CareerForge AI currently targets Windows development.

Recommended environment:

* Python 3.14+
* Node.js
* npm
* Git
* Ollama (optional for local AI features)

Follow the setup instructions in [`README.md`](README.md).

---

## Making Changes

Before submitting a pull request:

1. Understand the existing architecture.
2. Keep changes focused.
3. Avoid unnecessary changes to unrelated files.
4. Follow the existing coding style.
5. Add or update documentation when necessary.
6. Test your changes locally.
7. Make sure existing functionality is not unnecessarily broken.

---

## Backend Contributions

The backend is built with Python, FastAPI, SQLAlchemy, SQLite, and Pydantic.

When modifying backend functionality:

* Keep API endpoints organized.
* Use appropriate type hints.
* Handle errors properly.
* Keep database operations consistent with the existing architecture.
* Keep job ingestion, document processing, matching, and application-management logic organized.
* Avoid unnecessary blocking operations in asynchronous endpoints.

---

## Frontend Contributions

The frontend uses React, TypeScript, Vite, Vanilla CSS, and Lucide React.

When modifying the frontend:

* Prefer TypeScript types over `any`.
* Keep components focused.
* Reuse existing components where practical.
* Maintain accessibility.
* Keep the UI consistent with the existing CareerForge AI design system.
* Avoid unnecessary changes to the existing styling system.

---

## AI and Resume Features

CareerForge AI includes local AI functionality through Ollama with deterministic fallback behavior when offline.

When contributing to AI-assisted functionality:

* Preserve factual accuracy.
* Do not introduce unsupported candidate claims.
* Keep resume and cover-letter content traceable to verified candidate information.
* Preserve the existing human-review workflow.
* Avoid introducing behavior that fabricates candidate experience, skills, achievements, or qualifications.

---

## Job Data and Matching

CareerForge AI supports job discovery through Adzuna, Jooble, and user imports.

When modifying job-related functionality:

* Preserve existing normalization and deduplication behavior.
* Avoid unnecessarily changing job freshness handling.
* Keep matching behavior consistent with the existing evidence-based approach.
* Ensure changes do not unnecessarily break existing job ingestion workflows.

---

## Sensitive Data

Never commit sensitive or private information.

Do not commit:

* Passwords
* API keys
* Access tokens
* Private certificates
* `.env` files containing secrets
* Private resumes
* Personally identifiable information
* Production databases
* Private logs
* Private job-application data
* Telegram bot credentials

Before creating a pull request, check:

```powershell
git status
git diff
git diff --cached
```

---

## Commit Messages

Use clear commit messages.

Good examples:

```text
Add job deduplication improvement
Fix resume export formatting
Improve ATS keyword analysis
Add Jooble import handling
Update setup documentation
```

Avoid vague messages such as:

```text
fix
changes
update
stuff
```

---

## Pull Requests

When opening a pull request, explain:

1. What was changed.
2. Why the change was needed.
3. How it was tested.
4. Any limitations or known issues.

Example:

```text
### What changed

Improved duplicate detection for imported job listings.

### Why

Multiple providers can return the same job listing, resulting in duplicate
entries.

### Testing

Tested the updated behavior against existing backend tests and sample job
data.

### Notes

The change preserves the existing multi-signal deduplication behavior.
```

---

## Issues

Before opening an issue, search existing issues to see whether the problem has already been reported.

For bug reports, include:

* Operating system
* Python version
* Node.js version
* npm version
* CareerForge AI version or commit
* Steps to reproduce
* Expected behavior
* Actual behavior
* Relevant error messages or logs

Do not upload private resumes, credentials, personal information, or other sensitive data.

---

## Feature Requests

Feature requests are welcome.

Please explain:

* What problem the feature solves.
* How you expect it to work.
* Why it would be useful to CareerForge AI users.
* Any relevant examples or screenshots.

Please avoid submitting feature requests that require unsupported claims about candidate information or fabricated resume content.

---

## Code of Conduct

Be respectful and constructive.

Harassment, discrimination, personal attacks, malicious behavior, and intentionally disruptive contributions are not welcome.

---

## License and Contributions

By submitting a contribution to the CareerForge project, you confirm that:

1. You have the right to submit the contribution.
2. Your contribution does not knowingly violate another person's or organization's intellectual property rights.
3. You understand that the project is distributed under its existing **Personal and Non-Commercial Source-Available License**.

Submitting a contribution does not grant commercial rights to CareerForge or CareerForge AI.

The project maintainer may review, modify, accept, or reject contributions at their discretion.

---

## Thank You

Every useful contribution helps make CareerForge AI better.

Thank you for helping improve the project.
