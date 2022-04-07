"""Sensor platform for IDFM Integration"""
from .const import DEFAULT_NAME, DOMAIN, ICON, DATA_TRAFFIC
from .entity import IDFMEntity

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass


"""
async def async_setup_entry(hass, entry, async_add_devices):
    coordinator = hass.data[DOMAIN]
    async_add_devices([IDFMTimeSensor(coordinator, entry)])
"""

async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [IDFMTimeSensor(coordinator, entry, 0), IDFMTimeSensor(coordinator, entry, 1), IDFMTimeSensor(coordinator, entry, 2)], True
    )



class IDFMTimeSensor(IDFMEntity, SensorEntity):
    """IDFM Timestamp Sensor class."""
    def __init__(self, coordinator, config_entry, num):
        super().__init__(coordinator, config_entry)
        self.num = num


    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + str(self.num)

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_next_{self.num}"
        
    @property
    def device_class(self):
        """Return the class of this binary_sensor."""
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
