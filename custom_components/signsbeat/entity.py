"""SignsbeatEntity base class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import SignsbeatCoordinator


class SignsbeatEntity(CoordinatorEntity[SignsbeatCoordinator]):
    """Base entity class for Signsbeat — provides shared device info and attribution."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SignsbeatCoordinator,
        user_id: str,
        entry_title: str,
    ) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, user_id)},
            name=entry_title,
            manufacturer="Signsbeat",
        )
