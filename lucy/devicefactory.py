from .devices import Sensor, Switch

class DeviceFactory():
    @staticmethod
    def create(node_address, node_type, slave):
        if node_type == "SENSOR":
            return Sensor("Sensor", node_address, slave)
        if node_type == "SWITCH":
            return Switch("Switch", node_address, slave)

        print("Unable to create %s" % node_type)
