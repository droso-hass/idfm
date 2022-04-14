"""
Custom integration for Ile de france mobilite for Home Assistant.
"""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from idfm_api import IDFMApi
from .const import (
    CONF_LINE,
    CONF_DIRECTION,
    CONF_STOP,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
    DATA_TRAFFIC,
    DATA_INFO,
)

SCAN_INTERVAL = timedelta(seconds=60)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    line_id = entry.data.get(CONF_LINE)
    direction = entry.data.get(CONF_DIRECTION)
    stop_area_id = entry.data.get(CONF_STOP)

    session = async_get_clientsession(hass)
    client = IDFMApi(session)

    coordinator = IDFMDataUpdateCoordinator(
        hass,
        client=client,
        line_id=line_id,
        stop_area_id=stop_area_id,
        direction=direction,
    )
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )

    entry.add_update_listener(async_reload_entry)
    return True


class IDFMDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: IDFMApi,
        line_id: str,
        stop_area_id: str,
        direction: str,
    ) -> None:
        """Initialize."""
        self.api = client
        self.line_id = line_id
        self.stop_area_id = stop_area_id
        self.direction = direction
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def async_update(self):
        await self._async_update_data()

    async def _async_update_data(self):
        """Update data via library."""
        try:
            tr = await self.api.get_traffic(
                self.line_id, self.stop_area_id, self.direction
            )
            inf = await self.api.get_infos(self.line_id)
            return {DATA_TRAFFIC: tr, DATA_INFO: inf}
        except Exception as exception:
            raise UpdateFailed() from exception


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
