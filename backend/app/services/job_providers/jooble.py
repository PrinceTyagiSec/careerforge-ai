import time
import asyncio
import datetime
import httpx
from typing import List, Optional, Dict, Any, Tuple

from app.services.job_providers.base import BaseJobProvider, ProviderJobItem
from app.core.config import settings


class JoobleProvider(BaseJobProvider):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Jooble")

        self.api_key = api_key or settings.JOOBLE_API_KEY
        self.base_url = "https://in.jooble.org/api"

        self._cache: Dict[str, Tuple[float, List[ProviderJobItem]]] = {}
        self.cache_ttl_seconds = 300

        self.rate_limit_delay = 1.0
        self._last_request_time = 0.0

    async def _rate_limit(self):
        elapsed = time.time() - self._last_request_time

        if elapsed < self.rate_limit_delay:
            await asyncio.sleep(
                self.rate_limit_delay - elapsed
            )

        self._last_request_time = time.time()

    async def search(
        self,
        keywords: Optional[str] = None,
        location: Optional[str] = "India",
        page: int = 1,
        results_per_page: int = 100,
        remote_status: Optional[str] = None,
        min_salary: Optional[float] = None,
        **kwargs
    ) -> List[ProviderJobItem]:

        if not self.api_key:
            print("JOOBLE: Missing API key")
            return []

        cache_key = (
            f"{keywords}:{location}:{remote_status}:"
            f"{min_salary}:{page}:{results_per_page}"
        )

        if cache_key in self._cache:
            ts, cached_results = self._cache[cache_key]

            if time.time() - ts < self.cache_ttl_seconds:
                print("JOOBLE: Returning cached results")
                return cached_results

        await self._rate_limit()

        endpoint = f"{self.base_url}/{self.api_key}"

        search_keywords = (
            keywords.strip()
            if keywords and keywords.strip()
            else "software developer"
        )

        if remote_status == "Remote":
            search_keywords = f"{search_keywords} remote".strip()

        elif remote_status == "Hybrid":
            search_keywords = f"{search_keywords} hybrid".strip()

        payload = {
            "keywords": search_keywords,
            "location": location or "India",
            "page": page,
        }

        if min_salary is not None:
            payload["salary"] = int(min_salary)

        print("\n========== JOOBLE REQUEST ==========")
        print("endpoint :", endpoint)
        print("keywords :", search_keywords)
        print("location :", location)
        print("page     :", page)
        print("payload  :", payload)
        print("====================================\n")

        retries = 3
        backoff = 1.5

        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:

                    response = await client.post(
                        endpoint,
                        json=payload,
                        headers={
                            "Content-Type": "application/json"
                        }
                    )

                    print(
                        f"JOOBLE RESPONSE: "
                        f"attempt={attempt + 1} "
                        f"status={response.status_code}"
                    )

                    # Rate limit
                    if response.status_code == 429:
                        print(
                            "JOOBLE: Rate limited. "
                            f"Retrying in {backoff * (attempt + 1):.1f}s"
                        )

                        if attempt < retries - 1:
                            await asyncio.sleep(
                                backoff * (attempt + 1)
                            )
                            continue

                        print("JOOBLE: Rate limit retries exhausted")
                        return []

                    # Authentication / API key problem
                    if response.status_code in {401, 403}:
                        print(
                            "JOOBLE AUTH ERROR:",
                            response.text[:1000]
                        )
                        return []

                    # Other HTTP errors
                    if response.status_code != 200:
                        print(
                            "JOOBLE HTTP ERROR:",
                            response.status_code
                        )
                        print(
                            "JOOBLE RESPONSE BODY:",
                            response.text[:2000]
                        )

                        return []

                    # Parse JSON
                    try:
                        data = response.json()
                    except Exception as exc:
                        print("JOOBLE JSON ERROR:", repr(exc))
                        print(
                            "JOOBLE RAW RESPONSE:",
                            response.text[:2000]
                        )
                        return []

                    print(
                        "JOOBLE RESPONSE KEYS:",
                        list(data.keys())
                        if isinstance(data, dict)
                        else type(data).__name__
                    )

                    jobs_data = data.get("jobs", [])

                    if not isinstance(jobs_data, list):
                        print(
                            "JOOBLE INVALID JOBS FIELD:",
                            repr(jobs_data)[:2000]
                        )
                        return []

                    results: List[ProviderJobItem] = []

                    for item in jobs_data:
                        if not isinstance(item, dict):
                            continue

                        company = item.get(
                            "company",
                            "Unknown Company"
                        )

                        title = item.get(
                            "title",
                            "Untitled Role"
                        )

                        snippet = item.get(
                            "snippet",
                            ""
                        )

                        link = item.get(
                            "link",
                            ""
                        )

                        ext_id = str(
                            item.get("id", "")
                        )

                        job_loc = item.get(
                            "location",
                            location or "India"
                        )

                        pub_date = None

                        updated_str = item.get("updated")

                        if updated_str:
                            try:
                                pub_date = (
                                    datetime.datetime
                                    .fromisoformat(
                                        updated_str.replace(
                                            "Z",
                                            "+00:00"
                                        )
                                    )
                                    .replace(tzinfo=None)
                                )
                            except Exception:
                                pass

                        results.append(
                            ProviderJobItem(
                                provider_name="Jooble",
                                external_id=ext_id,
                                title=title,
                                company_name=company,
                                location=job_loc,
                                description=snippet,
                                url=link,
                                salary_currency="INR",
                                published_at=pub_date,
                                raw_data=item
                            )
                        )

                    self._cache[cache_key] = (
                        time.time(),
                        results
                    )

                    print(
                        f"JOOBLE SUCCESS: {len(results)} jobs"
                    )

                    return results

            except httpx.TimeoutException as exc:
                print(
                    f"JOOBLE TIMEOUT "
                    f"(attempt {attempt + 1}):",
                    repr(exc)
                )

                if attempt < retries - 1:
                    await asyncio.sleep(
                        backoff * (attempt + 1)
                    )

            except httpx.RequestError as exc:
                print(
                    f"JOOBLE REQUEST ERROR "
                    f"(attempt {attempt + 1}):",
                    repr(exc)
                )

                if attempt < retries - 1:
                    await asyncio.sleep(
                        backoff * (attempt + 1)
                    )

            except Exception as exc:
                print(
                    "JOOBLE UNEXPECTED ERROR:",
                    repr(exc)
                )
                return []

        return []

    async def check_health(self) -> Dict[str, Any]:

        if not self.api_key:
            return {
                "provider_name": "Jooble",
                "status": "Unavailable",
                "error_message": "Missing Jooble API Key",
                "latency_ms": 0.0
            }

        start = time.time()

        try:
            endpoint = f"{self.base_url}/{self.api_key}"

            payload = {
                "keywords": "software developer",
                "location": "India",
                "page": 1
            }

            async with httpx.AsyncClient(
                timeout=10.0
            ) as client:

                res = await client.post(
                    endpoint,
                    json=payload,
                    headers={
                        "Content-Type": "application/json"
                    }
                )

            latency = round(
                (time.time() - start) * 1000,
                2
            )

            print(
                "\n========== JOOBLE HEALTH =========="
            )
            print("status :", res.status_code)
            print(
                "body   :",
                res.text[:1000]
            )
            print(
                "===================================\n"
            )

            if res.status_code == 200:
                return {
                    "provider_name": "Jooble",
                    "status": "Connected",
                    "error_message": None,
                    "latency_ms": latency
                }

            if res.status_code == 429:
                return {
                    "provider_name": "Jooble",
                    "status": "Rate Limited",
                    "error_message": (
                        "Rate limit exceeded on Jooble API"
                    ),
                    "latency_ms": latency
                }

            return {
                "provider_name": "Jooble",
                "status": "Failed",
                "error_message": (
                    f"HTTP {res.status_code}: "
                    f"{res.text[:500]}"
                ),
                "latency_ms": latency
            }

        except Exception as exc:
            latency = round(
                (time.time() - start) * 1000,
                2
            )

            return {
                "provider_name": "Jooble",
                "status": "Failed",
                "error_message": str(exc),
                "latency_ms": latency
            }