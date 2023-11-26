"""Parser for ESP32 Anemometer BLE devices."""

from dataclasses import dataclass
from datetime import datetime
import logging
import re
import sys
from typing import Any

from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import (
    DeviceClass,
    DeviceKey,
    SensorDescription,
    SensorDeviceInfo,
    SensorLibrary,
    SensorUpdate,
    SensorValue,
    Units,
)

_LOGGER = logging.getLogger(__name__)


class Esp32AnemometerBluetoothDeviceData(BluetoothData):
    """Data for ESP32 Anemometer BLE sensors."""

    __ADVERTISING_MANUFACTURING_DATA_KEY = 13

    def __init__(self) -> None:
        super().__init__()

        # Data that we know how to parse but don't yet map to the SensorData model.
        self.unhandled: dict[str, Any] = {}

        # If this is True, then we have not seen an advertisement with a payload
        # Until we see a payload, we can't tell if this device is encrypted or not
        self.pending = True

        # The last service_info we saw that had a payload
        # We keep this to help in reauth flows where we want to reprocess and old
        # value with a new bindkey.
        self.last_service_info: BluetoothServiceInfo | None = None

    def supported(self, data: BluetoothServiceInfo) -> bool:
        ret = False
        manuf_data = data.manufacturer_data
        # TODO to update
        if (
            len(manuf_data) == 1
            and self.__ADVERTISING_MANUFACTURING_DATA_KEY in manuf_data.keys()
        ):
            bytes_data = manuf_data[self.__ADVERTISING_MANUFACTURING_DATA_KEY]
            if (
                len(bytes_data) == self.__ADVERTISING_DATA_SIZE
                and bytes_data[0] == 0x05
            ):
                ret = True
        return ret

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug(
            "Parsing ESP32 Anemometer BLE advertisement data: %s", service_info
        )

        # TODO to update

        raw_data = self.get_manufacturing_data(service_info)
        if raw_data is not None and self._parse_data(raw_data, True):
            self.last_service_info = service_info

    def _parse_data(self, raw_data: bytearray, is_adv_data: bool = False) -> bool:
        """
        Decode the raw data and update the corresponding value.

        :param raw_data: Bytes from the frame.
        :param is_adv_data: Information if data comes from advertising data of active connection.
        :return: None
        """

        # TODO to update

        frame_length = self.__CONNECTED_DATA_SIZE
        offset = 0
        if is_adv_data:
            frame_length = self.__ADVERTISING_DATA_SIZE
            offset = 1

        if len(raw_data) != frame_length:
            return False

        # Positive value: byte 1 & 2 present the tenfold of the temperature
        # Negative value: byte 2 - byte 3 present the tenfold of the temperature
        # t0 = val [ 0 ]
        # t1 = val [ 1 ]
        # t2 = val [ 2 ]
        # if t2 == 255:
        #   temperature = (t1 - t2) / 10.0
        # else:
        #   temperature = ((t0 * 255) + t1) / 10.0
        start_idx = 1 + offset
        stop_idx = start_idx + 2
        temp = int.from_bytes(raw_data[start_idx:stop_idx], "little")
        if temp >= 0x8000:
            temp = temp - 0xFFFF
        self.temperature = temp / 10.0
        self.humidity = raw_data[4 + offset]
        self.battery = raw_data[9 + offset]
        self.update_predefined_sensor(
            SensorLibrary.TEMPERATURE__CELSIUS, self.temperature
        )
        self.update_predefined_sensor(SensorLibrary.HUMIDITY__PERCENTAGE, self.humidity)
        self.update_predefined_sensor(SensorLibrary.BATTERY__PERCENTAGE, self.battery)

        return True

    def get_manufacturing_data(self, adv_data: BluetoothServiceInfo) -> bytearray:
        """
        Get the manufacturing data from the manufacturing frame.Z

        Args:
            adv_data (BluetoothServiceInfo): Frame with data

        Raises:
            Exception: Invalid data detected

        Returns:
            bytearray: the data to update sensor values
        """
        # TODO to update

        data = adv_data.manufacturer_data
        if self.__ADVERTISING_MANUFACTURING_DATA_KEY in data.keys():
            ret = bytearray(data[self.__ADVERTISING_MANUFACTURING_DATA_KEY])
        else:
            raise Exception("Invalid data for this sensor.")
        return ret
