"""Constants for the Signsbeat integration."""

from __future__ import annotations

from logging import Logger, getLogger
from typing import Final

LOGGER: Logger = getLogger(__package__)

DOMAIN: Final = "official-signsbeat-homeassistant"

ATTRIBUTION: Final = "Data provided by Signsbeat"

# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
API_BASE_URL: Final = "https://external-analysis-service-c72589e909e4.herokuapp.com"

# Config-entry data key that stores the Personal Access Token
CONF_PAT: Final = "pat"

# Polling interval (cloud services must be >= 60 seconds per HA rules)
UPDATE_INTERVAL_MINUTES: Final = 60

# Rolling window of days to fetch on every coordinator refresh
SCORE_FETCH_DAYS: Final = 30
