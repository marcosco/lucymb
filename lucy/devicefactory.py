from __future__ import print_function
from lucy.devices import Switch, Sensor


# Must be Refactored in order to accept the type directly and not the string representing the type itself.
class DeviceFactory:
    def __init__(self):
        pass

    @staticmethod
    def create(node_address, node_type, slave):
        """

        :param node_address: Address of the Node
        :type node_address: int
        :param node_type: Define the type of the node, currently Sensor or Switch
        :type node_type: string
        :param slave:
        :type slave:
        :return:
        :rtype: Any -> (
        """
        if node_type.upper() == "SENSOR":
            return Sensor("Sensor", node_address, slave)
        if node_type.upper() == "SWITCH":
            return Switch("Switch", node_address, slave)

        print("Unable to create %s" % node_type)
