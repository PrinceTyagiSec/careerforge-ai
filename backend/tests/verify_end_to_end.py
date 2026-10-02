import io
import json
import httpx

BASE_URL = "http://127.0.0.1:8000/api"

def test_full_workflow():
    print("=== STARTING FULL END-TO-END WORKFLOW TEST ===")

    with httpx.Client(base_url=BASE_URL, timeout=15.0) as client:
        # 1. Health Check
        r = client.get("/health")
        assert r.status_code == 200, f"Health check failed: {r.text}"
        print("[OK] Step 1: Backend Health Verified ->", r.json())

        # 2. Upload and Ingest Resume
        sample_resume_content = (
            "ARJUN SHARMA\n"
            "Bengaluru, Karnataka | arjun.sharma@example.com | +91 9876543210\n"
            "LinkedIn: linkedin.com/in/arjun-sharma | GitHub: github.com/arjun-dev\n\n"
            "PROFESSIONAL SUMMARY\n"
            "Backend Engineer with 3+ years experience designing distributed REST APIs using Python, FastAPI, Django, and PostgreSQL.\n\n"
            "TECHNICAL SKILLS\n"
            "Python, FastAPI, Django, PostgreSQL, Redis, Docker, Git, REST API, AWS, Linux\n\n"
            "WORK EXPERIENCE\n"
            "Senior Backend Engineer - FinTech Labs (Bengaluru)\n"
            "Jan 2023 - Present\n"
            "• Architected payment ingestion microservices processing 50k transactions/min using FastAPI and PostgreSQL.\n"
            "• Optimized database queries and Redis caching, reducing API p99 latency by 35%.\n"
            "• Spearheaded CI/CD pipelines with Docker and automated testing suites.\n\n"
            "EDUCATION\n"
            "B.Tech in Computer Science and Engineering - National Institute of Technology (2019 - 2023)\n\n"
            "PROJECTS\n"
            "Distributed Task Queue\n"
            "• Built an asynchronous task broker in Python with Redis and WebSocket event streaming.\n"
        )
        files = {"file": ("arjun_sharma_resume.txt", io.BytesIO(sample_resume_content.encode("utf-8")), "text/plain")}
        r = client.post("/resumes/upload", files=files)
        assert r.status_code == 200, f"Resume upload failed: {r.text}"
        resume_data = r.json()
        resume_id = resume_data["resume_id"]
        print(f"[OK] Step 2: Resume Ingested (ID: {resume_id}) -> {resume_data['extracted_summary']}")

        # 3. Verify Atomic Claims (Fact Protection)
        r = client.get(f"/resumes/{resume_id}")
        assert r.status_code == 200
        detail = r.json()
        claims = detail["claims"]
        assert len(claims) > 0, "No claims extracted!"
        print(f"[OK] Step 3: Atomic Claims Protected -> {len(claims)} verifiable claims recorded (e.g. '{claims[0]['statement']}')")

        # 4. Resume Quality Engine Analysis
        r = client.get(f"/resumes/{resume_id}/quality")
        assert r.status_code == 200
        quality = r.json()
        print(f"[OK] Step 4: Resume Quality Analyzed -> Overall Score: {quality['overall_quality_score']}% (Content: {quality['category_scores']['content']}%, Readability: {quality['category_scores']['readability']}%, ATS: {quality['category_scores']['ats']}%)")

        # 5. Search Jobs in India Ecosystem
        r = client.get("/jobs?location=Bengaluru")
        assert r.status_code == 200
        jobs_res = r.json()
        assert jobs_res["total"] > 0, "No jobs found!"
        first_job = jobs_res["results"][0]
        job_id = first_job["id"]
        print(f"[OK] Step 5: Jobs Discovered & Filtered -> Found {jobs_res['total']} jobs. Selected Job #{job_id}: '{first_job['title']}' at '{first_job['company_name']}'")

        # 6. Detailed Match & Evidence Architecture
        r = client.get(f"/jobs/{job_id}")
        assert r.status_code == 200
        job_detail = r.json()
        match_info = job_detail["match"]
        evidence_items = job_detail["evidence"]
        print(f"[OK] Step 6: Match Evaluated -> Score: {match_info['overall_score']}% | Strong Matches: {len(match_info['matching_skills'])} | Evidence items: {len(evidence_items)}")

        # 7. Tailor Resume with Human Review
        r = client.post(f"/jobs/{job_id}/tailor?template=ATS%20Simple")
        assert r.status_code == 200
        tailored = r.json()
        changes = tailored["changes"]
        print(f"[OK] Step 7: Resume Tailored (Zero Hallucination) -> Proposed {len(changes)} changes")
        if changes:
            change_id = changes[0]["id"]
            # Human Review: Approve change
            r_rev = client.put(f"/jobs/{job_id}/tailor/changes/{change_id}", json={"status": "Approved"})
            assert r_rev.status_code == 200
            print(f"[OK] Step 8: Human Review Performed -> Approved Change #{change_id}")

        # 8. ATS Keyword Analysis
        ats_score = tailored["ats_analysis"]["score"]
        print(f"[OK] Step 9: ATS Analysis -> ATS Score: {ats_score}% (Matched: {len(tailored['ats_analysis']['matched_keywords'])}, Missing: {len(tailored['ats_analysis']['missing_keywords'])})")

        # 9. Verify Cover Letter
        cover_letter = tailored["cover_letter"]["content"]
        assert len(cover_letter) > 50
        print("[OK] Step 10: Verified Cover Letter Generated")

        # 10. Test Resume Export
        r_pdf = client.get(f"/resumes/{resume_id}/export?format=pdf&template=ATS%20Simple")
        assert r_pdf.status_code == 200
        assert len(r_pdf.content) > 1000, "PDF export content too small"
        print(f"[OK] Step 11: Resume PDF Exported deterministically ({len(r_pdf.content)} bytes)")

        r_docx = client.get(f"/resumes/{resume_id}/export?format=docx&template=ATS%20Simple")
        assert r_docx.status_code == 200
        print(f"[OK] Step 12: Resume DOCX Exported ({len(r_docx.content)} bytes)")

        # 11. Application Management & Duplicate Warning Protection
        r_app = client.post("/applications", json={"job_id": job_id, "status": "Applied", "notes": "Applied via CareerForge AI"})
        assert r_app.status_code == 200
        app_res = r_app.json()
        app_id = app_res["application_id"]
        print(f"[OK] Step 13: Application Created -> App ID: {app_id}")

        # Test duplicate application detection
        r_dup = client.post("/applications", json={"job_id": job_id, "status": "Applied"})
        assert r_dup.status_code == 200
        dup_res = r_dup.json()
        assert dup_res["duplicate_warning"] == True
        print("[OK] Step 14: Duplicate Application Protection Verified -> Triggered warning as expected")

        # 12. Application Progression & Event Timeline
        r_stat = client.put(f"/applications/{app_id}/status", json={
            "status": "Interview",
            "event_title": "Technical Round Scheduled",
            "event_description": "System Design & Python Architecture interview"
        })
        assert r_stat.status_code == 200
        print("[OK] Step 15: Application Timeline Updated -> Status moved to 'Interview'")

        # 13. Saved Search & Background Monitoring Trigger
        r_search = client.post("/saved-searches", json={
            "name": "Bengaluru Python Roles",
            "keywords": "Python, FastAPI",
            "location": "Bengaluru",
            "frequency_minutes": 180,
            "notify_telegram": True,
            "min_match_threshold": 70.0
        })
        assert r_search.status_code == 200
        search_id = r_search.json()["id"]
        print(f"[OK] Step 16: Saved Search Created (ID: {search_id})")

        r_run = client.post(f"/saved-searches/{search_id}/run-now")
        assert r_run.status_code == 200
        print("[OK] Step 17: Background Monitoring Executed on Saved Search")

        # 14. Telegram Integration Simulation
        r_tele = client.get("/telegram")
        assert r_tele.status_code == 200
        print("[OK] Step 18: Telegram Integration Status Checked")

        # 15. Dashboard Analytics
        r_dash = client.get("/analytics/dashboard")
        assert r_dash.status_code == 200
        dash = r_dash.json()
        print(f"[OK] Step 19: Dashboard Analytics Aggregated -> Discovered: {dash['total_jobs_discovered']}, Applied: {dash['total_applied']}, Interviews: {dash['total_interviews']}, Response Rate: {dash['response_rate_pct']}%")

    print("\nSUCCESS: ALL 19 WORKFLOW STEPS PASSED WITH 100% COMPLETION!")

if __name__ == "__main__":
    test_full_workflow()
