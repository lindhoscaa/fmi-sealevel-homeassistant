from async_timeout import timeout
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .FMIMareoLibrary import get_sea_level_data

from .const import (
    _LOGGER,
    CONF_FMISID,
    COORDINATOR,
    DOMAIN,
    MIN_TIME_BETWEEN_UPDATES,
    API_TIMEOUT,
    UNDO_UPDATE_LISTENER,
)

PLATFORMS = ["sensor"]


def base_unique_id(fmisid):
    """Return unique id for entries in configuration."""
    return f"{fmisid}"


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up configured FMI."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, config_entry) -> bool:
    """Set up FMI as config entry."""
    websession = async_get_clientsession(hass)

    coordinator = FMIDataUpdateCoordinator(hass, websession, config_entry)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    undo_listener = config_entry.add_update_listener(update_listener)

    hass.data[DOMAIN][config_entry.entry_id] = {
        COORDINATOR: coordinator,
        UNDO_UPDATE_LISTENER: undo_listener,
    }

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    return True


async def async_unload_entry(hass, config_entry):
    for component in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(config_entry, component)

    hass.data[DOMAIN][config_entry.entry_id][UNDO_UPDATE_LISTENER]()
    hass.data[DOMAIN].pop(config_entry.entry_id)

    return True


async def update_listener(hass, config_entry):
    """Update FMI listener."""
    await hass.config_entries.async_reload(config_entry.entry_id)


class FMIMareoStruct:
    def __init__(self, current_mw=None, forecast_mw=None, observations_mw=None, current_n2000=None, forecast_n2000=None, observations_n2000=None):
        """Initialize the sea height data."""
        self.current_mw = current_mw
        self.forecast_mw = forecast_mw
        self.observations_mw = observations_mw
        self.current_n2000 = current_n2000
        self.forecast_n2000 = forecast_n2000
        self.observations_n2000 = observations_n2000



class FMIDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching FMI data API."""

    def __init__(self, hass, session, config_entry):
        """Initialize."""

        _LOGGER.info(f"Using FMISID: {config_entry.data[CONF_FMISID]}")

        self._hass = hass
        self.fmisid = config_entry.data[CONF_FMISID]
        self.unique_id = str(self.fmisid)

        _LOGGER.debug(
            "FMI: Data will be updated every %s min", MIN_TIME_BETWEEN_UPDATES
        )

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=MIN_TIME_BETWEEN_UPDATES
        )

    async def _async_update_data(self):
        """Update data via Open API."""

        # Update mareo data
        def update_mareo_data():
            """Get the latest mareograph forecast data from FMI and update the states."""

            _LOGGER.debug(f"FMI: mareo started")

            sea_level_data = get_sea_level_data(self.fmisid)
            _LOGGER.debug(f"FMI: mareo sea_level_data: {sea_level_data}")


            ##sealevel_tuple_list = get_sea_level_data(self.fmisid)

            mareo_op = FMIMareoStruct(current_mw=sea_level_data["CurrentMW"], forecast_mw=sea_level_data["Forecasts"]["SeaLevelMW"], observations_mw=sea_level_data["Observations"]["SeaLevelMW"], current_n2000=sea_level_data["CurrentN2000"], forecast_n2000=sea_level_data["Forecasts"]["SeaLevelN2000"], observations_n2000=sea_level_data["Observations"]["SeaLevelN2000"])
            self.mareo_data = mareo_op
            if len(sea_level_data["Forecasts"]["SeaLevelMW"]) > 0:
                _LOGGER.debug(
                    "FMI: Mareo_data updated with data: %s %s",

                )
            else:
                _LOGGER.debug("FMI: Mareo_data not updated. No data available!")

            _LOGGER.debug(f"FMI: mareo ended")
            return

        try:
            async with timeout(API_TIMEOUT):
                await self._hass.async_add_executor_job(update_mareo_data)
                _LOGGER.debug("FMI: Mareograph sea level data updated!")

        except error as error:
            raise UpdateFailed(error) from error
        return {}
