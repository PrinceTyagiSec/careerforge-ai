import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class TelegramIntegration(Base):
    __tablename__ = "telegram_integrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    bot_token = Column(String(255), nullable=True)
    chat_id = Column(String(100), nullable=True)
    telegram_username = Column(String(100), nullable=True)
    is_connected = Column(Boolean, default=False)
    last_tested_at = Column(DateTime, nullable=True)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="telegram_integration")


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    min_match_percentage = Column(Float, default=75.0)
    daily_notification_limit = Column(Integer, default=15)
    today_notification_count = Column(Integer, default=0)
    last_count_reset_date = Column(String(20), nullable=True) # YYYY-MM-DD
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(String(10), default="22:00")
    quiet_hours_end = Column(String(10), default="08:00")
    
    notify_high_matches = Column(Boolean, default=True)
    notify_saved_searches = Column(Boolean, default=True)
    notify_interviews = Column(Boolean, default=True)
    notify_follow_ups = Column(Boolean, default=True)
    notify_application_status = Column(Boolean, default=True)
    
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class TelegramNotification(Base):
    __tablename__ = "telegram_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    notification_type = Column(String(50), nullable=False) # Job Alert, Interview Reminder, Follow-up, System
    title = Column(String(255), nullable=False)
    message_text = Column(Text, nullable=False)
    is_sent = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
