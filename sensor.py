"""Support for pulse.eco sensor."""
from __future__ import annotations

from typing import Any, cast

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass
import logging
_LOGGER = logging.getLogger("pulse.eco")

from . import PulseEcoDataCoordinator
from .const import (
    CONF_SENSOR_IDS,
    ATTR_SENSOR_ID,
    ATTR_SENSOR_NAME,
    ATTRIBUTION,
    DEFAULT_NAME,
    DOMAIN,
    ICON,
    SENSOR_TYPES,
    PulseEcoSensorEntityDescription,
)
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    TEMP_CELSIUS,
    Platform,
)

async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the pulse.eco sensors."""
    pulseeco_coordinator = hass.data[DOMAIN]
    sensors = config_entry.options[CONF_SENSOR_IDS]
    l = list()
    for sensor in sensors.split(","):
        s = sensor.split(":")
        logging.error(str(s))

        description = PulseEcoSensorEntityDescription(
            key=s[2],
            name=s[2],
            native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            state_class=SensorStateClass.MEASUREMENT,
        )
        l.append(PulseEcoSensor(pulseeco_coordinator, description))
    async_add_entities(l)



class PulseEcoSensor(
    CoordinatorEntity[PulseEcoDataCoordinator], RestoreEntity, SensorEntity
):
    """Implementation of a pulse.eco sensor."""

    entity_description: PulseEcoSensorEntityDescription
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_icon = ICON

    def __init__(
            self,
            coordinator: PulseEcoDataCoordinator,
            description: PulseEcoSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = description.key
        self._state: StateType = None
        self._attrs: dict[str, Any] = {}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=DEFAULT_NAME,
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://pulse.eco/",
        )

    @property
    def native_value(self) -> StateType:
        """Return native value for entity."""
        if self.coordinator.data:
            state = 0
            if self.entity_description.key in self.coordinator.data:
                if "pm10" in self.coordinator.data[self.entity_description.key]:
                    state = self.coordinator.data[self.entity_description.key]["pm10"]
            self._state = cast(StateType, self.entity_description.value(state))
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data:
            if self.entity_description.key in self.coordinator.data:
                dat = self.coordinator.data[self.entity_description.key]
                for d in dat:
                    self._attrs.update(
                        {
                            d: dat[d],
                        }
                    )
            # self._attrs.update(
            #     {
            #         ATTR_SENSOR_NAME: self.coordinator.data["sensorName"],
            #     }
            # )
            # if self.entity_description.key == "pm10":
            #     self._attrs[ATTR_BYTES_RECEIVED] = self.coordinator.data[
            #         ATTR_BYTES_RECEIVED
            #     ]
            # elif self.entity_description.key == "upload":
            #     self._attrs[ATTR_BYTES_SENT] = self.coordinator.data[ATTR_BYTES_SENT]

        return self._attrs

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if state := await self.async_get_last_state():
            self._state = state.state
