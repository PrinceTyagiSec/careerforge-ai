import time
import asyncio
import datetime
import httpx
from typing import List, Optional, Dict, Any
from app.services.job_providers.base import BaseJobProvider, ProviderJobItem
from app.core.config import settings

class AdzunaProvider(BaseJobProvider):
    def __init__(self, app_id: Optional[str] = None, app_key: Optional[str] = None, country: str = "in"):
        super().__init__("Adzuna")
        self.app_id = app_id or settings.ADZUNA_APP_ID
        self.app_key = app_key or settings.ADZUNA_APP_KEY
        self.country = country or settings.DEFAULT_COUNTRY
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self._cache: Dict[str, Tuple[float, List[ProviderJobItem]]] = {}
        self.cache_ttl_seconds = 300 # 5 min cache
        self.rate_limit_delay = 1.0 # 1 sec minimum between requests
        self._last_request_time = 0.0

    async def _rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    async def search(
        self,
        keywords: Optional[str] = None,
        location: Optional[str] = "India",
        page: int = 1,
        results_per_page: int = 20,
        **kwargs
    ) -> List[ProviderJobItem]:
        if not self.app_id or not self.app_key:
            return []

        cache_key = f"{keywords}:{location}:{page}:{results_per_page}"
        if cache_key in self._cache:
            ts, cached_results = self._cache[cache_key]
            if time.time() - ts < self.cache_ttl_seconds:
                return cached_results

        await self._rate_limit()

        endpoint = f"{self.base_url}/{self.country}/search/{page}"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": min(results_per_page, 50),
            "content-type": "application/json"
        }
        if keywords:
            params["what"] = keywords
        if location and location.lower() != "india":
            params["where"] = location

        headers = {"User-Agent": "CareerForge-AI/1.0"}
        retries = 3
        backoff = 1.5

        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=12.0) as client:
                    response = await client.get(endpoint, params=params, headers=headers)
                    
                    if response.status_code == 429:
                        # Rate limited
                        await asyncio.sleep(backoff * (attempt + 1))
                        continue

                    if response.status_code == 200:
                        data = response.json()
                        results = []
                        for item in data.get("results", []):
                            company = item.get("company", {}).get("display_name", "Unknown Company")
                            title = item.get("title", "Untitled Role")
                            desc = item.get("description", "")
                            url = item.get("redirect_url", "")
                            ext_id = str(item.get("id", ""))
                            
                            # Location
                            loc_parts = item.get("location", {}).get("display_name", "")
                            job_loc = loc_parts if loc_parts else (location or "India")
                            
                            # Salary
                            sal_min = item.get("salary_min")
                            sal_max = item.get("salary_max")
                            
                            # Date
                            created_str = item.get("created")
                            pub_date = None
                            if created_str:
                                try:
                                    pub_date = datetime.datetime.fromisoformat(created_str.replace("Z", "+00:00")).replace(tzinfo=None)
                                except Exception:
                                    pass

                            results.append(ProviderJobItem(
                                provider_name="Adzuna",
                                external_id=ext_id,
                                title=title,
                                company_name=company,
                                location=job_loc,
                                description=desc,
                                url=url,
                                salary_min=sal_min,
                                salary_max=sal_max,
                                salary_currency="INR" if self.country == "in" else "USD",
                                published_at=pub_date,
                                raw_data=item
                            ))

                        self._cache[cache_key] = (time.time(), results)
                        return results
                    else:
                        break
            except (httpx.TimeoutException, httpx.RequestError):
                if attempt < retries - 1:
                    await asyncio.sleep(backoff * (attempt + 1))
                else:
                    break

        return []

    async def check_health(self) -> Dict[str, Any]:
        if not self.app_id or not self.app_key:
            return {
                "provider_name": "Adzuna",
                "status": "Unavailable",
                "error_message": "Missing API credentials (app_id or app_key)",
                "latency_ms": 0.0
            }

        start = time.time()
        try:
            endpoint = f"{self.base_url}/{self.country}/search/1"
            params = {
                "app_id": self.app_id,
                "app_key": self.app_key,
                "results_per_page": 1,
                "what": "developer"
            }
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(endpoint, params=params)
                latency = round((time.time() - start) * 1000, 2)
                if res.status_code == 200:
                    return {
                        "provider_name": "Adzuna",
                        "status": "Connected",
                        "error_message": None,
                        "latency_ms": latency
                    }
                elif res.status_code == 429:
                    return {
                        "provider_name": "Adzuna",
                        "status": "Rate Limited",
                        "error_message": "Rate limit exceeded on Adzuna API",
                        "latency_ms": latency
                    }
                else:
                    return {
                        "provider_name": "Adzuna",
                        "status": "Failed",
                        "error_message": f"HTTP {res.status_code}: {res.text[:100]}",
                        "latency_ms": latency
                    }
        except Exception as e:
            latency = round((time.time() - start) * 1000, 2)
            return {
                "provider_name": "Adzuna",
                "status": "Failed",
                "error_message": str(e),
                "latency_ms": latency
            }
