"""Config flow for the VigiEau integration."""

from __future__ import annotations

from typing import Any

from addressesfrpy import AddressFr, AddressFrException, AddressNotFound
from vigieaupy import VigiEau, VigiEauException
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult, SubentryFlowResult
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_ID,
    CONF_LATITUDE,
    CONF_LOCATION,
    CONF_LONGITUDE,
    CONF_TARGET,
)
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import DOMAIN
from .helpers import find_item

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(
            CONF_ADDRESS, description="Coordinates or Address"
        ): selector.TextSelector()
    }
)


class VigiEauConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config or options flow for VigiEau."""

    VERSION = 1
    MINOR_VERSION = 1
    addresses = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user step."""

        LOCATION_SCHEMA = {
            vol.Optional(
                CONF_TARGET,
                default={
                    CONF_LONGITUDE: self.hass.config.longitude,
                    CONF_LATITUDE: self.hass.config.latitude,
                },
            ): selector.LocationSelector()
        }

        data_schema = CONFIG_SCHEMA.extend(LOCATION_SCHEMA)
        errors = {}
        if user_input is not None:
            try:
                api = AddressFr(async_create_clientsession(self.hass))
                if user_input.get(CONF_ADDRESS):
                    addresses = await api.async_search(
                        user_input[CONF_ADDRESS],
                        index="poi",
                        category="commune",
                        limit=40,
                    )
                else:
                    addresses = await api.async_reverse(
                        lon=user_input[CONF_TARGET][CONF_LONGITUDE],
                        lat=user_input[CONF_TARGET][CONF_LATITUDE],
                        index="poi",
                        category="commune",
                        limit=40,
                    )

                if len(addresses) == 0:
                    return self.async_abort(reason="no_addresses_found")

                self.addresses = {
                    addr["properties"]["toponym"]: {
                        "properties": addr["properties"],
                        "coordinates": tuple(addr["geometry"]["coordinates"]),
                    }
                    for addr in addresses
                }

            except AddressNotFound:
                errors["base"] = "address_not_found"
            except AddressFrException:
                errors["base"] = "unknown"
            else:
                return await self.async_step_finish()

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors, last_step=True
        )

    async def async_step_finish(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """User flow to add a new location."""
        errors = {}
        if user_input is not None:
            location = user_input[CONF_LOCATION]
            citycode = find_item(
                self.addresses, f"{location}.properties.citycode.0", default=None
            )
            coordinates = find_item(
                self.addresses, f"{location}.coordinates", default=None
            )
            if (
                citycode is None
                and coordinates is None
                and not isinstance(coordinates, tuple)
            ):
                return self.async_abort(reason="invalid_location")

            # Extracting coordinates from the selected address
            lon, lat = coordinates

            try:
                api = VigiEau(async_create_clientsession(self.hass))
                await api.async_get_data(lon, lat, citycode)
            except VigiEauException:
                errors["base"] = "data_fetch_error"
            else:
                await self.async_set_unique_id(citycode)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"{DOMAIN} - {location}",
                    data={
                        CONF_LATITUDE: lat,
                        CONF_LONGITUDE: lon,
                        CONF_ID: citycode,
                        CONF_LOCATION: location,
                    },
                )

        LOCATION_SCHEMA = vol.Schema(
            {
                vol.Required(CONF_LOCATION): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=list(self.addresses.keys()),
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )
        return self.async_show_form(
            step_id="finish", data_schema=LOCATION_SCHEMA, errors=errors
        )
