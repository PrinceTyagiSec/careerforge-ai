import datetime
import httpx
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.telegram import TelegramIntegration, NotificationPreference, TelegramNotification
from app.models.job import Job
from app.models.matching import JobMatch

class TelegramService:
    @staticmethod
    async def send_raw_message(bot_token: str, chat_id: str, text: str) -> Dict[str, Any]:
        """
        Sends Telegram message via Bot API with Markdown formatting.
        """
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(url, json=payload)
            if res.status_code == 200:
                return {"success": True, "data": res.json()}
            else:
                return {"success": False, "error": f"HTTP {res.status_code}: {res.text}"}

    @classmethod
    async def test_connection(cls, bot_token: str, chat_id: str) -> Dict[str, Any]:
        msg = (
            "✨ *CareerForge AI Connected Successfully!*\n\n"
            "Your local-first career operating system is now linked to Telegram.\n"
            "You will receive verified job alerts and scheduled interview reminders here."
        )
        return await cls.send_raw_message(bot_token, chat_id, msg)

    @classmethod
    async def notify_job_alert(
        cls,
        db: Session,
        user_id: int,
        job: Job,
        match: JobMatch
    ) -> bool:
        """
        Formats and dispatches high-quality job alert respecting user thresholds,
        quiet hours, and duplicate suppression.
        """
        tele = db.query(TelegramIntegration).filter(TelegramIntegration.user_id == user_id, TelegramIntegration.is_enabled == True).first()
        if not tele or not tele.bot_token or not tele.chat_id or not tele.is_connected:
            return False

        prefs = db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).first()
        if prefs:
            # Check match threshold
            if match.overall_score < prefs.min_match_percentage:
                return False

            # Check daily limit
            today_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
            if prefs.last_count_reset_date != today_str:
                prefs.last_count_reset_date = today_str
                prefs.today_notification_count = 0
                
            if prefs.today_notification_count >= prefs.daily_notification_limit:
                return False

            # Check quiet hours
            if prefs.quiet_hours_enabled:
                now_time = datetime.datetime.utcnow().strftime("%H:%M")
                if prefs.quiet_hours_start <= now_time or now_time <= prefs.quiet_hours_end:
                    return False

        # Duplicate suppression: Check if this job was already notified
        already_sent = db.query(TelegramNotification).filter(
            TelegramNotification.user_id == user_id,
            TelegramNotification.job_id == job.id,
            TelegramNotification.is_sent == True
        ).first()
        if already_sent:
            return False

        # Format message as per Section 32
        import json
        try:
            matched_skills = json.loads(match.matching_skills_json or "[]")
            missing_skills = json.loads(match.missing_skills_json or "[]")
        except Exception:
            matched_skills = []
            missing_skills = []

        salary_text = "Not specified"
        if job.salary_min and job.salary_max:
            salary_text = f"₹{job.salary_min:,.0f} - ₹{job.salary_max:,.0f} {job.salary_currency}"
        elif job.salary_min:
            salary_text = f"From ₹{job.salary_min:,.0f} {job.salary_currency}"

        sources_list = [s.provider_name for s in job.sources]
        source_label = ", ".join(sources_list) if sources_list else "CareerForge"

        msg = (
            f"🎯 *New High-Match Job Alert: {match.overall_score}% Match*\n\n"
            f"💼 *Title:* {job.title}\n"
            f"🏢 *Company:* {job.company_name}\n"
            f"📍 *Location:* {job.location} ({job.remote_status})\n"
            f"💰 *Salary:* {salary_text}\n"
            f"⏳ *Freshness:* {job.freshness_status}\n"
            f"🌐 *Source:* {source_label}\n\n"
            f"✅ *Top Matching Skills:* {', '.join(matched_skills[:4]) if matched_skills else 'N/A'}\n"
            f"⚠️ *Missing / Desired:* {', '.join(missing_skills[:3]) if missing_skills else 'None identified'}\n\n"
            f"🔗 [View & Apply Listing]({job.canonical_url})"
        )

        res = await cls.send_raw_message(tele.bot_token, tele.chat_id, msg)
        success = res.get("success", False)

        record = TelegramNotification(
            user_id=user_id,
            job_id=job.id,
            notification_type="Job Alert",
            title=f"Job Alert: {job.title} ({match.overall_score}%)",
            message_text=msg,
            is_sent=success,
            error_message=res.get("error"),
            sent_at=datetime.datetime.utcnow()
        )
        db.add(record)

        if success and prefs:
            prefs.today_notification_count += 1

        db.commit()
        return success
