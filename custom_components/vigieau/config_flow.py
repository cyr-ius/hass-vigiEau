"""Config flow for the VigiEau integration."""

import logging
from typing import Any

from vigieaupy import Consommateur, Source, VigiEau, VigiEauException
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_CODE, CONF_NAME, CONF_SOURCE
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import CONF_COMMUNE, CONF_CONSUMER, CONF_INSEE_CODE, CONF_ZIPCODE, DOMAIN
from .helpers import find_root_item

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SOURCE): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[s.label for s in Source],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required(CONF_CONSUMER): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[s.label for s in Consommateur],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Optional(
            CONF_ZIPCODE, description="Code postal"
        ): selector.NumberSelector(),
        vol.Optional(
            CONF_NAME, description="Nom de la commune"
        ): selector.TextSelector(),
    }
)


class VigiEauConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config or options flow for VigiEau."""

    VERSION = 1
    MINOR_VERSION = 1
    _communes = {}
    _source = None
    _consommateur = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user step."""
        errors = {}
        if user_input is not None:
            try:
                api = VigiEau(session=async_create_clientsession(self.hass))
                if user_input.get(CONF_NAME):
                    self._communes = await api.async_get_cog(
                        name=user_input[CONF_NAME]
                    )
                if user_input.get(CONF_ZIPCODE):
                    self._communes = await api.async_get_cog(
                        code=user_input[CONF_ZIPCODE]
                    )

                if len(self._communes) == 0:
                    return self.async_abort(reason="invalid_location")

                self._source = user_input.get(CONF_SOURCE)
                self._consommateur = user_input.get(CONF_CONSUMER)

            except VigiEauException as error:
                _LOGGER.error(error)
                errors["base"] = "data_fetch_error"
            else:
                return await self.async_step_finish()

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )

    async def async_step_finish(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """User flow to add a new location."""
        errors = {}
        if user_input is not None:
            name = user_input[CONF_NAME]
            commune = find_root_item(self._communes, "nom", name)

            if commune is None:
                return self.async_abort(reason="invalid_location")

            if CONF_CODE not in commune:
                return self.async_abort(reason="code_not_found")

            insee_code = commune[CONF_CODE]

            try:
                api = VigiEau(async_create_clientsession(self.hass))
                s_enum = Source.from_label(self._source)
                c_enum = Consommateur.from_label(self._consommateur)
                await api.async_get_data(
                    codeInsee=insee_code, source=s_enum, consommateur=c_enum
                )
            except VigiEauException:
                errors["base"] = "data_fetch_error"
            else:
                await self.async_set_unique_id(
                    f"{insee_code}-{self._source}-{self._consommateur}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"{DOMAIN} - {name}",
                    data={
                        CONF_COMMUNE: commune,
                        CONF_INSEE_CODE: insee_code,
                        CONF_SOURCE: s_enum.value,
                        CONF_CONSUMER: c_enum.value,
                    },
                )
        noms = sorted([c["nom"] for c in self._communes])
        LOCATION_SCHEMA = vol.Schema(
            {
                vol.Required(CONF_NAME): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=noms,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )
        return self.async_show_form(
            step_id="finish", data_schema=LOCATION_SCHEMA, errors=errors
        )
