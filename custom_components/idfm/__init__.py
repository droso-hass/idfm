"""
Custom integration for Ile de france mobilite for Home Assistant.
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core_config import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from idfm_api import IDFMApi
from idfm_api.models import TransportType

from .const import (
    CONF_DESTINATION,
    CONF_DIRECTION,
    CONF_EXCLUDE_ELEVATORS,
    CONF_LINE,
    CONF_STOP,
    CONF_TOKEN,
    CONF_TRANSPORT,
    DATA_INFO,
    DATA_TRAFFIC,
    DOMAIN,
    STARTUP_MESSAGE,
)

SCAN_INTERVAL = timedelta(minutes=3)
PLATFORMS = [Platform.BINARY_SENSOR, Platform.CALENDAR, Platform.SENSOR]

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    transport_type = entry.data.get(CONF_TRANSPORT)
    line_id = entry.data.get(CONF_LINE)
    direction = entry.data.get(CONF_DIRECTION)
    destination = entry.data.get(CONF_DESTINATION)
    stop_area_id = entry.data.get(CONF_STOP)
    exclude_elevators = entry.data.get(CONF_EXCLUDE_ELEVATORS) or True

    session = async_get_clientsession(hass)
    client = IDFMApi(session, entry.data.get(CONF_TOKEN), timeout=300)

    coordinator = IDFMDataUpdateCoordinator(
        hass,
        client=client,
        transport_type=transport_type,
        line_id=line_id,
        stop_area_id=stop_area_id,
        destination=destination,
        direction=direction,
        exclude_elevators=exclude_elevators,
    )
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    platforms_to_setup = []

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            platforms_to_setup.append(platform)

    if platforms_to_setup:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setups(entry, platforms_to_setup)
        )

    entry.add_update_listener(async_reload_entry)

    return True

class IDFMDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: IDFMApi,
        transport_type: str,
        line_id: str,
        stop_area_id: str,
        direction: str,
        destination: str,
        exclude_elevators: bool,
    ) -> None:
        """Initialize."""
        self.api = client
        self.transport_type = transport_type
        self.line_id = line_id
        self.stop_area_id = stop_area_id
        self.direction = direction
        self.destination = destination
        self.exclude_elevators = exclude_elevators
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def async_update(self):
        await self._async_update_data()

    async def _async_update_data(self):
        """Update data via library."""
        try:
            d = datetime.now()
            # skip updating for tram, train and trams between 1h30 and 5h30
            if self.transport_type not in [
                TransportType.TRAIN,
                TransportType.METRO,
                TransportType.TRAM,
            ] or (
                (d.hour == 1 and d.minute < 30)
                or (d.hour < 1 or d.hour > 5)
                or (d.hour == 5 and d.minute >= 30)
            ):
                tr = await self.api.get_traffic(
                    self.stop_area_id, self.destination, self.direction, self.line_id
                )
                # Filter past schedules
                utcd = datetime.utcnow().replace(tzinfo=timezone.utc)
                sorted_tr = sorted(
                    filter(
                        lambda x: (x.schedule is not None and x.schedule > utcd), tr
                    ),
                    key=lambda x: x.schedule,
                )
                inf = await self.api.get_line_reports(
                    self.line_id, self.exclude_elevators
                )
                return {DATA_TRAFFIC: sorted_tr, DATA_INFO: inf}
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
