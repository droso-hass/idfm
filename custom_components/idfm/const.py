"""Constants for IDFM """
# Base component constants
NAME = "Ile de france mobilités"
DOMAIN = "idfm"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "1.1"

ATTRIBUTION = "Data provided by https://me-deplacer.iledefrance-mobilites.fr"
ISSUE_URL = "https://github.com/droso-hass/idfm/issues"

# Icons
ICON = "mdi:train"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
PLATFORMS = [BINARY_SENSOR, SENSOR]


# Configuration and options
CONF_TRANSPORT = "transport_mode"
CONF_LINE = "transport_line"
CONF_LINE_NAME = "transport_line_name"
CONF_STOP = "stop_area"
CONF_STOP_NAME = "stop_area_name"
CONF_DIRECTION = "direction"

DATA_TRAFFIC = "traffic"
DATA_INFO = "info"

# Defaults
ATTR_INFO_SEVERITY = "severity"
ATTR_INFO_DESC = "description"
ATTR_INFO_TYPE = "type"
ATTR_INFO_START_TIME = "start_time"
ATTR_INFO_END_TIME = "end_time"

ATTR_TRAFFIC_FORWARD = "forward"
ATTR_TRAFFIC_DIRECTION = "direction"


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
