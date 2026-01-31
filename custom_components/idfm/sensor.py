"""Sensor platform for IDFM Integration"""
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.util.dt import as_local

from .const import (
    ATTR_TRAFFIC_AT_STOP,
    ATTR_TRAFFIC_DESTINATION,
    ATTR_TRAFFIC_DETAILS,
    ATTR_TRAFFIC_DIRECTION,
    ATTR_TRAFFIC_PLATFORM,
    ATTR_TRAFFIC_STATUS,
    CONF_DESTINATION,
    CONF_DIRECTION,
    CONF_STOP_NAME,
    CONF_NB_ENTITIES,
    DATA_TRAFFIC,
    DOMAIN,
    ICON,
)
from .entity import IDFMEntity

async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [ 
            IDFMTimeSensor(coordinator, entry, i) 
            for i in range(entry.data.get(CONF_NB_ENTITIES) or 4)
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
            + (
                self.config_entry.data[CONF_DIRECTION]
                or self.config_entry.data[CONF_DESTINATION]
                or "any"
            )
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
        if self.coordinator.data is not None and self.num < len(
            self.coordinator.data[DATA_TRAFFIC]
        ):
            return as_local(self.coordinator.data[DATA_TRAFFIC][self.num].schedule)
        return None

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
        if self.coordinator.data is not None and self.num < len(
            self.coordinator.data[DATA_TRAFFIC]
        ):
            self._attrs.update(
                {
                    ATTR_TRAFFIC_DETAILS: self.coordinator.data[DATA_TRAFFIC][
                        self.num
                    ].note,
                    ATTR_TRAFFIC_DESTINATION: self.coordinator.data[DATA_TRAFFIC][
                        self.num
                    ].destination_name,
                    ATTR_TRAFFIC_DIRECTION: self.coordinator.data[DATA_TRAFFIC][
                        self.num
                    ].direction,
                    ATTR_TRAFFIC_AT_STOP: self.coordinator.data[DATA_TRAFFIC][
                        self.num
                    ].at_stop,
                    ATTR_TRAFFIC_PLATFORM: self.coordinator.data[DATA_TRAFFIC][
                        self.num
                    ].platform,
                    ATTR_TRAFFIC_STATUS: self.coordinator.data[DATA_TRAFFIC][
                        self.num
                    ].status,
                }
            )
        return self._attrs
