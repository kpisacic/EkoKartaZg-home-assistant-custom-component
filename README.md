# EkoKartaZg-home-assistant-custom-component
Home Assistant Custom Components for "Eko Karta Zagreb" service (Grad Zagreb and Nastavni zavod za javno zdravstvo "Andrija Štampar")

The `eko_karta_zagreb` weather platform provide meteorological and ecological data for Eko Karta Zagreb service (Grad Zagreb and Nastavni zavod za javno zdravstvo "Andrija Štampar") - https://ekokartazagreb.stampar.hr/ .

The following device types and data are supported:

- [Weather](#weather) - Current conditions and forecasts
- [Sensor](#sensor) - Current conditions and alerts
- [Air Quality](#air_quality) - Air Quality data

## Installation

There are two options; manual or HACS installation:

*Manual installation*
- Copy `eko_karta_zagreb`  folder in `custom_components` from repository to your Home Assistant configuration `custom_components` folder. Don't copy any other YAML files from repository root not to overwrite your own configuration.

*HACS installation*

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

- Use HACS custom repository (not default) - (https://github.com/kpisacic/EkoKartaZg-home-assistant-custom-component)


## Location Selection

Each platform can determine location in any of following ways:
- by reading configuration parameter `sensor_id` - see (#station_id) for list of currently supported sensor ID's
- by reading configuration parameter `lon` and `lat` of desired location, and then determining closes Eko Karta Zagreb sensor
- by reading home assistant's location, and then determining closes Eko Karta Zagreb sensor

So, minimum configuration is without any named consifuration parameters except platform name.

## Weather

The `eko_karta_zagreb` weather platform populates a weather card with Eko Karta Zagreb current conditions.

To add Eko Karta Zagreb weather to your installation, place `custom_components/eko_karta_zagreb` folder and files in your `configuration` folder of home assistant, and add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
weather:
  - platform: eko_karta_zagreb
    name: EKo Karta Zagreb Maksimir Weather
    station_id: 969
    lon: 16.01
    lat: 45.82
```

- The platform checks for new data every 20 minutes, and the source data is typically updated hourly within 10 minutes after the hour.
- If no name is given, the weather entity will be named `weather.eko_karta_zagreb`.

*Configuration*

- name:
  - description: Name to be used for the entity ID, e.g. `weather.<name>`.
  - required: false
  - type: string
- station_id:
  - description: The station code of a specific weather station to use - see (#station_id)
  - required: false
  - type: string
- lon:
  - description: Longitude of location to use for closest station determination
  - required: false
  - type: float
- lat:
  - description: Latitude of location to use for closest station determination
  - required: false
  - type: float

## Sensor

The `eko_karta_zagreb` sensor platform creates sensors based on Eko Karta Zagreb current conditions.

To add Eko Karta Zagreb sensor to your installation, place `custom_components/eko_karta_zagreb` folder and files in your `configuration` folder of home assistant, and add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: eko_karta_zagreb
    name: EkoZG Maksimir
    station_id: 969
    lon: 16.01
    lat: 45.82
    monitored_conditions:
      - temperature
      - pressure
      - humidity
      - air_quality_index
      - carbon_monoxide
      - nitrogen_monoxide
      - nitrogen_dioxide
      - ozone
      - particulate_matter_0_1
      - particulate_matter_10
      - particulate_matter_2_5
      - sulphur_dioxide
```

- A sensor will be created for each of the following conditions, with a default name like `sensor.<name>_temperature`. If no name is given, the sensor entity will be named `sensor.eko_karta_zagreb_temperature`.
  - `temperature` - The current temperature, in °C.
  - `pressure` - The current air pressure, in kPa.
  - `humidity` - The current humidity, in %.
  - `air_quality_index` - Current air quality index
  - `carbon_monoxide` - Current concentraton of cardon monoxide
  - `nitrogen_monoxide` - Current concentration of nitrogen monoxide
  - `nitrogen_dioxide` - Current concentration of nitrogen dioxide
  - `ozone` - Current ozone concentration
  - `particulate_matter_0_1` - Current concentration of particles <1μm
  - `particulate_matter_10` - Current concentration of particles >10μm
  - `particulate_matter_2_5` - Current concentration of particles 2-5μm
  - `sulphur_dioxide` - Current concentration of sulphur_dioxide

*Configuration*
- name:
  - description: Name to be used for the entity ID, e.g. `sensor.<name>_temperature`.
  - required: false
  - type: string
- station_id:
  - description: The station code of a specific weather station to use - see (#station_id)
  - required: false
  - type: string
- lon:
  - description: Longitude of location to use for closest station determination
  - required: false
  - type: float
- lat:
  - description: Latitude of location to use for closest station determination
  - required: false
  - type: float
- monitored_conditions:
  - description: List of sensors to monitor, create in home assistant
  - required: true
  - type: list or
      - temperature
      - pressure
      - humidity
      - air_quality_index
      - carbon_monoxide
      - nitrogen_monoxide
      - nitrogen_dioxide
      - ozone
      - particulate_matter_0_1
      - particulate_matter_10
      - particulate_matter_2_5
      - sulphur_dioxide

## Air_Quality

The `eko_karta_zagreb` air quality platform creates air quality entity based on Eko Karta Zagreb current conditions and measurements.

To add Eko Karta Zagreb air quality to your installation, place `custom_components/eko_karta_zagreb` folder and files in your `configuration` folder of home assistant, and add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
air_quality:
  - platform: eko_karta_zagreb
    name: EkoZG Maksimir
    station_id: 969
    lon: 16.01
    lat: 45.82
```
If no name is given, the air quality entity will be named `air_quality.eko_karta_zagreb`.

*Configuration*

- name:
  - description: Name to be used for the entity ID, e.g. `air_quality.<name>`.
  - required: false
  - type: string
- station_id:
  - description: The station code of a specific weather station to use - see (#station_id)
  - required: false
  - type: string
- lon:
  - description: Longitude of location to use for closest station determination
  - required: false
  - type: float
- lat:
  - description: Latitude of location to use for closest station determination
  - required: false
  - type: float


## station_id

-  "id": 426,	"name": "Zagreb Mirogojska",
-  "id": 970,	"name": "Zagrebačka avenija-Selska",
-  "id": 973,	"name": "Oranice-Ilica",
-  "id": 969,	"name": "Maksimir",
-  "id": 971,	"name": "Branimirova-Držićeva",
-  "id": 968,	"name": "Sesvete",
-  "id": 422,	"name": "IMI",
-  "id": 974,	"name": "Jadranski most - Selska",
-  "id": 972,	"name": "Savska-Jukićeva",
-  "id": 967,	"name": "IMI Zagreb Ksaverska",
