"""IDFMEntity class"""
from __future__ import annotations
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DIRECTION,
    CONF_LINE,
    CONF_LINE_NAME,
    CONF_STOP,
    CONF_STOP_NAME,
    DOMAIN,
    NAME,
    VERSION,
    ATTRIBUTION_COMPACT,
    LICENSE_URL,
)


class IDFMEntity(CoordinatorEntity):
    """Base entity for the IDFM integration."""
    _attr_attribution = ATTRIBUTION_COMPACT
    _attr_has_entity_name = True
    
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_extra_state_attributes = {
            "integration": DOMAIN,
        }

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id

    @property
    def device_info(self):
        dev_id = (
            self.config_entry.data[CONF_LINE]
            + self.config_entry.data[CONF_STOP]
            + (self.config_entry.data[CONF_DIRECTION] or "any")
        )
        return {
            "identifiers": {(DOMAIN, dev_id)},
            "name": self.config_entry.data[CONF_LINE_NAME]
            + " - "
            + self.config_entry.data[CONF_STOP_NAME]
            + " -> "
            + (self.config_entry.data[CONF_DIRECTION] or "any"),
            "model": VERSION,
            "manufacturer": NAME,
            "configuration_url": LICENSE_URL,
        }

