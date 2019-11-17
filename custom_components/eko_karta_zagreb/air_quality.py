"""Air Quality for data from Eko Karta Zagreb."""
import logging
from datetime import timedelta
import voluptuous as vol

from homeassistant.components.air_quality import(
    ATTR_AQI,
    ATTR_ATTRIBUTION,
    ATTR_CO,
    ATTR_NO,
    ATTR_NO2,
    ATTR_OZONE,
    ATTR_PM_0_1,
    ATTR_PM_10,
    ATTR_PM_2_5,
    ATTR_SO2,
    PLATFORM_SCHEMA,
    AirQualityEntity,
)
from homeassistant.const import CONF_NAME
from homeassistant.helpers import config_validation as cv

# Reuse data and API logic from the sensor implementation
from .sensor import (
    ATTRIBUTION,
    DEFAULT_NAME,
    CONF_STATION_ID,
    EkoKartaZagrebData,
    SENSOR_TYPES,
    ATTR_STATION,
    ATTR_UPDATED,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_STATION_ID): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

SCAN_INTERVAL = timedelta(minutes=20)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Eko Karta Zagreb weather platform."""
    name = config.get(CONF_NAME)
    station_id = config.get(CONF_STATION_ID)

    _LOGGER.debug("Setup platform: %s",  station_id )

    probe = EkoKartaZagrebData(station_id=station_id)
    try:
        probe.update()
    except (ValueError, TypeError) as err:
        _LOGGER.error("Received error from Eko Karta Zagreb: %s", err)
        return False

    add_entities([EkoKartaZagrebAirQuality(probe, name)], True)

class EkoKartaZagrebAirQuality(AirQualityEntity):
    """Representation of a air quality condition."""

    def __init__(self, eko_karta_zagreb_data, name):
        """Initialise the platform with a data instance and station name."""
        _LOGGER.debug("Initialized.")
        self.eko_karta_zagreb_data = eko_karta_zagreb_data
        self._name = name
        self._state = self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_AQI][4])
        self._last_update = self.eko_karta_zagreb_data.last_update

    def update(self):
        """Update current conditions."""
        _LOGGER.debug("Update - called.")
        self.eko_karta_zagreb_data.update()
        if self._last_update != self.eko_karta_zagreb_data.last_update:
            _LOGGER.debug("Update - updated from last date found.")
            self._last_update = self.eko_karta_zagreb_data.last_update
            self._state = self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_AQI][4])
        else:
            _LOGGER.debug("Update - no update found.")
    
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    
    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        ret = {
            ATTR_STATION: self.eko_karta_zagreb_data.get_data(SENSOR_TYPES["location"][4]),
            ATTR_UPDATED: self.eko_karta_zagreb_data.last_update.isoformat(),
        }
        return(ret)

    @property
    def particulate_matter_2_5(self):
        """Return the particulate matter 2.5 level."""
        return float(self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_PM_2_5][4]))

    @property
    def particulate_matter_10(self):
        """Return the particulate matter 10 level."""
        return float(self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_PM_10][4]))

    @property
    def particulate_matter_0_1(self):
        """Return the particulate matter 0.1 level."""
        return float(self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_PM_0_1][4]))

    @property
    def air_quality_index(self):
        """Return the Air Quality Index (AQI)."""
        return float(self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_AQI][4]))

    @property
    def ozone(self):
        """Return the O3 (ozone) level."""
        return float(self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_OZONE][4]))

    @property
    def carbon_monoxide(self):
        """Return the CO (carbon monoxide) level."""
        return float(self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_CO][4]))

    @property
    def sulphur_dioxide(self):
        """Return the SO2 (sulphur dioxide) level."""
        return float(self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_SO2][4]))

    @property
    def nitrogen_monoxide(self):
        """Return the NO (nitrogen monoxide) level."""
        return float(self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_NO][4]))

    @property
    def nitrogen_dioxide(self):
        """Return the NO2 (nitrogen dioxide) level."""
        return float(self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_NO2][4]))
