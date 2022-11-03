"""Config flow for pulse.eco."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_SENSOR_ID,
    CONF_COUNTRY_ID,
    CONF_CITY_NAME,
    CONF_SENSOR_IDS,
    CONF_MANUAL,
    DEFAULT_COUNTRY,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class PulseEcoFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle pulse.eco config flow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
            config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return PulseEcoOptionsFlowHandler(config_entry)

    async def async_step_user(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self.async_show_form(step_id="user")

        return self.async_create_entry(title=DEFAULT_NAME, data=user_input)


class PulseEcoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle SpeedTest options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._countries: dict = {}

    async def async_step_init(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            #     country_id = user_input[CONF_COUNTRY_ID]
            #     user_input[CONF_COUNTRY_ID] = country_id

            return self.async_create_entry(title="", data=user_input)

        self._countries = self.hass.data[DOMAIN].countries

        options = {
            # vol.Optional(
            #     CONF_COUNTRY_ID,
            #     default=self.config_entry.options.get(CONF_COUNTRY_ID, DEFAULT_COUNTRY),
            # ): vol.In(self._countries.keys()),
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                ),
            ): int,
            vol.Optional(
                CONF_MANUAL, default=self.config_entry.options.get(CONF_MANUAL, False)
            ): bool,
            vol.Optional(
                CONF_SENSOR_IDS,
                default=self.config_entry.options.get(CONF_SENSOR_IDS, ""),
            ): str
        }

        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(options), errors=errors
        )
