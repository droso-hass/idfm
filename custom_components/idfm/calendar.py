import datetime

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant, callback
from homeassistant.util.dt import as_local, now

from .const import CONF_LINE_NAME, CONF_STOP_NAME, DOMAIN, DATA_INFO
from .entity import IDFMEntity


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    """Setup calendar platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IDFMCalendar(coordinator, entry)], True)


class IDFMCalendar(IDFMEntity, CalendarEntity):
    def __init__(
        self,
        coordinator,
        config_entry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self._events = []

    @property
    def name(self):
        """Return the name of the calendar."""
        return (
            "idfm_"
            + self.config_entry.data[CONF_LINE_NAME]
            + " ["
            + self.config_entry.data[CONF_STOP_NAME]
            + "] Calendar"
        )

    @property
    def event(self) -> CalendarEvent | None:
        if len(self._events) == 0:
            return None
        lst = []
        dt = now()
        next_ev = self._events[0]
        for i in self._events:
            if as_local(i.start) <= dt and dt <= as_local(i.end):
                lst.append(i)
            if i.start-dt < next_ev.start-dt:
                next_ev = i
        if len(lst) > 0:
            lst.sort(key=lambda x: x._severity)
            return lst[0]
        else:
            return next_ev

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        relevant_events = []
        for event in self._events:
            if (
                (event.start <= start_date and event.end >= end_date)
                or (event.start >= start_date and event.start <= end_date)
                or (event.end >= start_date and event.end <= end_date)
            ):
                relevant_events.append(event)
        return relevant_events

    @callback
    def _handle_coordinator_update(self) -> None:
        events = []
        dt = now()
        if self.coordinator.data is not None:
            for i in self.coordinator.data[DATA_INFO]:
                for t in i.periods:
                    # ignore past events
                    if as_local(t[1]) >= dt:
                        ev = CalendarEvent(
                            start=t[0],
                            end=t[1],
                            summary=i.name or i.message,
                            description=i.message,
                            recurrence_id=i.id,
                        )
                        ev._severity = i.severity
                        events.append(ev)
            self._events = events
