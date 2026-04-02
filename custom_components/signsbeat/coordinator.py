"""DataUpdateCoordinator for the Signsbeat integration."""

from __future__ import annotations

import asyncio
import datetime
from typing import TYPE_CHECKING, Final

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DailyScore, SignsbeatApi
from .const import LOGGER, SCORE_FETCH_DAYS, UPDATE_INTERVAL_MINUTES
from .exceptions import SignsbeatApiException, SignsbeatAuthException

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SignsbeatConfigEntry

UPDATE_INTERVAL: Final = datetime.timedelta(minutes=UPDATE_INTERVAL_MINUTES)
TIMEOUT: Final = 60  # Must exceed the aiohttp per-request timeout (45 s)


class SignsbeatCoordinator(DataUpdateCoordinator[list[DailyScore]]):
    """Coordinator that polls the Signsbeat API for daily scores."""

    config_entry: SignsbeatConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: SignsbeatConfigEntry,
        api: SignsbeatApi,
    ) -> None:
        """Initialize SignsbeatCoordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name="Signsbeat",
            update_interval=UPDATE_INTERVAL,
        )
        self._api = api

    async def _async_update_data(self) -> list[DailyScore]:
        """Fetch daily scores from the Signsbeat API (rolling 30-day window)."""
        today = datetime.date.today()
        start = (today - datetime.timedelta(days=SCORE_FETCH_DAYS - 1)).isoformat()
        end = today.isoformat()

        async with asyncio.timeout(TIMEOUT):
            try:
                scores = await self._api.async_get_daily_scores(start, end)
            except SignsbeatAuthException as err:
                raise ConfigEntryAuthFailed(err) from err
            except SignsbeatApiException as err:
                raise UpdateFailed(f"Signsbeat API error: {err}") from err

        LOGGER.debug(
            "Fetched %d daily score records (%s → %s)", len(scores), start, end
        )
        return scores
