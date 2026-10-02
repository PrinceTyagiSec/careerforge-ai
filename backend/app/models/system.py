import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float
from app.core.database import Base

class ProviderCredential(Base):
    __tablename__ = "provider_credentials"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(50), unique=True, index=True, nullable=False) # adzuna, jooble, ollama, telegram
    api_key_or_token = Column(String(255), nullable=True) # masked in responses
    app_id_or_user = Column(String(255), nullable=True)
    extra_config_json = Column(Text, default="{}")
    is_enabled = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class ProviderHealth(Base):
    __tablename__ = "provider_health"

    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(50), unique=True, index=True, nullable=False)
    status = Column(String(50), default="Unknown") # Connected, Failed, Rate Limited, Degraded, Unavailable
    last_checked_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_success_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    response_latency_ms = Column(Float, nullable=True)
    consecutive_failures = Column(Integer, default=0)


class BackgroundTask(Base):
    __tablename__ = "background_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_identifier = Column(String(100), unique=True, index=True, nullable=False) # UUID or named task
    task_name = Column(String(255), nullable=False)
    status = Column(String(50), default="Pending") # Pending, Running, Completed, Failed, Retrying
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    result_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AIConfiguration(Base):
    __tablename__ = "ai_configurations"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), default="ollama")
    model_name = Column(String(100), default="llama3")
    base_url = Column(String(255), default="http://localhost:11434")
    temperature = Column(Float, default=0.2)
    max_tokens = Column(Integer, default=2048)
    timeout_seconds = Column(Integer, default=45)
    is_enabled = Column(Boolean, default=True)
    fallback_to_deterministic = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
