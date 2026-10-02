from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.system import ProviderCredential, ProviderHealth
from app.schemas.system import ProviderHealthItem, ProviderCredentialUpdate
from app.services.job_providers.manager import JobProviderManager
from app.services.ai.ollama_client import OllamaClient

router = APIRouter(prefix="/providers", tags=["Providers"])

@router.get("/health")
async def get_providers_health(db: Session = Depends(get_db)):
    mgr = JobProviderManager(db)
    health_results = await mgr.check_all_providers_health()
    
    # Check Ollama status
    ollama = OllamaClient()
    ollama_health = await ollama.check_health()

    return {
        "providers": health_results,
        "ollama": ollama_health
    }

@router.get("/credentials")
def get_credentials(db: Session = Depends(get_db)):
    creds = db.query(ProviderCredential).all()
    results = []
    for c in creds:
        masked_key = f"{c.api_key_or_token[:4]}...{c.api_key_or_token[-4:]}" if c.api_key_or_token and len(c.api_key_or_token) > 8 else "***"
        results.append({
            "provider_name": c.provider_name,
            "app_id_or_user": c.app_id_or_user,
            "is_enabled": c.is_enabled,
            "has_key": bool(c.api_key_or_token),
            "masked_key": masked_key
        })
    return results

@router.post("/credentials")
def update_credential(data: ProviderCredentialUpdate, db: Session = Depends(get_db)):
    name = data.provider_name.lower().strip()
    if name not in ["adzuna", "jooble"]:
        raise HTTPException(status_code=400, detail="Supported providers: adzuna, jooble")

    cred = db.query(ProviderCredential).filter(ProviderCredential.provider_name == name).first()
    if not cred:
        cred = ProviderCredential(provider_name=name)
        db.add(cred)

    if data.api_key_or_token:
        cred.api_key_or_token = data.api_key_or_token.strip()
    if data.app_id_or_user is not None:
        cred.app_id_or_user = data.app_id_or_user.strip()
    cred.is_enabled = data.is_enabled

    db.commit()
    return {"message": f"Credentials for {name.capitalize()} updated successfully."}
