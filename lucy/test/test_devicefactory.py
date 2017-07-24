import pytest
from lucy.devices import Device
from lucy.slave import Slave
from lucy.devicefactory import DeviceFactory
from lucy.devices import Sensor, Switch


class TestDeviceFactory(object):
    def test_create_sensor(self, monkeypatch):
        monkeypatch.setattr(Device, 'get_reading', lambda x: str())
        monkeypatch.setattr(Slave, '_extract_manifesto', lambda x: dict())
        mock_slave = Slave(slave_id=1, master='Master')
        node = DeviceFactory.create(
            node_address=10,
            node_type="Sensor",
            slave=mock_slave
        )
        assert isinstance(node, Sensor)

    def test_create_switch(self, monkeypatch):
        monkeypatch.setattr(Device, 'get_reading', lambda x: str())
        monkeypatch.setattr(Slave, '_extract_manifesto', lambda x: dict())
        mock_slave = Slave(slave_id=1, master='Master')
        node = DeviceFactory.create(
            node_address=10,
            node_type="Switch",
            slave=mock_slave
        )
        assert isinstance(node, Switch)
