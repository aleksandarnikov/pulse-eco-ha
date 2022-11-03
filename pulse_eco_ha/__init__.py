"""Support for fetching pulse.eco data."""
from __future__ import annotations

from datetime import timedelta
import logging
import json
import requests

# import pulse_eco

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL, EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_CITY_NAME,
    CONF_SENSOR_ID,
    CONF_MANUAL,
    CONF_SENSOR_IDS,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_COUNTRY,
    DOMAIN,
    PLATFORMS,
    PULSE_ECO_SERVICE,
)

_LOGGER = logging.getLogger("pulse.eco")


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the pulse.eco component."""
    # logging.error(dir(config_entry.data))
    # for k in config_entry.data.keys:
    #     logging.error(k, config_entry.data[k])
    coordinator = PulseEcoDataCoordinator(hass, config_entry)
    await coordinator.async_setup()

    async def _enable_scheduled_pulseeco(*_):
        """Activate the data update coordinator."""
        coordinator.update_interval = timedelta(
            minutes=config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )
        await coordinator.async_refresh()

    if not config_entry.options.get(CONF_MANUAL, False):
        if hass.state == CoreState.running:
            await _enable_scheduled_pulseeco()
        else:
            # Running a pulse eco fetch during startup can prevent
            # integrations from being able to setup because it
            # can saturate the network interface.
            hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STARTED, _enable_scheduled_pulseeco
            )

    hass.data[DOMAIN] = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload PulseEco Entry from config_entry."""
    hass.services.async_remove(DOMAIN, PULSE_ECO_SERVICE)

    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    if unload_ok:
        hass.data.pop(DOMAIN)
    return unload_ok


class PulseEcoDataCoordinator(DataUpdateCoordinator):
    """Get the latest data from pulse.eco."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the data object."""
        self.hass = hass
        self.config_entry: ConfigEntry = config_entry
        # self.api: pulse_eco.fetch | None = None
        self.api = None
        self.countries: dict[str, dict] = {DEFAULT_COUNTRY: {}}
        super().__init__(
            self.hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self.async_update,
        )

    def initialize(self) -> None:
        """Initialize pulse.eco api."""
        # self.api = speedtest.Speedtest(secure=True)

    def update_data(self):
        """Get the latest data from pulse.eco."""
        # self.api.download()
        # self.api.upload()
        # return self.api.results.dict()
        try:
            sensorids = self.config_entry.options[CONF_SENSOR_IDS]
            logging.error("sensorids " + sensorids)
        except:
            pass

        sensorids = self.config_entry.options[CONF_SENSOR_IDS]

        cities = dict()
        sensors_city = dict()
        sensors_name = dict()
        sensors = set()

        sensor_data = dict()

        for sensor in sensorids.split(","):
            ss = sensor.split(":")
            if ss[0] not in cities:
                cities[ss[0]] = list()
            cities[ss[0]].append(ss[1])
            sensors_city[ss[1]] = ss[0]
            sensors_name[ss[1]] = ss[2]
            sensors.add(ss[1])
            sensor_data[ss[2]] = dict()

        for city in cities:
            print(city)
            response = requests.get("https://" + city + ".pulse.eco/rest/current")
            measurements = response.json()
            for measurement in measurements:
                if measurement["sensorId"] in sensors:
                    sensor_data[sensors_name[measurement["sensorId"]]][measurement["type"]] = int(measurement["value"])
        return sensor_data

        # l = list()
        # rr = dict()
        # for sensor in sensors.split(","):
        #     s = sensor.split(":")

        #     r = dict()
        #     r["pm10"] = 10
        #     r["pm25"] = 125
        #     r["temperature"] = 13
        #     r["sensorId"] = s[1]
        #     r["city"] = s[0]
        #     r["sensorName"] = s[2]
        #     rr[s[2]] = r

        # return rr

    async def async_update(self) -> dict[str, str]:
        """Update pulse.eco data."""
        return await self.hass.async_add_executor_job(self.update_data)

    async def async_setup(self) -> None:
        """Set up Pulse.."""
        await self.hass.async_add_executor_job(self.initialize)

        async def request_update(call: ServiceCall) -> None:
            """Request update."""
            await self.async_request_refresh()

        self.hass.services.async_register(DOMAIN, PULSE_ECO_SERVICE, request_update)

        self.config_entry.async_on_unload(
            self.config_entry.add_update_listener(options_updated_listener)
        )


async def options_updated_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    if entry.options[CONF_MANUAL]:
        hass.data[DOMAIN].update_interval = None
        return

    hass.data[DOMAIN].update_interval = timedelta(
        minutes=entry.options[CONF_SCAN_INTERVAL]
    )
    await hass.data[DOMAIN].async_request_refresh()
