"""Constants for the FMI Weather and Sensor integrations."""
from datetime import timedelta

import logging

_LOGGER = logging.getLogger(__package__)
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

DOMAIN = "fmi-sealevel"
NAME = "FMI-SeaLevel"
MANUFACTURER = "Lindh Technologies"

CONF_FMISID = "station_fmisid"
ATTRIBUTION = "Lindh Technologies, Data provided by FMI"
API_TIMEOUT = 60


COORDINATOR = "coordinator"
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=1)
UNDO_UPDATE_LISTENER = "undo_update_listener"

