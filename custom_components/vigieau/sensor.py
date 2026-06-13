"""Sensor platform for VigiEau integration."""

from dataclasses import dataclass
from typing import Any

from vigieaupy import Consommateur, Source

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import VigiEauConfigEntry
from .entity import VigiEauEntity
from .helpers import find_item

PARALLEL_UPDATES = 0


@dataclass(frozen=True)
class VigiEauSensorDescription(SensorEntityDescription):
    """Describes a sensor."""

    extra_attributes: dict[str, str] | None = None
    default: Any | None = None


SENSOR_TYPES: tuple[VigiEauSensorDescription, ...] = (
    VigiEauSensorDescription(
        key="niveauGravite",
        name="Niveau de gravité",
        icon="mdi:water",
        translation_key="gravity",
        extra_attributes={
            "dateDebutValidite": "arrete.dateDebutValidite",
            "watershedName": "nom",
            "departement": "departement",
        },
        options=["alerte", "alerte_renforcee", "critique", "normal", "vigilance"],
        device_class=SensorDeviceClass.ENUM,
        default="normal",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VigiEauConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Initialize VigiEau config entry."""
    coordinator = entry.runtime_data

    entities = [
        VigiEauSensorEntity(coordinator, description, source, consumer)
        for consumer in Consommateur
        for source in Source
        for description in SENSOR_TYPES
    ]
    async_add_entities(entities)


class VigiEauSensorEntity(VigiEauEntity, SensorEntity):
    """VigiEau Sensor."""

    @property
    def native_value(self) -> str | None:
        """Return sensor state."""
        return find_item(
            self._item,
            self.entity_description.key,
            default=self.entity_description.default,
        )
