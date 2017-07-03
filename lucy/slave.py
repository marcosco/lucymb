import datetime
import json
import logging
from lucy.exceptions import ErrorReadingDevice

import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu


class Slave(object):
    id = str()
    _master = dict()
    _errors = int()
    lastConnect = str()

    nodes = {}

    sensors = dict()
    sensors[0] = "NOT_VALID"
    sensors[16] = "SENSOR"
    sensors[128] = "SWITCH"

    MAX_RETRIES = 0

    logger = modbus_tk.utils.create_logger("console", level=logging.WARNING)

    def __init__(self, slave_id, master, retries=5):
        self.MAX_RETRIES = retries
        self.id = slave_id
        self._master = master
        self.nodes = self._extract_manifesto()

    def __str__(self):
        slave = {"Id": self.id, "Errors": self._errors, "Nodes": self.nodes, "LastConnect": self.lastConnect}

        return json.dumps(slave)

    def _extract_manifesto(self):
        D = {}

        try:
            count = self.read_holding_registers(0, 1)["ret"][0]

            for index in range(count):
                try:
                    node_type = self.read_holding_registers(0 + index + 1, 1)["ret"][0]
                    node_addr = count + index + 1

                    D[node_addr] = self.sensors[node_type]
                except modbus_tk.modbus_rtu.ModbusInvalidResponseError as e:
                    self.logger.error("ModbusInvalidResponseError: %s" % e)
                except ErrorReadingDevice as e:
                    self.logger.error("ErrorReadingDevice: %s" % e)
            return D

        except modbus_tk.modbus.ModbusError as exc:
            self.logger.error("%s- Code=%d", exc, exc.get_exception_code())
        except ErrorReadingDevice as e:
            self.logger.error("ErrorReadingDevice: %s" % e)

    def read_holding_registers(self, addr, length, attempt=0):
        attempt += 1
        try:
            master = self._master
            ret = {"ret": master.execute(self.id, cst.READ_HOLDING_REGISTERS, addr, length), "err": attempt - 1}
            self.lastConnect = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.logger.info(ret)
            return ret

        except modbus_tk.modbus.ModbusError as exc:
            # self.logger.error("%s- Code=%d", exc, exc.get_exception_code())
            raise (ErrorReadingDevice("Error reading device."))

        except modbus_tk.modbus_rtu.ModbusInvalidResponseError as e:
            # self.logger.error("ModbusInvalidResponseError: %s"%e)
            if attempt < self.MAX_RETRIES:
                self._errors += 1;
                # self.logger.info("Attempt %s: Retrying..."%attempt)
                return self.read_holding_registers(addr, length, attempt)

            else:
                # self.logger.warning("Attempt %s: Skipping..."%attempt)
                raise (ErrorReadingDevice("Error reading device."))

    def write_single_register(self, addr, value, attempt=0):
        attempt += 1
        try:
            # Connect to the slave
            master = self._master

            ret = {"ret": master.execute(self.id, cst.WRITE_SINGLE_REGISTER, addr, output_value=value),
                   "err": attempt - 1}
            self.lastConnect = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.logger.info(ret)
            return ret

        except modbus_tk.modbus.ModbusError as exc:
            # self.logger.error("%s- Code=%d", exc, exc.get_exception_code())
            raise (ErrorReadingDevice("Error reading device."))
        except modbus_tk.modbus_rtu.ModbusInvalidResponseError as e:
            # self.logger.error("ModbusInvalidResponseError: %s"%e)
            if attempt < self.MAX_RETRIES:
                self._errors += 1;
                # self.logger.info("Attempt %s: Retrying..."%attempt)
                return self.write_single_register(addr, value, attempt)

            else:
                # self.logger.warning("Attempt %s: Skipping..."%attempt)
                raise (ErrorReadingDevice("Error reading device."))
