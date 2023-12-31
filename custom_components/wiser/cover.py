"""
Cover Platform Device for Wiser.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
import asyncio

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverEntity,
    CoverEntityFeature,
)

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .schedules import WiserScheduleEntity

from .const import (
    DATA,
    DOMAIN,
    MANUFACTURER_SCHNEIDER,
)
from .helpers import get_device_name, get_identifier

import logging

MANUFACTURER = MANUFACTURER_SCHNEIDER

_LOGGER = logging.getLogger(__name__)

SUPPORT_FLAGS = (
    CoverEntityFeature.OPEN
    | CoverEntityFeature.CLOSE
    | CoverEntityFeature.SET_POSITION
    | CoverEntityFeature.STOP
)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up Wiser shutter device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]

    wiser_shutters = []
    if data.wiserhub.devices.shutters:
        _LOGGER.debug("Setting up shutter entities")
        for shutter in data.wiserhub.devices.shutters.all:
            if shutter.product_type == "Shutter":
                wiser_shutters.append(WiserShutter(data, shutter.id))
        async_add_entities(wiser_shutters, True)


class WiserShutter(CoordinatorEntity, CoverEntity, WiserScheduleEntity):
    """Wisershutter ClientEntity Object."""

    def __init__(self, coordinator, shutter_id) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._device_id = shutter_id
        self._device = self._data.wiserhub.devices.shutters.get_by_id(self._device_id)
        self._schedule = self._device.schedule
        _LOGGER.debug(f"{self._data.wiserhub.system.name} {self.name} initialise")

    async def async_force_update(self, delay: int = 0):
        _LOGGER.debug(f"Hub update initiated by {self.name}")
        if delay:
            asyncio.sleep(delay)
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug(f"{self.name} updating")
        self._device = self._data.wiserhub.devices.shutters.get_by_id(self._device_id)
        self._schedule = self._device.schedule
        self.async_write_ha_state()

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_FLAGS

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._device_id),
            "identifiers": {(DOMAIN, get_identifier(self._data, self._device_id))},
            "manufacturer": MANUFACTURER,
            "model": self._data.wiserhub.devices.get_by_id(self._device_id).model,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def icon(self):
        """Return icon to show if shutter is closed or Open."""
        return "mdi:window-shutter" if self.is_closed else "mdi:window-shutter-open"

    @property
    def name(self):
        """Return Name of device"""
        return f"{get_device_name(self._data, self._device_id)} Control"

    @property
    def current_cover_position(self):
        """Return current position from data."""
        return self._device.current_lift

    @property
    def is_closed(self):
        return self._device.is_closed

    @property
    def is_opening(self):
        return self._device.is_opening

    @property
    def is_closing(self):
        return self._device.is_closing

    @property
    def unique_id(self):
        """Return unique Id."""
        return f"{self._data.wiserhub.system.name}-Wisershutter-{self._device_id}-{self.name}"

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        # Generic attributes
        attrs = super().state_attributes
        # Shutter Identification
        attrs["name"] = self._device.name
        attrs["model"] = self._device.model
        attrs["product_type"] = self._device.product_type
        attrs["product_identifier"] = self._device.product_identifier
        attrs["product_model"] = self._device.product_model
        attrs["serial_number"] = self._device.serial_number
        attrs["firmware"] = self._device.firmware_version

        # Room
        if self._data.wiserhub.rooms.get_by_id(self._device.room_id) is not None:
            attrs["room"] = self._data.wiserhub.rooms.get_by_id(
                self._device.room_id
            ).name
        else:
            attrs["room"] = "Unassigned"

        # Settings
        attrs["shutter_id"] = self._device_id
        attrs["away_mode_action"] = self._device.away_mode_action
        attrs["mode"] = self._device.mode
        attrs["lift_open_time"] = self._device.drive_config.open_time
        attrs["lift_close_time"] = self._device.drive_config.close_time

        # Command state
        attrs["control_source"] = self._device.control_source

        # Status
        attrs["is_open"] = self._device.is_open
        attrs["is_closed"] = self._device.is_closed
        if self._device.is_open:
            attrs["current_state"] = "Open"
        elif self._device.is_closed:
            attrs["current_state"] = "Closed"
        elif not (self._device.is_open or self._device.is_closed):
            attrs["current_state"] = "Middle"
        attrs["lift_movement"] = self._device.lift_movement

        # Positions
        attrs["current_lift"] = self._device.current_lift
        attrs["manual_lift"] = self._device.manual_lift
        attrs["target_lift"] = self._device.target_lift
        attrs["scheduled_lift"] = self._device.scheduled_lift

        # Schedule
        attrs["schedule_id"] = self._device.schedule_id
        if self._device.schedule:
            attrs["schedule_name"] = self._device.schedule.name
            attrs["next_day_change"] = str(self._device.schedule.next.day)
            attrs["next_schedule_change"] = str(self._device.schedule.next.time)
            attrs["next_schedule_datetime"] = str(self._device.schedule.next.datetime)
            attrs["next_schedule_state"] = self._device.schedule.next.setting

        return attrs

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs[ATTR_POSITION]
        _LOGGER.debug(f"Setting cover position for {self.name} to {position}")
        await self._device.open(position)
        await self.async_force_update()

    async def async_close_cover(self, **kwargs):
        """Close shutter"""
        _LOGGER.debug(f"Closing {self.name}")
        await self._device.close()
        await self.async_force_update()

    async def async_open_cover(self, **kwargs):
        """Close shutter"""
        _LOGGER.debug(f"Opening {self.name}")
        await self._device.open()
        await self.async_force_update()

    async def async_stop_cover(self, **kwargs):
        """Stop shutter"""
        _LOGGER.debug(f"Stopping {self.name}")
        await self._device.stop()
        await self.async_force_update()
