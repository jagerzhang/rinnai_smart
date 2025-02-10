"""Constants for the rinnai_smart integration."""

import logging


LOGGER = logging.getLogger(__package__)

DOMAIN = "rinnai"
CLIENT = "client"

TITLE = "林内智家"
MANUFACTURER = "林内"
WATER_HEATER = "热水器"

MIN_TEMP = 32
MAX_TEMP = 60

OPERATION_MAP = {
    # "0":  "关机",
    "A0":  "普通模式",
    "C1":  "厨房模式",
    "C2":  "低温模式",
    "D0":  "淋浴模式",
    "84":  "浴缸模式",
    "88":  "水温按摩模式",
    "E0":  "循环模式"
}

OPERATION_COMMAND_MAP = {
    "普通模式": "regularMode", 
    "厨房模式": "kitchenMode",
    "低温模式": "lowTempMode",
    "淋浴模式": "showerMode",
    "浴缸模式": "bathModeConfirm",
    "水温按摩模式": "massageMode",
    # "循环模式": "cycleModeSetting"
}

CYCLE_MODE_MAP = {"0": "标准", "1": "舒适", "2": "节能"}

CYCLE_MODE_COMMAND_MAP = {
    "标准": "00",
    "舒适": "01", 
    "节能": "02"
}

SWITCHES = [
    {
        "icon": "mdi:power-cycle",
        "entity_type": "cycle_reservation",
        "name": "循环预约"
    },
    {
        "icon": "mdi:water-circle",
        "entity_type": "temporary_cycle_insulation",
        "name": "一键循环"
    },
]

SELECTS = [
    {
        "entity_type": "cycle_mode",
        "name": "循环模式",
        "options": list(CYCLE_MODE_MAP.values())
    },
    {
        "entity_type": "operation_mode",
        "name": "模式",
        "options": list(OPERATION_MAP.values())
    },
]

TEXTS = [
    {
        "icon": "mdi:av-timer",
        "entity_type": "cycle_reservation_time",
        "name": "循环预约时间",
        "mode": "text",
        "pattern": r"^(\d+(,\d+)*)?$"
    }
]

BINARY_SENSORS = [
    {
        "icon": "mdi:gas-burner",
        "entity_type": "burning_state",
        "name": "燃烧状态",
    }
]