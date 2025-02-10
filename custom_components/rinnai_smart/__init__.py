"""The rinnai_smart integration."""

from __future__ import annotations
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import ssl as ssl_util
from homeassistant.const import (
    CONF_PASSWORD, 
    CONF_USERNAME,
    MAJOR_VERSION,
    MINOR_VERSION,
)

from .const import (
    DOMAIN,
    CLIENT
)
from .device import RinnaiDeviceDataUpdateCoordinator
from .rinnai_client import RinnaiClient

PLATFORMS = ["water_heater", "text", "select", "switch", "binary_sensor"]


def is_min_ha_version(min_ha_major_ver: int, min_ha_minor_ver: int) -> bool:
    """Check if HA version at least a specific version."""
    return (
        MAJOR_VERSION > min_ha_major_ver or
        (MAJOR_VERSION == min_ha_major_ver and MINOR_VERSION >= min_ha_minor_ver)
    )

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up rinnai_smart from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    hass.data[DOMAIN][entry.entry_id][CLIENT] = client = RinnaiClient(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    devices = await client.get_devices()
    hass.async_create_task(client.run(ssl_util.client_context()))

    hass.data[DOMAIN][entry.entry_id]["devices"] = devices = [
        RinnaiDeviceDataUpdateCoordinator(hass, client, value["device"], entry.options)
        for value in devices.values()
    ]
    for device in devices:
        # await device.async_config_entry_first_refresh() # FIXME: _async_setup is not invoked in docker HA 2024.6.3
        await device._async_setup()

    if is_min_ha_version(2022,8):
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    else:
        hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    
    return True

async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry):
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
