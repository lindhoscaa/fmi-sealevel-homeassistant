import voluptuous as vol

from homeassistant.const import CONF_NAME

from homeassistant import config_entries, core

from . import base_unique_id

from .const import _LOGGER, CONF_FMISID

from .FMIMareoLibrary import get_sea_level_data

async def validate_user_config(hass: core.HomeAssistant, data):
    fmisid = data[CONF_FMISID]
    _LOGGER.info(f"Validating fmisid {fmisid}")
    try:
        seaLevelData = await hass.async_add_executor_job(get_sea_level_data, fmisid)
    except:
        return False
    _LOGGER.info(f"Got initial sealevel data: {seaLevelData}")

    try:
        latest_sea_level = seaLevelData["CurrentMW"]
        return True
    except:
        return False


class ConfigFlowHandler(config_entries.ConfigFlow, domain="fmi-sealevel"):
    """Config flow handler for FMI."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle user step."""
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(base_unique_id(user_input[CONF_FMISID]))
            self._abort_if_unique_id_configured()

            valid = await validate_user_config(self.hass, user_input)

            if valid:
                _LOGGER.debug(f"Input validated. Creating entry.")
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )
            else:
                _LOGGER.debug(f"Input not validated. Showing form.")
            errors["fmi-sealevel"] = valid["err"]

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="name"): str,
                vol.Required(CONF_FMISID, default=134253): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
