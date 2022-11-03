"""Constants used by pulse.eco."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    TEMP_CELSIUS,
    Platform,
)

DOMAIN: Final = "pulse_eco_ha"

PULSE_ECO_SERVICE: Final = "fetch"


@dataclass
class PulseEcoSensorEntityDescription(SensorEntityDescription):
    """Class describing pulseeco sensor entities."""

    value: Callable = round


SENSOR_TYPES: Final[tuple[PulseEcoSensorEntityDescription, ...]] = (
    PulseEcoSensorEntityDescription(
        key="pm10",
        name="PM10",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PulseEcoSensorEntityDescription(
        key="pm25",
        name="PM25",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        # value=lambda value: round(value / 10**6, 2),
    ),
    PulseEcoSensorEntityDescription(
        key="temperature",
        name="Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        # value=lambda value: round(value / 10**6, 2),
    ),
)

CONF_COUNTRY_ID: Final = "city_name"
CONF_CITY_NAME: Final = "city_name"
CONF_SENSOR_ID: Final = "sensor_id"
CONF_MANUAL: Final = "manual"
CONF_SENSOR_IDS: Final = "sensor_ids"

DEFAULT_COUNTRY: Final = "MK"
DEFAULT_NAME: Final = "PulseEco"
DEFAULT_SCAN_INTERVAL: Final = 60

ATTR_SENSOR_ID: Final = "sensor_id"
ATTR_SENSOR_NAME: Final = "sensor_name"

ATTRIBUTION: Final = "Data retrieved from pulse.eco"

ICON: Final = "mdi:speedometer"

PLATFORMS: Final = [Platform.SENSOR]
