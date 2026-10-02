import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.user_helper import get_or_create_default_user
from app.models.telegram import TelegramIntegration, NotificationPreference, TelegramNotification
from app.schemas.system import TelegramConfigUpdate, NotificationPrefUpdate
from app.services.telegram.notifier import TelegramService

router = APIRouter(prefix="/telegram", tags=["Telegram"])

@router.get("")
def get_telegram_status(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    tele = user.telegram_integration
    prefs = db.query(NotificationPreference).filter(NotificationPreference.user_id == user.id).first()
    if not prefs:
        prefs = NotificationPreference(user_id=user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)

    masked_token = None
    if tele and tele.bot_token:
        masked_token = f"{tele.bot_token[:6]}...{tele.bot_token[-4:]}"

    return {
        "is_configured": bool(tele and tele.bot_token and tele.chat_id),
        "is_connected": tele.is_connected if tele else False,
        "is_enabled": tele.is_enabled if tele else False,
        "masked_token": masked_token,
        "chat_id": tele.chat_id if tele else None,
        "last_tested_at": tele.last_tested_at if tele else None,
        "preferences": {
            "min_match_percentage": prefs.min_match_percentage,
            "daily_notification_limit": prefs.daily_notification_limit,
            "today_notification_count": prefs.today_notification_count,
            "quiet_hours_enabled": prefs.quiet_hours_enabled,
            "quiet_hours_start": prefs.quiet_hours_start,
            "quiet_hours_end": prefs.quiet_hours_end,
            "notify_high_matches": prefs.notify_high_matches,
            "notify_saved_searches": prefs.notify_saved_searches,
            "notify_interviews": prefs.notify_interviews
        }
    }

@router.post("/configure")
async def configure_telegram(data: TelegramConfigUpdate, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    tele = user.telegram_integration
    if not tele:
        tele = TelegramIntegration(user_id=user.id)
        db.add(tele)

    tele.bot_token = data.bot_token.strip()
    tele.chat_id = data.chat_id.strip()
    tele.is_enabled = data.is_enabled

    # Test connection immediately
    test_res = await TelegramService.test_connection(tele.bot_token, tele.chat_id)
    if test_res.get("success"):
        tele.is_connected = True
        tele.last_tested_at = datetime.datetime.utcnow()
        db.commit()
        return {"success": True, "message": "Telegram bot connected and test message sent successfully!"}
    else:
        tele.is_connected = False
        db.commit()
        return {"success": False, "error": test_res.get("error", "Failed to communicate with Telegram Bot API.")}

@router.post("/test")
async def send_test_message(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    tele = user.telegram_integration
    if not tele or not tele.bot_token or not tele.chat_id:
        raise HTTPException(status_code=400, detail="Telegram is not configured yet.")

    res = await TelegramService.test_connection(tele.bot_token, tele.chat_id)
    if res.get("success"):
        tele.is_connected = True
        tele.last_tested_at = datetime.datetime.utcnow()
        db.commit()
        return {"success": True, "message": "Test notification delivered to your Telegram!"}
    else:
        return {"success": False, "error": res.get("error")}

@router.put("/preferences")
def update_preferences(data: NotificationPrefUpdate, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    prefs = db.query(NotificationPreference).filter(NotificationPreference.user_id == user.id).first()
    if not prefs:
        prefs = NotificationPreference(user_id=user.id)
        db.add(prefs)

    prefs.min_match_percentage = data.min_match_percentage
    prefs.daily_notification_limit = data.daily_notification_limit
    prefs.quiet_hours_enabled = data.quiet_hours_enabled
    prefs.quiet_hours_start = data.quiet_hours_start
    prefs.quiet_hours_end = data.quiet_hours_end
    prefs.notify_high_matches = data.notify_high_matches
    prefs.notify_saved_searches = data.notify_saved_searches
    prefs.notify_interviews = data.notify_interviews

    db.commit()
    return {"message": "Notification preferences updated successfully"}

@router.get("/history")
def get_notification_history(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    notes = db.query(TelegramNotification).filter(
        TelegramNotification.user_id == user.id
    ).order_by(desc(TelegramNotification.sent_at)).limit(50).all()

    return [{
        "id": n.id,
        "title": n.title,
        "type": n.notification_type,
        "is_sent": n.is_sent,
        "error": n.error_message,
        "sent_at": n.sent_at
    } for n in notes]
