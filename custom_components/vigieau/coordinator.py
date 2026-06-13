"""Coordinator for VigiEau integration."""

import asyncio
from datetime import timedelta
import logging
from typing import Any

from vigieaupy import Consommateur, Source, VigiEau, VigiEauException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CODE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import CONF_COMMUNE, DOMAIN
from .helpers import find_item, find_root_item

_LOGGER = logging.getLogger(__name__)


class VigiEauDataUpdateCoordinator(DataUpdateCoordinator):
    """Define an object to fetch data from VigiEau."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Class to manage fetching data API."""
        self.client = None
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(hours=1)
        )

    async def _async_setup(self) -> None:
        """Initialize the VigiEau client."""
        self.client = VigiEau(async_create_clientsession(self.hass))

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from VigiEau API."""
        commune = self.config_entry.data[CONF_COMMUNE]
        insee_code = commune[CONF_CODE]
        consumers = list(Consommateur)
        try:
            results = await asyncio.gather(
                *[
                    self.client.async_get_data(
                        codeInsee=insee_code, consommateur=consumer
                    )
                    for consumer in consumers
                ]
            )
            data = dict(zip(consumers, results, strict=True))

            _LOGGER.debug("Fetched data: %s", data)

            date = dt_util.now().date()
            status: dict[Source, dict[Consommateur, dict[str, Any]]] = {}
            for src in Source:
                for consumer in consumers:
                    data_source = find_root_item(
                        data[consumer],
                        "type",
                        src.value,
                        {"niveauGravite": "normal"},
                    )
                    date_debut = find_item(data_source, "arrete.dateDebutValidite")
                    date_fin = find_item(data_source, "arrete.dateFinValidite")
                    niveau = (
                        find_item(data_source, "niveauGravite", "normal")
                        if date_debut
                        and date > dt_util.parse_date(date_debut)
                        and (date_fin is None or date < dt_util.parse_date(date_fin))
                        else "normal"
                    )
                    status.setdefault(src, {})[consumer] = {
                        **data_source,
                        "niveauGravite": niveau,
                    }

        except VigiEauException as error:
            raise UpdateFailed(f"Error fetching data: {error}") from error
        else:
            _LOGGER.debug("Status: %s", status)
            return status
