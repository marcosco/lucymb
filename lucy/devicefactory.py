from __future__ import print_function
from devices import Sensor, Switch


# Must be Refactored in order to accept the type directly and not the string representing the type itself.
class DeviceFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(node_address, node_type, slave):
        """

        :param node_address: Address of the Node
        :type node_address: str
        :param node_type:
        :type node_type:
        :param slave:
        :type slave:
        :return:
        :rtype: Any -> (
        """
        if node_type == "SENSOR":
            return Sensor("Sensor", node_address, slave)
        if node_type == "SWITCH":
            return Switch("Switch", node_address, slave)

        print("Unable to create %s" % node_type)
