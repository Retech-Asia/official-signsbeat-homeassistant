"""Calendar platform for the Signsbeat integration.

Exposes daily health scores as calendar events so they appear
on the Home Assistant Calendar dashboard.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.util import dt as dt_util

from .api import DailyScore, SignsbeatApi
from .const import LOGGER
from .coordinator import SignsbeatCoordinator
from .entity import SignsbeatEntity
from .exceptions import SignsbeatApiException, SignsbeatAuthException

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from .data import SignsbeatConfigEntry

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SignsbeatConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Signsbeat calendar entity."""
    coordinator = entry.runtime_data.coordinator
    api = entry.runtime_data.api
    user_id = entry.unique_id or entry.entry_id
    async_add_entities([SignsbeatCalendarEntity(coordinator, api, user_id, entry.title)])


def _score_to_event(score: DailyScore) -> CalendarEvent:
    """Convert a DailyScore into a CalendarEvent (all-day)."""
    day = date.fromisoformat(score.date)
    return CalendarEvent(
        start=day,
        end=day + timedelta(days=1),
        summary=f"Signsbeat: {score.score} – {score.status}",
        description=(
            f"Health Score: {score.score}\nStatus: {score.status}\nDate: {score.date}"
        ),
    )


class SignsbeatCalendarEntity(SignsbeatEntity, CalendarEntity):
    """A calendar entity that surfaces Signsbeat daily scores as all-day events."""

    _attr_name = "Health scores"

    def __init__(
        self,
        coordinator: SignsbeatCoordinator,
        api: SignsbeatApi,
        user_id: str,
        entry_title: str,
    ) -> None:
        """Initialize the Signsbeat calendar entity."""
        super().__init__(coordinator, user_id, entry_title)
        self._api = api
        self._attr_unique_id = f"{user_id}_calendar"

    @property
    def event(self) -> CalendarEvent | None:
        """Return today's event (the 'current' event for the calendar entity)."""
        today = dt_util.now().date().isoformat()
        scores = self.coordinator.data or []

        today_score = next((s for s in scores if s.date == today), None)
        if today_score is None:
            past_scores = sorted(
                (s for s in scores if s.date <= today),
                key=lambda s: s.date,
                reverse=True,
            )
            today_score = past_scores[0] if past_scores else None

        if today_score is None:
            return None
        return _score_to_event(today_score)

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return score events within the requested time window.

        Calls the Signsbeat API directly so any date range (including past
        months) is supported. Falls back to the coordinator cache on error.
        """
        start_iso = start_date.date().isoformat()
        end_iso = end_date.date().isoformat()

        try:
            scores = await self._api.async_get_daily_scores(start_iso, end_iso)
            LOGGER.debug(
                "Calendar fetch %s – %s returned %d scores", start_iso, end_iso, len(scores)
            )
        except (SignsbeatApiException, SignsbeatAuthException) as err:
            LOGGER.warning(
                "Failed to fetch Signsbeat scores for %s – %s; using cached data. Error: %s",
                start_iso,
                end_iso,
                err,
            )
            scores = [
                s
                for s in (self.coordinator.data or [])
                if start_iso <= s.date <= end_iso
            ]

        return [_score_to_event(score) for score in scores]
