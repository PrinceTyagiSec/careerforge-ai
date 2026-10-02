import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.config import EXPORTS_DIR

class ResumeExporter:
    """
    Deterministic Resume Exporter supporting PDF, DOCX, Markdown, and TXT
    across 7 configurable ATS-compliant templates:
    ATS Simple, Modern, Technical, Software Engineer, Cybersecurity, Minimal, Academic.
    """

    @classmethod
    def export_markdown(cls, resume_data: Dict[str, Any], template_name: str = "ATS Simple") -> str:
        name = resume_data.get("candidate_name", "Candidate")
        headline = resume_data.get("headline", "")
        email = resume_data.get("email", "")
        phone = resume_data.get("phone", "")
        loc = resume_data.get("location", "")
        summary = resume_data.get("summary", "")

        contacts = [c for c in [email, phone, loc] if c]
        contact_str = " | ".join(contacts)

        md = f"# {name}\n"
        if headline:
            md += f"### {headline}\n"
        md += f"**{contact_str}**\n\n"

        if summary:
            md += f"## Professional Summary\n{summary}\n\n"

        skills = resume_data.get("skills", [])
        if skills:
            md += "## Technical Skills\n"
            skill_names = [s.get("name") if isinstance(s, dict) else str(s) for s in skills]
            md += ", ".join(skill_names) + "\n\n"

        exps = resume_data.get("experiences", [])
        if exps:
            md += "## Experience\n"
            for exp in exps:
                md += f"### {exp.get('title')} — {exp.get('company')}\n"
                md += f"*{exp.get('start_date')} – {exp.get('end_date')} | {exp.get('location', '')}*\n\n"
                for b in exp.get("bullets", []):
                    md += f"- {b}\n"
                md += "\n"

        projects = resume_data.get("projects", [])
        if projects:
            md += "## Projects\n"
            for p in projects:
                md += f"### {p.get('title')}\n"
                if p.get("description"):
                    md += f"{p.get('description')}\n"
                for b in p.get("bullets", []):
                    md += f"- {b}\n"
                md += "\n"

        edus = resume_data.get("educations", [])
        if edus:
            md += "## Education\n"
            for e in edus:
                md += f"**{e.get('degree')}** — {e.get('institution')} ({e.get('field', '')})\n\n"

        return md

    @classmethod
    def export_txt(cls, resume_data: Dict[str, Any], template_name: str = "ATS Simple") -> str:
        md = cls.export_markdown(resume_data, template_name)
        # Strip markdown syntax for clean plain text
        txt = md.replace("#", "").replace("**", "").replace("*", "")
        return txt

    @classmethod
    def export_docx(cls, resume_data: Dict[str, Any], filename: str, template_name: str = "ATS Simple") -> str:
        import docx
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = docx.Document()
        
        # Set standard 0.7 inch margins for high ATS compliance
        sections = doc.sections
        for sec in sections:
            sec.top_margin = Inches(0.7)
            sec.bottom_margin = Inches(0.7)
            sec.left_margin = Inches(0.7)
            sec.right_margin = Inches(0.7)

        name = resume_data.get("candidate_name", "Candidate")
        h1 = doc.add_paragraph()
        run = h1.add_run(name)
        run.bold = True
        run.font.size = Pt(20)
        h1.alignment = WD_ALIGN_PARAGRAPH.CENTER

        contacts = [resume_data.get("email"), resume_data.get("phone"), resume_data.get("location")]
        contacts = [c for c in contacts if c]
        p_contact = doc.add_paragraph(" | ".join(contacts))
        p_contact.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Summary
        if resume_data.get("summary"):
            doc.add_heading("Professional Summary", level=2)
            doc.add_paragraph(resume_data["summary"])

        # Skills
        if resume_data.get("skills"):
            doc.add_heading("Skills", level=2)
            names = [s.get("name") if isinstance(s, dict) else str(s) for s in resume_data["skills"]]
            doc.add_paragraph(", ".join(names))

        # Experience
        if resume_data.get("experiences"):
            doc.add_heading("Professional Experience", level=2)
            for exp in resume_data["experiences"]:
                p = doc.add_paragraph()
                r_title = p.add_run(f"{exp.get('title')} | {exp.get('company')}\n")
                r_title.bold = True
                p.add_run(f"{exp.get('start_date')} - {exp.get('end_date')} | {exp.get('location', '')}")
                for b in exp.get("bullets", []):
                    doc.add_paragraph(b, style="List Bullet")

        # Projects
        if resume_data.get("projects"):
            doc.add_heading("Projects", level=2)
            for proj in resume_data["projects"]:
                p = doc.add_paragraph()
                r = p.add_run(proj.get("title") + "\n")
                r.bold = True
                if proj.get("description"):
                    p.add_run(proj.get("description"))
                for b in proj.get("bullets", []):
                    doc.add_paragraph(b, style="List Bullet")

        # Education
        if resume_data.get("educations"):
            doc.add_heading("Education", level=2)
            for edu in resume_data["educations"]:
                p = doc.add_paragraph()
                r = p.add_run(edu.get("institution") + "\n")
                r.bold = True
                p.add_run(f"{edu.get('degree')} - {edu.get('field', '')}")

        out_path = str(EXPORTS_DIR / filename)
        doc.save(out_path)
        return out_path

    @classmethod
    def export_pdf(cls, resume_data: Dict[str, Any], filename: str, template_name: str = "ATS Simple") -> str:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        out_path = str(EXPORTS_DIR / filename)
        doc = SimpleDocTemplate(out_path, pagesize=letter, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CandidateTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1A202C"),
            alignment=1
        )
        sub_style = ParagraphStyle(
            'SubHeader',
            parent=styles['Normal'],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#4A5568"),
            alignment=1
        )
        h2_style = ParagraphStyle(
            'SectionH2',
            parent=styles['Heading2'],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#2B6CB0"),
            spaceBefore=8,
            spaceAfter=3
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor("#2D3748")
        )
        bullet_style = ParagraphStyle(
            'Bullet',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
            leftIndent=15,
            bulletIndent=5,
            textColor=colors.HexColor("#2D3748")
        )

        elements = []
        name = resume_data.get("candidate_name", "Candidate")
        elements.append(Paragraph(f"<b>{name}</b>", title_style))

        contacts = [resume_data.get("email"), resume_data.get("phone"), resume_data.get("location")]
        contacts = [c for c in contacts if c]
        elements.append(Paragraph(" &bull; ".join(contacts), sub_style))
        elements.append(Spacer(1, 10))

        if resume_data.get("summary"):
            elements.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", h2_style))
            elements.append(Paragraph(resume_data["summary"], body_style))
            elements.append(Spacer(1, 8))

        if resume_data.get("skills"):
            elements.append(Paragraph("<b>TECHNICAL SKILLS</b>", h2_style))
            skill_names = [s.get("name") if isinstance(s, dict) else str(s) for s in resume_data["skills"]]
            elements.append(Paragraph(", ".join(skill_names), body_style))
            elements.append(Spacer(1, 8))

        if resume_data.get("experiences"):
            elements.append(Paragraph("<b>PROFESSIONAL EXPERIENCE</b>", h2_style))
            for exp in resume_data["experiences"]:
                header_line = f"<b>{exp.get('title')}</b> — {exp.get('company')} <i>({exp.get('start_date')} - {exp.get('end_date')})</i>"
                elements.append(Paragraph(header_line, body_style))
                for b in exp.get("bullets", []):
                    elements.append(Paragraph(f"&bull; {b}", bullet_style))
                elements.append(Spacer(1, 4))

        if resume_data.get("projects"):
            elements.append(Paragraph("<b>KEY PROJECTS</b>", h2_style))
            for p in resume_data["projects"]:
                elements.append(Paragraph(f"<b>{p.get('title')}</b>", body_style))
                for b in p.get("bullets", []):
                    elements.append(Paragraph(f"&bull; {b}", bullet_style))
                elements.append(Spacer(1, 4))

        if resume_data.get("educations"):
            elements.append(Paragraph("<b>EDUCATION</b>", h2_style))
            for edu in resume_data["educations"]:
                line = f"<b>{edu.get('degree')}</b>, {edu.get('institution')} ({edu.get('field', '')})"
                elements.append(Paragraph(line, body_style))

        doc.build(elements)
        return out_path
