"""Sensor platform for the Signsbeat integration.

Exposes daily wellness data as three sensor entities per account:
  - ``score``      — most recent health score (0–100).
  - ``status``     — most recent health status label (e.g. "Recovery", "Mild Stress").
  - ``score_date`` — the date the displayed score belongs to.

The ``status`` sensor exposes a ``score_date`` attribute and a ``note``
(human-readable freshness notice) so users can tell at a glance whether
the value is from today or a past date.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Final

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.util import dt as dt_util

from .api import DailyScore
from .const import DOMAIN
from .coordinator import SignsbeatCoordinator
from .entity import SignsbeatEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from .data import SignsbeatConfigEntry

PARALLEL_UPDATES = 0  # Read-only coordinator-based entities


@dataclass(frozen=True)
class SignsbeatSensorEntityDescription(SensorEntityDescription):
    """Extends SensorEntityDescription with a value extractor for DailyScore."""

    value_fn: Callable[[DailyScore], float | str | None] = lambda score: score.score


SIGNSBEAT_SENSORS: Final[tuple[SignsbeatSensorEntityDescription, ...]] = (
    SignsbeatSensorEntityDescription(
        key="score",
        translation_key="score",
        icon="mdi:heart-pulse",
        native_unit_of_measurement="score",
        value_fn=lambda score: score.score,
    ),
    SignsbeatSensorEntityDescription(
        key="status",
        translation_key="status",
        icon="mdi:emoticon-outline",
        value_fn=lambda score: score.status,
    ),
    SignsbeatSensorEntityDescription(
        key="score_date",
        translation_key="score_date",
        icon="mdi:calendar-heart",
        device_class=SensorDeviceClass.DATE,
        value_fn=lambda score: score.date,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SignsbeatConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Signsbeat sensor entities."""
    coordinator = entry.runtime_data.coordinator
    user_id = entry.unique_id or entry.entry_id

    async_add_entities(
        SignsbeatSensor(coordinator, description, user_id, entry.title)
        for description in SIGNSBEAT_SENSORS
    )


def _resolve_score(
    coordinator: SignsbeatCoordinator,
) -> tuple[DailyScore | None, bool]:
    """Return (score, is_today) — falling back to the most recent past score."""
    today = dt_util.now().date().isoformat()
    scores = coordinator.data or []

    for score in scores:
        if score.date == today:
            return score, True

    past = sorted(
        (s for s in scores if s.date < today),
        key=lambda s: s.date,
        reverse=True,
    )
    if past:
        return past[0], False
    return None, False


class SignsbeatSensor(SignsbeatEntity, SensorEntity):
    """A sensor representing one daily metric from Signsbeat."""

    entity_description: SignsbeatSensorEntityDescription

    def __init__(
        self,
        coordinator: SignsbeatCoordinator,
        description: SignsbeatSensorEntityDescription,
        user_id: str,
        entry_title: str,
    ) -> None:
        """Initialize the Signsbeat sensor."""
        super().__init__(coordinator, user_id, entry_title)
        self.entity_description = description
        self._attr_unique_id = f"{user_id}_{description.key}"

    @property
    def native_value(self) -> float | str | date | None:
        """Return the most recent available value for this metric."""
        score, _ = _resolve_score(self.coordinator)
        if score is None:
            return None
        raw = self.entity_description.value_fn(score)
        if self.entity_description.key == "score_date" and isinstance(raw, str):
            return date.fromisoformat(raw)
        return raw

    @property
    def extra_state_attributes(self) -> dict[str, object] | None:
        """Expose attributes relevant to the status sensor only."""
        if self.entity_description.key in ("score", "score_date"):
            return None

        score, is_today = _resolve_score(self.coordinator)
        if score is None:
            return None

        attrs: dict[str, object] = {"score_date": score.date}
        if is_today:
            attrs["note"] = "Score from today"
        else:
            today = dt_util.now().date().isoformat()
            attrs["note"] = (
                f"No data yet for today ({today}). "
                f"Showing last available score from {score.date}."
            )
        return attrs
