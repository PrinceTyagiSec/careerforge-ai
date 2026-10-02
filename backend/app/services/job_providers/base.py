import abc
import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class ProviderJobItem(BaseModel):
    provider_name: str
    external_id: Optional[str] = None
    title: str
    company_name: str
    location: str = "India"
    description: str
    url: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "INR"
    published_at: Optional[datetime.datetime] = None
    employment_type: str = "Full-time"
    raw_data: Optional[Dict[str, Any]] = None


class BaseJobProvider(abc.ABC):
    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    @abc.abstractmethod
    async def search(
        self,
        keywords: Optional[str] = None,
        location: Optional[str] = "India",
        page: int = 1,
        results_per_page: int = 20,
        **kwargs
    ) -> List[ProviderJobItem]:
        """
        Execute real API search with credentials, pagination, timeout and error handling.
        """
        pass

    @abc.abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """
        Returns {
            'provider_name': str,
            'status': 'Connected' | 'Failed' | 'Rate Limited' | 'Unavailable',
            'error_message': Optional[str],
            'latency_ms': float
        }
        """
        pass
