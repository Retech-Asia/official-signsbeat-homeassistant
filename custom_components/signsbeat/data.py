"""Custom types for the Signsbeat integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .api import SignsbeatApi
    from .coordinator import SignsbeatCoordinator

type SignsbeatConfigEntry = ConfigEntry[SignsbeatData]


@dataclass
class SignsbeatData:
    """Runtime data stored on the config entry."""

    api: SignsbeatApi
    coordinator: SignsbeatCoordinator
