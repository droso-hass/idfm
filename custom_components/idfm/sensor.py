"""Sensor platform for IDFM Integration"""
from .const import (
    CONF_DIRECTION,
    CONF_STOP_NAME,
    DOMAIN,
    ICON,
    DATA_TRAFFIC,
    ATTR_TRAFFIC_FORWARD,
    ATTR_TRAFFIC_DIRECTION,
)
from .entity import IDFMEntity

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            IDFMTimeSensor(coordinator, entry, 0),
            IDFMTimeSensor(coordinator, entry, 1),
            IDFMTimeSensor(coordinator, entry, 2),
        ],
        True,
    )


class IDFMTimeSensor(IDFMEntity, SensorEntity):
    """IDFM Timestamp Sensor class."""

    def __init__(self, coordinator, config_entry, num):
        super().__init__(coordinator, config_entry)
        self.num = num
        self._attrs = {}

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + str(self.num)

    @property
    def name(self):
        """Return the name of the sensor."""
        return (
            "idfm_"
            + self.config_entry.data[CONF_STOP_NAME]
            + " -> "
            + self.config_entry.data[CONF_DIRECTION]
            + " #"
            + str(self.num)
        )

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return SensorDeviceClass.TIMESTAMP

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.num < len(self.coordinator.data[DATA_TRAFFIC]):
            return self.coordinator.data[DATA_TRAFFIC][self.num].schedule

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def device_class(self):
        """Return de device class of the sensor."""
        return "timestamp"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if self.num < len(self.coordinator.data[DATA_TRAFFIC]):
            self._attrs.update(
                {
                    ATTR_TRAFFIC_FORWARD: self.coordinator.data[DATA_TRAFFIC][
                        self.num
                    ].forward,
                    ATTR_TRAFFIC_DIRECTION: self.coordinator.data[DATA_TRAFFIC][
                        self.num
                    ].direction,
                }
            )
        return self._attrs