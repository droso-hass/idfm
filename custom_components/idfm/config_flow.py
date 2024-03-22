"""Adds config flow for IDFM Integration"""
from typing import Any, Dict, Optional

import voluptuous as vol
from aiohttp import ClientSession
from homeassistant import config_entries
from idfm_api import IDFMApi
from idfm_api.dataset import Dataset
from idfm_api.models import TransportType

from .const import (
    CONF_DESTINATION,
    CONF_DIRECTION,
    CONF_EXCLUDE_ELEVATORS,
    CONF_LINE,
    CONF_LINE_NAME,
    CONF_STOP,
    CONF_STOP_NAME,
    CONF_TOKEN,
    CONF_TRANSPORT,
    CONF_NB_ENTITIES,
    DOMAIN,
)

# select transport type > select line > select stop > select direction


class IDFMFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for IDFM."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._session = ClientSession()
        self._client = None
        self.data = {}

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle a flow initialized by the user."""
        if user_input is None:
            user_input = {}

        if CONF_TOKEN in user_input and CONF_EXCLUDE_ELEVATORS in user_input:
            self.data[CONF_TOKEN] = user_input[CONF_TOKEN]
            self.data[CONF_EXCLUDE_ELEVATORS] = user_input[CONF_EXCLUDE_ELEVATORS]
            self._client = IDFMApi(self._session, user_input[CONF_TOKEN], timeout=300)
            return await self.async_step_transport()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_TOKEN): str,
                vol.Required(CONF_EXCLUDE_ELEVATORS, default=True): bool,
            }),
            errors={},
        )

    async def async_step_transport(self, user_input: Optional[Dict[str, Any]] = None):
        """Second step in config flow to select a transport mode"""
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
            step_id="transport",
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
        """Thrid step in config flow to select the transport line"""
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
        """Fourth step in config flow to select a starting stop."""
        if user_input is None:
            user_input = {}

        stops = await self._client.get_stops(self.data[CONF_LINE])

        if CONF_STOP in user_input:
            for s in stops:
                if s.name + " - " + s.city == user_input[CONF_STOP]:
                    self.data[CONF_STOP] = s.exchange_area_id or s.stop_id
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
        """Fifth step in config flow to select a specific direction/destination"""
        if user_input is None:
            user_input = {}

        if CONF_DIRECTION in user_input:
            self.data[CONF_DIRECTION] = None
            self.data[CONF_DESTINATION] = None
            if user_input[CONF_DIRECTION][0:3] == "Dir":
                self.data[CONF_DIRECTION] = user_input[CONF_DIRECTION][5:]
            elif user_input[CONF_DIRECTION][0:3] == "Des":
                self.data[CONF_DESTINATION] = user_input[CONF_DIRECTION][6:]
            return await self.async_step_entities()

        directions = await self._client.get_directions(
            self.data[CONF_STOP],
            line_id=self.data[CONF_LINE],
        )
        destinations = await self._client.get_destinations(
            self.data[CONF_STOP],
            line_id=self.data[CONF_LINE],
        )
        directions = (
            ["Dir: " + x for x in directions if x is not None]
            + ["Dest: " + x for x in destinations if x is not None]
            + ["any"]
        )

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

    async def async_step_entities(self, user_input: Optional[Dict[str, Any]] = None):
        """Fifth step in config flow to select a the number of entities."""
        if user_input is None:
            user_input = {}

        if CONF_NB_ENTITIES in user_input:
            self.data[CONF_NB_ENTITIES] = user_input[CONF_NB_ENTITIES]         
            return self.async_create_entry(
                title=self.data[CONF_LINE_NAME] + " - " + self.data[CONF_STOP_NAME],
                data=self.data,
            )

        return self.async_show_form(
            step_id="entities",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NB_ENTITIES,
                        default=4,
                    ): vol.Range(min=1, max=50)
                }
            ),
            errors={},
        )