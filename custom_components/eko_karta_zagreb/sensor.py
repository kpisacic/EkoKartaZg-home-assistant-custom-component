"""Sensor for the Eko Karta Zagreb."""
from datetime import timedelta, datetime
import gzip
import json
import logging
import os
from urllib.request import urlopen, URLError, HTTPError
import voluptuous as vol

from homeassistant.components.weather import (
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_PRESSURE,
    ATTR_WEATHER_TEMPERATURE,
)
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
)
from homeassistant.const import (
    CONF_NAME,
    CONF_MONITORED_CONDITIONS,
    __version__,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

ATTR_STATION = "station"
ATTR_UPDATED = "updated"
ATTRIBUTION = "Data provided by Eko Karta Zagreb"

CONF_STATION_ID = "station_id"

DEFAULT_NAME = "eko_karta_zagreb"

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=20)

SENSOR_TYPES = {
    ATTR_WEATHER_TEMPERATURE: ("Temperature", "°C", "temperature", float, "temperature", "", "", "mdi:thermometer"),
    ATTR_WEATHER_HUMIDITY: ("Humidity", "%", "humidity", int, "humidity", "", "", "mdi:water-percent"),
    ATTR_WEATHER_PRESSURE: ("Pressure", "hPa", "pressure", float, "pressure", "", "", "mdi:thermometer-lines"),
    ATTR_AQI: ("Air Quality index", "", "AQI", float, "airIndex", "", "", "mdi:air-filter"),
    ATTR_CO: ("Carbon Monoxide (CO)", "mg/m3", "CO", float, "co", "coIndex", "coAvg",""),
    ATTR_NO: ("Nitrogen Monoxide (NO)", "µg/m3", "NO", float, "no0", "", "no0Avg",""),
    ATTR_NO2: ("Nitrogen Dioxide (NO₂)", "µg/m3", "NO₂", float, "no2", "no2Index", "no2Avg", ""),
    ATTR_OZONE: ("Ozone (O₃)", "µg/m3", "O₃", float, "o3", "o3Index", "o3Avg", ""),
    ATTR_PM_0_1: ("Particles (<1)", "µg/m3", "PM1", float, "pm1", "", "pm1Avg", ""),
    ATTR_PM_10: ("Particles (>10)", "µg/m3", "PM10", float, "pm10", "pm10Index", "pm10Avg", ""),
    ATTR_PM_2_5: ("Particles (2-5)", "µg/m3", "PM2-5", float, "pm25", "pm25Index", "pm25Avg", ""),
    ATTR_SO2: ("Sulphur Dioxide (SO₂)", "µg/m3", "SO₂", float, "so2", "so2Index", "so2Avg", ""),
    # general attributes
    "location": ("Location", "", "", str, "locationName", "", "", ""),
    "lon": ("Longitude", "°", "Long °", float, "xCoordinate", "","", ""),
    "lat": ("Latitude", "°", "Latt °", float, "yCoordinate", "","", ""),
    "update_timestamp": ("Update Timestamp", None, "Update", str, "measurementDate", "", "", "mdi:clock"),
}

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MONITORED_CONDITIONS, default=[ATTR_WEATHER_TEMPERATURE]): vol.All(
            cv.ensure_list, [vol.In(SENSOR_TYPES)]
        ),        
        vol.Required(CONF_STATION_ID): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Eko Karta Zagreb sensor platform."""
    name = config.get(CONF_NAME)
    station_id = config.get(CONF_STATION_ID)

    # if station_name not in dhmz_stations(hass.config.config_dir):
    #     _LOGGER.error(
    #         "Configured DHMZ %s (%s) is not a known station",
    #         CONF_STATION_NAME,
    #         station_name,
    #     )
    #     return False
    
	# if forecast_region_name not in dhmz_regions(hass.config.config_dir):
    #     _LOGGER.error(
    #         "Configured DHMZ %s (%s) is not a known region",
    #         CONF_FORECAST_REGION_NAME,
    #         forecast_region_name,
    #     )
    #     return False

    probe = EkoKartaZagrebData(station_id=station_id)
    try:
        probe.update()
    except (ValueError, TypeError) as err:
        _LOGGER.error("Received error from Eko Karta Zagreb: %s", err)
        return False

    add_entities(
        [
            EkoKartaZagrebSensor(probe, variable, name)
            for variable in config[CONF_MONITORED_CONDITIONS]
        ],
        True,
    )


class EkoKartaZagrebSensor(Entity):
    """Implementation of a Eko Karta Zagreb sensor."""

    def __init__(self, probe, variable, name):
        """Initialize the sensor."""
        self.probe = probe
        self.client_name = name
        self.variable = variable

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.client_name} {SENSOR_TYPES[self.variable][2]}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.probe.get_data(SENSOR_TYPES[self.variable][4])

    @property
    def icon(self):
        """Return the state of the sensor."""
        return SENSOR_TYPES[self.variable][7]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return SENSOR_TYPES[self.variable][1]

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        ret = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_STATION: self.probe.get_data(SENSOR_TYPES["location"][4]),
            ATTR_UPDATED: self.probe.last_update.isoformat(),
        }
        if SENSOR_TYPES[self.variable][5]:
            ret["Index"] = self.probe.get_data(SENSOR_TYPES[self.variable][5])
        if SENSOR_TYPES[self.variable][6]:
            ret["Average"] = self.probe.get_data(SENSOR_TYPES[self.variable][6])
        return(ret)

    def update(self):
        """Delegate update to probe."""
        self.probe.update()

class EkoKartaZagrebData:
    """The class for handling the data retrieval."""

    EKOKARTAZAGREB_AIR_API_URL = "https://ekokartazagreb.stampar.hr/rest/measurements/air/station/{}/latest?"
    EKOKARTAZAGREB_AIRINDEX_API_URL = "https://ekokartazagreb.stampar.hr/rest/measurements/air-index/station/{}/latest?"

    _station_id = ""
    _data = {}

    def __init__(self, station_id):
        """Initialize the probe."""
        self._station_id = station_id
        self._data = {}
        _LOGGER.debug("Initialized sensor data: %s", station_id)

    @property
    def last_update(self):
        """Return the timestamp of the most recent data."""
        date_time = self._data.get("measurementDate")
        if date_time is not None:
            return datetime.fromtimestamp(float(date_time)/1000.)

    def current_air(self):
        """Fetch and parse the latest data."""
        try:
            _LOGGER.debug("Updating - started")
            # check air sensor
            url = self.EKOKARTAZAGREB_AIR_API_URL.format(self._station_id)
            response = urlopen(url)
            elems = json.load(response)

            # check if invalid meassurements of temperature, humidity and pressure - remove them from collection, so they dont get updated
            if len(self._data) != 0 and float(elems["temperature"]) == 0. and float(elems["humidity"]) == 0. and float(elems["pressure"]) == 0. :
                del elems["temperature"]
                del elems["pressure"]
                del elems["humidity"]

            # update sensor data
            self._data.update(elems)

            # check air index sensor
            url = self.EKOKARTAZAGREB_AIRINDEX_API_URL.format(self._station_id)
            response = urlopen(url)
            elems = json.load(response)

            # update sensor data
            self._data.update(elems)

        except HTTPError as err:
            _LOGGER.error("HTTP error: %s", err.reason )
        except URLError as err:
            _LOGGER.error("URL error: %s", err.reason )
        except json.JSONDecodeError as err:
            _LOGGER.error("JSON decoding error: %s", err.msg )

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from Eko Karta Zagreb."""
        if self.last_update and (
            self.last_update + timedelta(hours=1)
            > datetime.now()
        ):
            _LOGGER.debug("Skipping sensor data update, last_update was: %s", self.last_update)
            return  # Not time to update yet; data is only hourly

        _LOGGER.debug("Doing sensor data update, last_update was: %s", self.last_update)
        self.current_air()

        _LOGGER.debug("Sensor, current data: %s", self._data)

        _LOGGER.debug("Updating - finished.")

    def get_data(self, variable):
        """Get the data."""
        return self._data.get(variable)

def _get_ekokartazagreb_stations():
    """Return {CONF_STATION: (lat, lon)} for all stations, for auto-config."""
    # capital_stations = {r["Station"] for r in DhmzData.current_situation()}
    # req = requests.get(
    #     "https://www.zamg.ac.at/cms/en/documents/climate/"
    #     "doc_metnetwork/zamg-observation-points",
    #     timeout=15,
    # )
    stations = {}
    # for row in csv.DictReader(req.text.splitlines(), delimiter=";", quotechar='"'):
    #     if row.get("synnr") in capital_stations:
    #         try:
    #             stations[row["synnr"]] = tuple(
    #                 float(row[coord].replace(",", "."))
    #                 for coord in ["breite_dezi", "länge_dezi"]
    #             )
    #         except KeyError:
    #             _LOGGER.error("ZAMG schema changed again, cannot autodetect station")
    return stations


def ekokartazagreb_stations(cache_dir):
    """Return {CONF_STATION: (lat, lon)} for all stations, for auto-config.

    Results from internet requests are cached as compressed json, making
    subsequent calls very much faster.
    """
    cache_file = os.path.join(cache_dir, ".zamg-stations.json.gz")
    if not os.path.isfile(cache_file):
        stations = _get_ekokartazagreb_stations()
        with gzip.open(cache_file, "wt") as cache:
            json.dump(stations, cache, sort_keys=True)
        return stations
    with gzip.open(cache_file, "rt") as cache:
        return {k: tuple(v) for k, v in json.load(cache).items()}
