from __future__ import print_function
from lucy.devices import Switch, Sensor
from lucy.slave import Slave
from lucy.exceptions import NoTypeSpecifiedToFactory


# Must be Refactored in order to accept the type directly and not the string representing the type itself.
class DeviceFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(node_address, node_type, slave):
        """
        Factory Method to return the device type.

        :param node_address: Address of the Node
        :type node_address: int
        :param node_type: Define the type of the node, currently Sensor or Switch
        :type node_type: string
        :param slave: Slave Object to be bind to
        :type slave: Slave
        :return: Switch or Sensor Object
        :rtype: Any -> (Switch or Sensor)
        """
        if node_type.upper() == "SENSOR":
            return Sensor(name="Sensor", address=node_address, slave=slave)
        if node_type.upper() == "SWITCH":
            return Switch(name="Switch", address=node_address, slave=slave)
        raise NoTypeSpecifiedToFactory(message="No type specified during creation from the factory.")
