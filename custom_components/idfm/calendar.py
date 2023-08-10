import datetime

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant, callback
from homeassistant.util.dt import as_local, now

from .const import CONF_LINE_NAME, CONF_STOP_NAME, DOMAIN, DATA_INFO
from .entity import IDFMEntity


async def async_setup_entry(
    hass: HomeAssistant,
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
        lst = []
        next_ev = None
        next_ev_t = None
        dt = now()
        if self.coordinator.data is not None:
            for i in self.coordinator.data[DATA_INFO]:
                for t in i.periods:
                    if dt <= as_local(t[1]):
                        if as_local(t[0]) <= dt:
                            lst.append(i)
                        elif next_ev is None or t[0]-dt < next_ev_t[0]-dt:
                            next_ev = i
                            next_ev_t = t
            if len(lst) > 0:
                t = ()
                lst.sort(key=lambda x: x.severity)
                for p in lst[0].periods:
                    if as_local(p[0]) <= dt and dt <= as_local(p[1]):
                        t = p
                return CalendarEvent(
                    start=t[0],
                    end=t[1],
                    summary=lst[0].name or lst[0].message,
                    description=lst[0].message,
                    recurrence_id=lst[0].id,
                )
            elif next_ev is not None:
                return CalendarEvent(
                    start=next_ev_t[0],
                    end=next_ev_t[1],
                    summary=next_ev.name or next_ev.message,
                    description=next_ev.message,
                    recurrence_id=next_ev.id,
                )
        return None

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
