"""The Signsbeat integration."""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from .api import SignsbeatApi
from .const import CONF_PAT
from .coordinator import SignsbeatCoordinator
from .data import SignsbeatConfigEntry, SignsbeatData
from .exceptions import SignsbeatApiException, SignsbeatAuthException

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = [Platform.CALENDAR, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: SignsbeatConfigEntry) -> bool:
    """Set up Signsbeat from a config entry."""
    api = SignsbeatApi(hass, entry.data[CONF_PAT])

    # Quickly validate the token before committing to a full coordinator setup.
    today = date.today()
    start = (today - timedelta(days=6)).isoformat()
    end = today.isoformat()
    try:
        await api.async_get_daily_scores(start, end)
    except SignsbeatAuthException as err:
        raise ConfigEntryAuthFailed from err
    except SignsbeatApiException as err:
        raise ConfigEntryNotReady from err

    coordinator = SignsbeatCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = SignsbeatData(api=api, coordinator=coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SignsbeatConfigEntry) -> bool:
    """Unload a Signsbeat config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
