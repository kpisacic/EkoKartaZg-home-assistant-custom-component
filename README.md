# EkoKartaZg-home-assistant-custom-component
Home Assistant Custom Components for "Eko Karta Zagreb" service (Grad Zagreb and Nastavni zavod za javno zdravstvo)

---
title: "Eko Karta Zagreb"
description: "Weather data from Eko Karta Zagreb service."
logo: ekokartazagreb.svg
ha_category:
  - Weather
  - Sensor
  - Air_Quality
ha_release: 0.99
ha_iot_class: Cloud Polling
---

The `eko_karta_zagreb` weather platform provide meteorological data for Eko Karta Zagreb service (Grad Zagreb and Nastavni zavod za javno zdravstvo) - https://ekokartazagreb.stampar.hr/ .

The following device types and data are supported:

- [Weather](#weather) - Current conditions and forecasts
- [Sensor](#sensor) - Current conditions and alerts
- [Air Quality](#air_quality) - Air Quality data

## Location Selection

Each platform does not choose automatically which weather station's data to use. Selection of different identifiers is under configuration section of this document. Current version does not validate nor enforces configuration choices, but this is down the roadmap.

For each platform, the location to use is determined according to the following list:

  - [station_id](#station_id) -  ID of the station for current data (mandatory)

## Weather

The `eko_karta_zagreb` weather platform populates a weather card with Eko Karta Zagreb current conditions.
To add Eko Karta Zagreb weather to your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
weather:
  - platform: eko_karta_zagreb
    name: EKo Karta Zagreb Maksimir Weather
    station_id: 969
```

- The platform checks for new data every 20 minutes, and the source data is typically updated hourly within 10 minutes after the hour.
- If no name is given, the weather entity will be named `weather.dhmz`.

*Configuration*

- name:
  - description: Name to be used for the entity ID, e.g. `weather.<name>`.
  - required: false
  - type: string
- station_id:
  - description: The station code of a specific weather station to use - see (#station_name)
  - required: true
  - type: string

## Sensor

The `dhmz` sensor platform creates sensors based on DHMZ current conditions data and daily forecasts.

To add DHMZ weather to your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: dhmz
    name: DHMZ Sensor Maksimir
    station_name: Zagreb-Maksimir
    forecast_region_name: Zagreb
    forecast_text: zg_text
    forecast_station_name: Zagreb_Maksimir
    monitored_conditions:
      - temperature
      - pressure
      - pressure_tendency
      - humidity
      - wind_speed
      - wind_bearing
      - condition
      - precipitation
      - forecast_text_today
      - forecast_text_tommorow
```

- A sensor will be created for each of the following conditions, with a default name like `sensor.<name>_temperature`:     
    - `temperature` - The current temperature, in ÂşC.
    - `pressure` - The current air pressure, in kPa.
    - `pressure_tendency` - The current air pressure tendency, e.g. "+0.5" in last hour.
    - `humidity` - The current humidity, in %.
    - `condition` - A brief text statement of the current weather conditions, e.g. "Sunny".
    - `wind_speed` - The current sustained wind speed, in km/h.
    - `wind_bearing` - The current cardinal wind direction, e.g. "SSW".
    - `precipitation` - precipitation in last 24 hours, in mm.
    - `forecast_text_today` - A textual description of today's forecast
    - `forecast_text_tommorow` - A textual description of tommorow's forecast

*Configuration*
- name:
  - description: Name to be used for the entity ID, e.g. `sensor.<name>_temperature`.
  - required: false
  - type: string
- station_name:
  - description: The station code of a specific weather station to use - see (#station_name)
  - required: true
  - type: string
- forecast_region_name:
  - description: The forecase region_name - see (#forecast_region_name)
  - required: true
  - type: string
- forecast_text:
  - description: The forecast text identifier - see ##forecast_text
  - required: true
  - type: string
- forecast_station_name:
  - description: The forecast station name - see ##forecast_station_name
  - required: true
  - type: string
- monitored_conditions:
  - description: List of sensors to monitor, create in home assistant
  - required: true
  - type: list or
      - temperature
      - pressure
      - pressure_tendency
      - humidity
      - wind_speed
      - wind_bearing
      - condition
      - precipitation
      - forecast_text_today
      - forecast_text_tommorow

## Camera

The `dhmz` camera platform displays DHMZ [radar imagery].

To add Environment Canada radar imagery to your installation, add the desired lines from the following example to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
camera:
  - platform: dhmz
    name: DHMZ Radar
```

- If no name is given, the camera entity will be named `camera.dhmz`.

*Configuration*

- name:
  - description: Name to be used for the entity ID, e.g. `camera.<name>`.
  - required: false
  - type: string


## station_id

