"""Adds config flow for IDFM Integration"""
from typing import Any, Dict, Optional
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from aiohttp import ClientSession


from idfm_api import IDFMApi
from idfm_api.models import TransportType
from .const import (
    CONF_LINE,
    CONF_LINE_NAME,
    CONF_DIRECTION,
    CONF_STOP,
    CONF_STOP_NAME,
    CONF_TRANSPORT,
    DOMAIN,
)

# select transport type > select line > select stop > select direction

class IDFMFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for IDFM."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        # self._session = async_get_clientsession(self.hass)
        self._session = ClientSession()
        self._client = IDFMApi(self._session)
        self.data = {}

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle a flow initialized by the user."""
        if user_input is None:
            user_input = {}

        if CONF_TRANSPORT in user_input:
            tr = {}
            for i in list(TransportType):
                tr[i.name] = i
            self.data[CONF_TRANSPORT] = TransportType(tr[user_input[CONF_TRANSPORT]])
            return await self.async_step_line()

        transports = [t.name for t in list(TransportType)]

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_TRANSPORT,
                        default=user_input.get(CONF_TRANSPORT) or transports[0],
                    ): vol.In(sorted(transports))
                }
            ),
            errors={},
        )

    async def async_step_line(self, user_input: Optional[Dict[str, Any]] = None):
        """Second step in config flow to add a repo to watch."""
        if user_input is None:
            user_input = {}

        lines = await self._client.get_lines(self.data[CONF_TRANSPORT])

        if CONF_LINE in user_input:
            for l in lines:
                if l.name == user_input[CONF_LINE]:
                    self.data[CONF_LINE] = l.id
                    self.data[CONF_LINE_NAME] = l.name
                    return await self.async_step_stop()

        names = [l.name for l in lines]

        return self.async_show_form(
            step_id="line",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_LINE,
                        default=user_input.get(CONF_LINE) or names[0],
                    ): vol.In(sorted(names))
                }
            ),
            errors={},
        )

    async def async_step_stop(self, user_input: Optional[Dict[str, Any]] = None):
        """Third step in config flow to add a repo to watch."""
        if user_input is None:
            user_input = {}

        stops = await self._client.get_stops(self.data[CONF_LINE])

        if CONF_STOP in user_input:
            for s in stops:
                if s.name  + " - " + s.city == user_input[CONF_STOP]:
                    self.data[CONF_STOP] = s.id
                    self.data[CONF_STOP_NAME] = s.name + " - " + s.city
                    return await self.async_step_direction()

        names = [s.name + " - " + s.city for s in stops]

        return self.async_show_form(
            step_id="stop",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_STOP,
                        default=user_input.get(CONF_STOP) or names[0],
                    ): vol.In(sorted(names))
                }
            ),
            errors={},
        )

    async def async_step_direction(self, user_input: Optional[Dict[str, Any]] = None):
        """Fourth step in config flow to add a repo to watch."""
        if user_input is None:
            user_input = {}

        if CONF_DIRECTION in user_input:
            self.data[CONF_DIRECTION] = (
                None
                if user_input[CONF_DIRECTION] == "any"
                else user_input[CONF_DIRECTION]
            )
            return self.async_create_entry(
                title=self.data[CONF_LINE_NAME] + " - " + self.data[CONF_STOP_NAME],
                data=self.data,
            )

        directions = await self._client.get_directions(
            self.data[CONF_LINE], self.data[CONF_STOP]
        )
        directions = [x for x in directions if x is not None] + ["any"]

        return self.async_show_form(
            step_id="direction",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DIRECTION,
                        default=user_input.get(CONF_DIRECTION) or directions[0],
                    ): vol.In(sorted(directions))
                }
            ),
            errors={},
        )