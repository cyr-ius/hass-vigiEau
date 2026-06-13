"""The VigiEau integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import VigiEauDataUpdateCoordinator

type VigiEauConfigEntry = ConfigEntry[VigiEauDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: VigiEauConfigEntry) -> bool:
    """Set up VigiEau from a config entry."""
    coordinator = VigiEauDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, (Platform.SENSOR,))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: VigiEauConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, (Platform.SENSOR,))
