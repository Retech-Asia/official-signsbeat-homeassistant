"""Async API client for Signsbeat — PAT (Bearer token) authentication."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_BASE_URL, LOGGER
from .exceptions import SignsbeatApiException, SignsbeatAuthException


@dataclass
class DailyScore:
    """A single day's score data returned by the Signsbeat API."""

    date: str
    """ISO 8601 date string, e.g. ``'2025-01-01'``."""

    score: int
    """Health score value (e.g. 0–100)."""

    status: str
    """Human-readable health status label, e.g. ``'Recovery'`` or ``'Mild Stress'``."""


class SignsbeatApi:
    """Async Signsbeat API client authenticated via a Personal Access Token."""

    def __init__(self, hass: HomeAssistant, pat: str) -> None:
        """Initialize the API client."""
        self._hass = hass
        self._pat = pat

    async def _async_request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Make an authenticated request to the Signsbeat API."""
        session = async_get_clientsession(self._hass)
        url = f"{API_BASE_URL}{path}"
        headers = {
            "Authorization": f"Bearer {self._pat}",
            "Accept": "application/json",
        }
        timeout = aiohttp.ClientTimeout(total=45)

        def _check_auth(status: int) -> None:
            if status in (401, 403):
                raise SignsbeatAuthException(
                    f"Authentication failed ({status}) from Signsbeat API: {url}"
                )

        try:
            async with session.request(
                method, url, headers=headers, timeout=timeout, **kwargs
            ) as response:
                _check_auth(response.status)
                response.raise_for_status()
                return await response.json()
        except SignsbeatAuthException:
            raise
        except TimeoutError as err:
            raise SignsbeatApiException(
                f"Timeout error from Signsbeat API: {err}"
            ) from err
        except aiohttp.ClientResponseError as err:
            raise SignsbeatApiException(
                f"HTTP error from Signsbeat API: {err}"
            ) from err
        except aiohttp.ClientError as err:
            raise SignsbeatApiException(
                f"Connection error to Signsbeat API: {err}"
            ) from err

    async def async_get_daily_scores(
        self, start_date: str, end_date: str
    ) -> list[DailyScore]:
        """Fetch daily scores for the given date range.

        Args:
            start_date: Inclusive start in ``YYYY-MM-DD`` format.
            end_date:   Inclusive end in ``YYYY-MM-DD`` format.

        Returns:
            A list of :class:`DailyScore` objects, one per day returned by the API.

        """
        response: dict[str, Any] = await self._async_request(
            "GET",
            "/API/external/getUserScoreData",
            params={"startDate": start_date, "endDate": end_date},
        )

        if not response.get("success"):
            raise SignsbeatApiException(
                f"Signsbeat API returned success=false: {response}"
            )

        data: list[dict[str, Any]] = response.get("data", [])
        LOGGER.debug(
            "async_get_daily_scores(%s → %s) returned %d records",
            start_date,
            end_date,
            len(data),
        )

        results = []
        for item in data:
            score_val = int(item["Score"])
            if score_val >= 65:
                status_label = "Recovery"
            elif score_val >= 25:
                status_label = "Mild Stress"
            else:
                status_label = "Stress"

            results.append(
                DailyScore(
                    date=item["Date"],
                    score=score_val,
                    status=status_label,
                )
            )
        return results
