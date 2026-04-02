"""Config flow for Signsbeat — PAT (Personal Access Token) authentication."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, timedelta
import hashlib
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .api import SignsbeatApi
from .const import CONF_PAT, DOMAIN, LOGGER
from .exceptions import SignsbeatApiException, SignsbeatAuthException

_PAT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PAT): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD),
        ),
    }
)


def _pat_unique_id(pat: str) -> str:
    """Return a stable unique_id derived from the PAT (SHA-256 prefix)."""
    return hashlib.sha256(pat.encode()).hexdigest()[:24]


async def _async_validate_pat(hass: Any, pat: str) -> None:
    """Validate the PAT by making a real request to the Signsbeat API.

    Raises:
        SignsbeatAuthException: Token is invalid / rejected by the API.
        SignsbeatApiException:  Network or API error.

    """
    api = SignsbeatApi(hass, pat)
    today = date.today()
    start = (today - timedelta(days=6)).isoformat()
    end = today.isoformat()
    await api.async_get_daily_scores(start, end)


class SignsbeatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow to handle Signsbeat PAT authentication."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step — ask the user for their PAT."""
        errors: dict[str, str] = {}

        if user_input is not None:
            pat = user_input[CONF_PAT].strip()
            try:
                await _async_validate_pat(self.hass, pat)
            except SignsbeatAuthException:
                errors[CONF_PAT] = "invalid_auth"
            except SignsbeatApiException:
                errors[CONF_PAT] = "cannot_connect"
            except Exception:
                LOGGER.exception("Unexpected error during Signsbeat PAT validation")
                errors["base"] = "unknown"
            else:
                unique_id = _pat_unique_id(pat)
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Signsbeat",
                    data={CONF_PAT: pat},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_PAT_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Start re-authentication when the stored PAT is rejected."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Ask the user to enter a new PAT during re-auth."""
        errors: dict[str, str] = {}

        if user_input is not None:
            pat = user_input[CONF_PAT].strip()
            try:
                await _async_validate_pat(self.hass, pat)
            except SignsbeatAuthException:
                errors[CONF_PAT] = "invalid_auth"
            except SignsbeatApiException:
                errors[CONF_PAT] = "cannot_connect"
            except Exception:
                LOGGER.exception("Unexpected error during Signsbeat re-auth")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    self._get_reauth_entry(),
                    data={CONF_PAT: pat},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=_PAT_SCHEMA,
            errors=errors,
        )
