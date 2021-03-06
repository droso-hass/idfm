"""Binary sensor platform for IDFM Integration"""
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)

from .const import (
    CONF_LINE_NAME,
    CONF_STOP_NAME,
    DOMAIN,
    DATA_INFO,
    ATTR_INFO_DESC,
    ATTR_INFO_END_TIME,
    ATTR_INFO_SEVERITY,
    ATTR_INFO_START_TIME,
    ATTR_INFO_TYPE,
)
from .entity import IDFMEntity
from datetime import datetime


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IDFMBinarySensor(coordinator, entry)], True)


class IDFMBinarySensor(IDFMEntity, BinarySensorEntity):
    """IDFM binary_sensor class."""

    def __init__(
        self,
        coordinator,
        config_entry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self._attrs = {}

    @property
    def name(self):
        """Return the name of the binary_sensor."""
        return (
            "idfm_"
            + self.config_entry.data[CONF_LINE_NAME]
            + " ["
            + self.config_entry.data[CONF_STOP_NAME]
            + "]"
        )

    @property
    def device_class(self):
        """Return the class of this binary_sensor."""
        return BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        dt = datetime.now()
        for i in self.coordinator.data[DATA_INFO]:
            if dt >= i.start_time and dt <= i.end_time:
                return True
        return False

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""

        lst = []
        dt = datetime.now()
        for i in self.coordinator.data[DATA_INFO]:
            if i.start_time >= dt or dt <= i.end_time:
                lst.append(i)

        if len(lst) == 0:
            lst = self.coordinator.data[DATA_INFO]

        lst.sort(key=lambda x: x.severity.value)

        if len(lst) > 0:
            data = lst[-1]
            self._attrs.update(
                {
                    ATTR_INFO_DESC: data.message,
                    ATTR_INFO_END_TIME: data.end_time,
                    ATTR_INFO_SEVERITY: data.severity.value,
                    ATTR_INFO_START_TIME: data.start_time,
                    ATTR_INFO_TYPE: data.type,
                }
            )
        else:
            self._attrs.update(
                {
                    ATTR_INFO_DESC: "",
                    ATTR_INFO_END_TIME: None,
                    ATTR_INFO_SEVERITY: 0,
                    ATTR_INFO_START_TIME: None,
                    ATTR_INFO_TYPE: "",
                }
            )

        return self._attrs
