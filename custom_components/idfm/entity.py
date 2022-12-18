"""IDFMEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DIRECTION,
    CONF_LINE,
    CONF_LINE_NAME,
    CONF_STOP,
    DOMAIN,
    NAME,
    VERSION,
    CONF_STOP_NAME,
)

from idfm_api.attribution import (
    IDFM_DB_LICENCE,
    IDFM_DB_LICENCE_LINK,
    IDFM_DB_SOURCES,
    IDFM_API_LINK,
    IDFM_API_LICENCE,
    IDFM_API_LICENCE_LINK
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
    def attribution(self) -> str:
        """Return the attribution."""
        static = "[" + ", ".join(IDFM_DB_SOURCES.values()) + "]"
        return f"Static Data: {static} under {IDFM_DB_LICENCE}: {IDFM_DB_LICENCE_LINK} - API provided by PRIM: {IDFM_API_LINK} under {IDFM_API_LICENCE}: {IDFM_API_LICENCE_LINK}"

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            "id": str(self.coordinator.data.get("id")),
            "integration": DOMAIN,
        }
