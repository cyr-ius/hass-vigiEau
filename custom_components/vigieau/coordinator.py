"""Coordinator for VigiEau integration."""

from datetime import timedelta
import logging
from typing import Any

from vigieaupy import VigiEau, VigiEauException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .helpers import find_root_item, find_item

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(hours=8)


class VigiEauDataUpdateCoordinator(DataUpdateCoordinator):
    """Define an object to fetch data from VigiEau."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Class to manage fetching data API."""
        self.entry = entry
        self.client = None
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_setup(self) -> None:
        """Initialize the VigiEau client."""
        try:
            self.client = VigiEau(
                async_create_clientsession(self.hass),
            )
        except VigiEauException as error:
            _LOGGER.error("Failed to initialize VigiEau client: %s", error)
            raise

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from VigiEau API."""
        try:
            data = await self.client.async_get_data(
                longitude=self.config_entry.data[CONF_LONGITUDE],
                latitude=self.config_entry.data[CONF_LATITUDE],
                city_id=self.config_entry.data[CONF_ID],
            )
            _LOGGER.debug("Fetched data: %s", data)
            if not data or not isinstance(data, list):
                raise UpdateFailed("No data received from VigiEau API")

            status = {}
            date = dt_util.now().date()
            for k in ("AEP", "SOU", "SUP"):
                status[k] = find_root_item(data, "type", k, default={})
                dateDebut = find_item(status, f"{k}.arrete.dateDebutValidite")
                dateFin = find_item(status, f"{k}.arrete.dateDebutValidite)")
                status[k]["niveauGravite"] = (
                    find_item(status, f"{k}.niveauGravite", "normal")
                    if dateDebut
                    and date > dt_util.parse_date(dateDebut)
                    and (dateFin is None or date < dt_util.parse_date(dateFin))
                    else "normal"
                )
            _LOGGER.debug("Processed status: %s", status)
        except VigiEauException as error:
            raise UpdateFailed(f"Error fetching data: {error}") from error
        else:
            return status
