"""Sensor platform for VigiEau integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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


@dataclass(frozen=True)
class VigiEauSensorDescription(SensorEntityDescription):
    """Describes a sensor."""

    extra_attributes: dict[str, str] | None = None
    default: Any | None = None


SENSOR_TYPES: tuple[VigiEauSensorDescription, ...] = (
    VigiEauSensorDescription(
        key="AEP.niveauGravite",
        name="Eau potable",
        icon="mdi:water",
        translation_key="gravity",
        unit_of_measurement="level",
        extra_attributes={
            "dateDebutValidite": "AEP.arrete.dateDebutValidite",
            "watershedName": "AEP.nom",
            "departement": "AEP.departement",
        },
        options=["alerte", "alerte renforcée", "critique", "normal", "vigilance"],
        device_class=SensorDeviceClass.ENUM,
        default="normal",
    ),
    VigiEauSensorDescription(
        key="SOU.niveauGravite",
        name="Eau souterraine",
        icon="mdi:water",
        translation_key="gravity",
        unit_of_measurement="level",
        extra_attributes={
            "dateDebutValidite": "SOU.arrete.dateDebutValidite",
            "watershedName": "SOU.nom",
            "departement": "SOU.departement",
        },
        options=["alerte", "alerte_renforcee", "critique", "normal", "vigilance"],
        device_class=SensorDeviceClass.ENUM,
        default="normal",
    ),
    VigiEauSensorDescription(
        key="SUP.niveauGravite",
        name="Eau surface",
        icon="mdi:water",
        translation_key="gravity",
        unit_of_measurement="level",
        extra_attributes={
            "dateDebutValidite": "SUP.arrete.dateDebutValidite",
            "watershedName": "SUP.nom",
            "departement": "SUP.departement",
        },
        options=["alerte", "alerte renforcée", "critique", "normal", "vigilance"],
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
        vigieauSensorEntity(coordinator, description) for description in SENSOR_TYPES
    ]
    async_add_entities(entities)


class vigieauSensorEntity(VigiEauEntity, SensorEntity):
    """vigieau Sensor."""

    @property
    def native_value(self):
        """Return sensor state."""
        return find_item(
            self.coordinator.data,
            self.entity_description.key,
            default=self.entity_description.default,
        )
