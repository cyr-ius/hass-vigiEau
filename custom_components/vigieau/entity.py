"""Parent Entity."""

from __future__ import annotations

from homeassistant.const import CONF_ID, CONF_LOCATION
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import VigiEauDataUpdateCoordinator
from .helpers import find_item


class VigiEauEntity(CoordinatorEntity[VigiEauDataUpdateCoordinator], Entity):
    """Base class for all Bbox entities."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: VigiEauDataUpdateCoordinator, description: EntityDescription
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = description
        id = coordinator.config_entry.data[CONF_ID]
        location = coordinator.config_entry.data[CONF_LOCATION]

        self._attr_unique_id = f"{id}-{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, id)},
            "name": location,
        }

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return the state attributes."""
        if not self.entity_description.extra_attributes:
            return None

        return {
            key: find_item(self.coordinator.data, path)
            for key, path in self.entity_description.extra_attributes.items()
        }
