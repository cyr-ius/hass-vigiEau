# VigiEau — Water consumption monitoring for Home Assistant

This custom integration for [Home Assistant](https://www.home-assistant.io/) integrates the French public service [VigiEau](https://vigieau.gouv.fr/) to monitor your household water consumption.

![downloads](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.vigieau.total)

## Features

- Sensors: daily, monthly and yearly water consumption.
- Alerts: notifications for threshold breaches or detected anomalies.
- Diagnostics: access to historical data and consumption statistics.
- Compatibility: works with meters supported by the VigiEau service.

## Installation

1. Install via HACS:
   - Open HACS → Integrations → Explore & Add.
   - Add the repository `cyr-ius/hass-vigiEau` to HACS.
   - Search for "VigiEau" and install the integration.

     [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=cyr-ius&repository=hass-heatzy&category=integration)

   - Restart Home Assistant after installation.

2. Manual install:
   - Copy the integration folder to `custom_components/hass-vigiEau`.
   - Restart Home Assistant.
3. Add the integration:
   - Go to Configuration → Integrations → Add Integration and search for "VigiEau".
   - Follow the configuration flow to connect your VigiEau account.

   [![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=vigieau)

## Configuration

- During first setup, provide your VigiEau account credentials to access meter data.
- Configure alert thresholds and select which sensors to enable.
- The integration uses Home Assistant's configuration flow (no YAML required).

## Notes

- Data is updated automatically according to the VigiEau service update frequency.
- Alerts and diagnostics are available in the Home Assistant UI.

## Support

For questions or feature requests, see the project documentation or open an issue on the GitHub repository.

---

_VigiEau is a public service that helps users monitor their water consumption and receive alerts in case of leaks or abnormal usage._
