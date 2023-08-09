"""Binary sensor platform for IDFM Integration"""
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.util.dt import as_local, now

from .const import (
    ATTR_INFO_CATEGORY,
    ATTR_INFO_CAUSE,
    ATTR_INFO_DESC,
    ATTR_INFO_EFFECT,
    ATTR_INFO_END_TIME,
    ATTR_INFO_SEVERITY,
    ATTR_INFO_START_TIME,
    ATTR_INFO_TYPE,
    CONF_LINE_NAME,
    CONF_STOP_NAME,
    DATA_INFO,
    DOMAIN,
)
from .entity import IDFMEntity


async def async_setup_entry(
    hass: HomeAssistant,
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
        self.is_on = False
        self.extra_state_attributes = {}

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

    @callback
    def _handle_coordinator_update(self) -> None:
        if self.coordinator.data is not None:
            lst = []
            dt = now()
            # keep only current events
            for i in self.coordinator.data[DATA_INFO]:
                for t in i.periods:
                    if as_local(t[0]) <= dt and dt <= as_local(t[1]):
                        lst.append(i)

            if len(lst) > 0:
                self.is_on = True

                # sort by severity
                lst.sort(key=lambda x: x.severity)
                data = lst[0]
                period = None
                for t in data.periods:
                    if as_local(t[0]) <= dt and dt <= as_local(t[1]):
                        period = t
                        break

                self.extra_state_attributes.update(
                    {
                        ATTR_INFO_DESC: data.message,
                        ATTR_INFO_END_TIME: as_local(period[1]),
                        ATTR_INFO_SEVERITY: data.severity,
                        ATTR_INFO_START_TIME: as_local(period[0]),
                        ATTR_INFO_TYPE: data.type,
                        ATTR_INFO_CATEGORY: data.category,
                        ATTR_INFO_CAUSE: data.cause,
                        ATTR_INFO_EFFECT: data.effect,
                    }
                )
            else:
                self.is_on = False

                self.extra_state_attributes.update(
                    {
                        ATTR_INFO_DESC: "",
                        ATTR_INFO_END_TIME: None,
                        ATTR_INFO_SEVERITY: 0,
                        ATTR_INFO_START_TIME: None,
                        ATTR_INFO_TYPE: "",
                        ATTR_INFO_CATEGORY: "",
                        ATTR_INFO_CAUSE: "",
                        ATTR_INFO_EFFECT: "",
                    }
                )
