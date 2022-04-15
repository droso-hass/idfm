"""IDFMEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_DIRECTION,
    CONF_LINE,
    CONF_LINE_NAME,
    CONF_STOP,
    DOMAIN,
    NAME,
    VERSION,
    CONF_STOP_NAME,
)


class IDFMEntity(CoordinatorEntity):
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id

    @property
    def device_info(self):
        id = (
            self.config_entry.data[CONF_LINE]
            + self.config_entry.data[CONF_STOP]
            + (self.config_entry.data[CONF_DIRECTION] or "any")
        )
        return {
            "identifiers": {(DOMAIN, id)},
            "name": self.config_entry.data[CONF_LINE_NAME] + " - " + self.config_entry.data[CONF_STOP_NAME]
            + " -> "
            + (self.config_entry.data[CONF_DIRECTION] or "any"),
            "model": VERSION,
            "manufacturer": NAME,
        }

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": str(self.coordinator.data.get("id")),
            "integration": DOMAIN,
        }
