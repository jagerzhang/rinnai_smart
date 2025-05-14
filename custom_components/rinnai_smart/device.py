"""Rinnai device object"""
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN, LOGGER, MANUFACTURER, OPERATION_COMMAND_MAP, CYCLE_MODE_MAP, CYCLE_MODE_COMMAND_MAP, OPERATION_MAP
)
from .rinnai_client import RinnaiClient

class RinnaiDeviceDataUpdateCoordinator(DataUpdateCoordinator):
    """Rinnai device object"""

    def __init__(
        self, hass: HomeAssistant, client: RinnaiClient, device: dict, options
    ):
        """Initialize the device"""
        self.hass: HomeAssistant = hass
        self._client: RinnaiClient = client
        self._device: dict = device
        self._manufacturer: str = MANUFACTURER
        self._device_information: Optional[Dict[str, Any]] | None = None
        self.options = options
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}-{device["id"]}",
            always_update=False
        )
    
    @property
    def id(self) -> str:
        """Return Rinnai thing name"""
        return self._device["id"]

    @property
    def device_name(self) -> str:
        """Return device name."""
        return self._device["name"]

    @property
    def manufacturer(self) -> str:
        """Return manufacturer for device"""
        return self._manufacturer

    @property
    def model(self) -> str:
        """Return model for device"""
        return self._device["deviceType"][-3:]

    @property
    def target_temperature(self) -> float:
        """Return the current temperature in degrees F"""
        return int(self._device_information["hotWaterTempSetting"], 16)

    @property
    def operation_mode(self) -> str:
        data = int(self._device_information["operationMode"], 16)
        data &= 0xBF
        return OPERATION_MAP.get("%02X" % data)

    @property
    def is_heating(self) -> bool:
        return self._device_information["burningState"] == "1"

    @property
    def is_on(self) -> bool:
        return self._device_information["operationMode"] != "0"
    
    @property
    def cycle_mode(self) -> str | None:
        return CYCLE_MODE_MAP.get(self._device_information["cycleModeSetting"], None)
    
    @property
    def is_cycle_reservation_on(self) -> bool:
        return self._device_information["cycleReservationSetting1"] == "1"
    
    @property
    def is_temporary_cycle_insulation_on(self) -> bool:
        return self._device_information["temporaryCycleInsulationSetting"] == "31"
    
    @property
    def is_burn_state_on(self) -> bool:
        return self._device_information["burningState"] == "1"

    @property
    def cycle_reservation_time(self) -> str:
        hours = []
        hour = 0
        print(self._device_information)
        return ""
        for hex_str in self._device_information["cycleReservationTimeSetting"].split():
            hex_value = int(hex_str, 16)
            for i in range(8):
                if hex_value & (1 << i):
                    hours.append(str(hour))
                hour += 1
        return ','.join(hours)

    async def _async_setup(self) -> None:
        await self._client.subscribe(self._device["id"], self._update_device)

    async def async_turn_off(self):
        await self._client.publish(self._device, "power", "00")

    async def async_turn_on(self):
        await self._client.publish(self._device, "power", "01")

    async def async_set_temperature(self, temperature: int):
        previous_temperature = int(self._device_information["hotWaterTempSetting"], 16)
        if temperature > previous_temperature:
            await self._client.publish(self._device, "hotWaterTempOperate", "01")
        elif temperature < previous_temperature:
            await self._client.publish(self._device, "hotWaterTempOperate", "00")

    async def async_set_operation_mode(self, operation_mode):
        command_id = OPERATION_COMMAND_MAP.get(operation_mode)
        if command_id:
            await self._client.publish(self._device, command_id, "01")

    async def async_set_cycle_mode(self, cycle_mode):
        await self._client.publish(self._device, "cycleModeSetting", CYCLE_MODE_COMMAND_MAP[cycle_mode])

    async def async_turn_on_cycle_reservation(self):
        await self._client.publish(self._device, "cycleReservationSetting1", "01")

    async def async_turn_off_cycle_reservation(self):
        await self._client.publish(self._device, "cycleReservationSetting1", "00")

    async def async_turn_on_temporary_cycle_insulation(self):
        await self._client.publish(self._device, "temporaryCycleInsulationSetting", "31")

    async def async_turn_off_temporary_cycle_insulation(self):
        await self._client.publish(self._device, "temporaryCycleInsulationSetting", "30")

    async def async_set_cycle_reservation_time(self, value: str):
        hours = [0, 0, 0]
        for hour in value.split(","):
            hour = int(hour, 10)
            index = int(hour / 8)
            bit = hour % 8
            hours[index] |= (1<<bit)
        data = " ".join(["%02X" % hour for hour in hours])
        await self._client.publish(self._device, "cycleReservationTimeSetting", data)

    async def _async_update_data(self):
        return self._device_information

    async def _update_device(self, device_info: dict) -> None:
        """Update the device information from the API"""
        self._device_information = device_info
        self.async_update_listeners()

        LOGGER.debug("Rinnai device data: %s", self._device_information)
