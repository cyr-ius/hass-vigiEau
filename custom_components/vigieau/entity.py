"""Parent Entity."""

from typing import Any

from vigieaupy import Consommateur, Source

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_COMMUNE, DOMAIN
from .coordinator import VigiEauDataUpdateCoordinator
from .helpers import find_item


class VigiEauEntity(CoordinatorEntity[VigiEauDataUpdateCoordinator]):
    """Base class for all VigiEau entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: VigiEauDataUpdateCoordinator,
        description: EntityDescription,
        source: Source,
        consumer: Consommateur,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._consumer = consumer
        self._source = source
        src_label = source.label
        consumer_label = consumer.label
        commune_name = coordinator.config_entry.data[CONF_COMMUNE].get("nom", "")
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{source.value}-{consumer.value}-{description.key}"
        self._attr_device_info = DeviceInfo(
            name=f"{src_label} ({commune_name})",
            identifiers={(DOMAIN, f"{coordinator.config_entry.entry_id}-{source.value}")},
        )
        self._attr_name = f"{self.entity_description.name} ({consumer_label})"
        self._item = self._find_item()

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return the state attributes."""
        if not self.entity_description.extra_attributes:
            return None

        return {
            key: find_item(self._item, path)
            for key, path in self.entity_description.extra_attributes.items()
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._item = self._find_item()
        super()._handle_coordinator_update()

    def _find_item(self) -> dict[str, Any]:
        """Find item."""
        return self.coordinator.data[self._source][self._consumer]
