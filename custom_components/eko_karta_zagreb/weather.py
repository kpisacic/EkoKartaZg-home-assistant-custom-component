"""Sensor for data from Eko Karta Zagreb."""
import logging
from datetime import timedelta
import voluptuous as vol

from homeassistant.components.weather import (
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_PRESSURE,
    ATTR_WEATHER_TEMPERATURE,
    PLATFORM_SCHEMA,
    WeatherEntity,
)
from homeassistant.const import CONF_NAME, TEMP_CELSIUS, CONF_LONGITUDE, CONF_LATITUDE
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
    closest_station,
    ekokartazagreb_stations,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_STATION_ID): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Inclusive(
            CONF_LATITUDE, "coordinates", "Latitude and longitude must exist together"
        ): cv.latitude,
        vol.Inclusive(
            CONF_LONGITUDE, "coordinates", "Latitude and longitude must exist together"
        ): cv.longitude,
    }
)

SCAN_INTERVAL = timedelta(minutes=20)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Eko Karta Zagreb weather platform."""
    name = config.get(CONF_NAME)
    station_id = config.get(CONF_STATION_ID)
    latitude = config.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config.get(CONF_LONGITUDE, hass.config.longitude)

    stations = ekokartazagreb_stations()
    _LOGGER.debug("Loaded stations dict: %s", stations)
    station_id = config.get(CONF_STATION_ID) 
    if station_id:
        _LOGGER.debug("Configuration station_id: %s", station_id)
        if station_id not in stations:
            _LOGGER.error("Configuration %s: %s , is not known", CONF_STATION_ID, station_id)
            return False            
    else:
        station_id = closest_station(latitude, longitude, stations)
        _LOGGER.debug("Found closest station_id: %s", station_id)

    station_name = stations[station_id][2]
    _LOGGER.debug("Determined station name: %s", station_name)

    probe = EkoKartaZagrebData(station_id=station_id)
    try:
        probe.update()
    except (ValueError, TypeError) as err:
        _LOGGER.error("Received error from Eko Karta Zagreb: %s", err)
        return False

    add_entities([EkoKartaZagrebWeather(probe, name, station_name)], True)

class EkoKartaZagrebWeather(WeatherEntity):
    """Representation of a weather condition."""

    def __init__(self, eko_karta_zagreb_data, name, station_name):
        """Initialise the platform with a data instance and station name."""
        _LOGGER.debug("Initialized.")
        self.eko_karta_zagreb_data = eko_karta_zagreb_data
        self._name = name
        self._state = self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_WEATHER_TEMPERATURE][4])
        self._last_update = self.eko_karta_zagreb_data.last_update
        self._station_name = station_name

    def update(self):
        """Update current conditions."""
        _LOGGER.debug("Update - called.")
        self.eko_karta_zagreb_data.update()
        if self._last_update != self.eko_karta_zagreb_data.last_update:
            _LOGGER.debug("Update - updated from last date found.")
            self._last_update = self.eko_karta_zagreb_data.last_update
            self._state = self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_WEATHER_TEMPERATURE][4])
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
    def condition(self):
        """Return the current condition."""
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
    def temperature(self):
        """Return the platform temperature."""
        return float(self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_WEATHER_TEMPERATURE][4]))

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def pressure(self):
        """Return the pressure."""
        return float(self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_WEATHER_PRESSURE][4]))

    @property
    def humidity(self):
        """Return the humidity."""
        return float(self.eko_karta_zagreb_data.get_data(SENSOR_TYPES[ATTR_WEATHER_HUMIDITY][4]))
