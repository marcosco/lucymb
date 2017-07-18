import pytest

from lucy.devicefactory import DeviceFactory
from lucy.devices import Sensor, Switch


class TestDeviceFactory(object):
    def test_create_sensor(self):
        node = DeviceFactory.create(
            10,
            "Sensor",
            None
        )
        assert isinstance(node, Sensor)

    def test_create_switch(self):
        node = DeviceFactory.create(
            10,
            "Switch",
            None
        )
        assert isinstance(node, Switch)