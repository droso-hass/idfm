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
    IDFM_API_LINK
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
        static = [f"<a href='{v}'>{k}</a>" for k,v in IDFM_DB_SOURCES.items()]
        attribution = f"""
        Données statiques issues des datasets {static}
        Données dynamiques mises a disposition par <a href='{IDFM_API_LINK}'>PRIM</a>
        Le tout sous licence <a href='{IDFM_DB_LICENCE_LINK}'>{IDFM_DB_LICENCE}</a>
        """
        return {
            "attribution": attribution,
            "id": str(self.coordinator.data.get("id")),
            "integration": DOMAIN,
        }
