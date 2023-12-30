"""The ESP32 anemometer BLE integration."""
from collections.abc import Callable, Coroutine
from logging import Logger
from typing import Any

from homeassistant.components.bluetooth import (
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
)
from homeassistant.components.bluetooth.active_update_processor import (
    ActiveBluetoothProcessorCoordinator,
)
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer

from .const import CONF_SLEEPY_DEVICE
from .parser import Esp32AnemometerBluetoothDeviceData as DeviceData


class Esp32ActiveBluetoothProcessorCoordinator(ActiveBluetoothProcessorCoordinator):
    """Define a Bluetooth Active Update Processor Coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: Logger,
        *,
        address: str,
        mode: BluetoothScanningMode,
        update_method: Callable[[BluetoothServiceInfoBleak], Any],
        needs_poll_method: Callable[[BluetoothServiceInfoBleak, float | None], bool],
        device_data: DeviceData,
        discovered_device_classes: set[str],
        poll_method: Callable[
            [BluetoothServiceInfoBleak],
            Coroutine[Any, Any, Any],
        ]
        | None = None,
        poll_debouncer: Debouncer[Coroutine[Any, Any, None]] | None = None,
        entry: ConfigEntry,
        connectable: bool = True,
    ) -> None:
        """Initialize the Xiaomi Bluetooth Active Update Processor Coordinator."""
        super().__init__(
            hass=hass,
            logger=logger,
            address=address,
            mode=mode,
            update_method=update_method,
            needs_poll_method=needs_poll_method,
            poll_method=poll_method,
            poll_debouncer=poll_debouncer,
            connectable=connectable,
        )
        self.discovered_device_classes = discovered_device_classes
        self.device_data = device_data
        self.entry = entry

    @property
    def sleepy_device(self) -> bool:
        """Return True if the device is a sleepy device."""
        return self.entry.data.get(CONF_SLEEPY_DEVICE, self.device_data.sleepy_device)


class Esp32BluetoothDataProcessor(PassiveBluetoothDataProcessor):
    """Define a Bluetooth Passive Update Data Processor."""

    coordinator: Esp32ActiveBluetoothProcessorCoordinator