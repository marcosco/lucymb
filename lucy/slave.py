import datetime
import json
import logging
import modbus_tk
import modbus_tk.defines as cst
import time

from modbus_tk import modbus_rtu, hooks
from .exceptions import ErrorReadingDevice
from serial import SerialException

class Slave():
    sensors = {
                0:      "NOT_VALID",
                16:     "SENSOR",
                128:    "SWITCH"
              }

    MAX_RETRIES = 0

    logger = modbus_tk.utils.create_logger("console", level=logging.WARNING)

    def __init__(self, id, master, retries=5):
        self._master = {}
        self._errors = 0;
        self.nodes = {};
        self.MAX_RETRIES = retries
        self.id = id
        self._master = master
        self.nodes = self._extract_manifesto()

    def __str__(self):
        slave = {
                    "Id":           self.id,
                    "Errors":       self._errors,
                    "Nodes":        self.nodes,
                    "LastConnect":  self.lastConnect
                }

        return str(slave)

    def _extract_manifesto(self):
        D = {};

        try:
            count = self.read_holding_registers(0, 1)["ret"][0]

            for index in range(count):
                try:
                    node_type = self.read_holding_registers(0 + index + 1, 1)["ret"][0]
                    node_addr = count + index + 1
                    D[node_addr] = self.sensors[node_type]
                except modbus_tk.modbus_rtu.ModbusInvalidResponseError as e:
                    self.logger.error("ModbusInvalidResponseError: %s"%e)
                except ErrorReadingDevice as e:
                    self.logger.error("ErrorReadingDevice: %s"%e)
            return D

        except modbus_tk.modbus.ModbusError as exc:
            self.logger.error("%s- Code=%d", exc, exc.get_exception_code())
        except ErrorReadingDevice as e:
            self.logger.warning("Device is unreachable: %s"%e)

    def read_holding_registers(self, addr, length, attempt=0):
        attempt += 1
        try:
            master = self._master
            ret = {
                    "ret": master.execute(self.id, cst.READ_HOLDING_REGISTERS, addr, length),
                    "err": attempt -1
                  }
            self.lastConnect = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return ret

        except (SerialException, modbus_tk.modbus.ModbusError, modbus_tk.modbus_rtu.ModbusInvalidResponseError) as e:
            if attempt < self.MAX_RETRIES:
                self._master.close()
                time.sleep(1.50)
                self._errors += 1;
                self.logger.info("Attempt %s: Retrying..."%attempt)
                return self.read_holding_registers(addr, length, attempt)

            else:
                self.logger.warning("Attempt %s: Skipping..."%attempt)
                raise(ErrorReadingDevice("Error reading device."))

    def write_single_register(self, addr, value, attempt=0):
        attempt += 1
        try:
            # Connect to the slave
            master = self._master

            ret = {
                    "ret": master.execute(self.id, cst.WRITE_SINGLE_REGISTER, addr, output_value=value),
                    "err": attempt -1
                  }
            self.lastConnect = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.logger.info(ret)
            return ret

        except modbus_tk.modbus.ModbusError as exc:
            raise(ErrorReadingDevice("Error reading device."))
        except modbus_tk.modbus_rtu.ModbusInvalidResponseError as e:
            if attempt < self.MAX_RETRIES:
                self._errors += 1;
                return self.write_single_register(addr, value, attempt)

            else:
                raise(ErrorReadingDevice("Error reading device."))
