import json
import datetime
import logging
from .exceptions import ErrorReadingDevice, InvalidOperation

class Device(object):
    name = ""
    _reading = ""
    _address = 0
    _slave = 0
    _errors = 0
    lastRead = ""
    id = ""
    _logger = ""
    got_news = True


    def __init__(self, name, address, slave):
        format = "%(asctime)s\t%(levelname)s\t%(module)s.%(funcName)s\t%(threadName)s\t%(message)s"
        logging.basicConfig(level=logging.DEBUG, format=format)

        self._logger = logging.getLogger(__name__)
        self.name = name
        self._address = address
        self._slave = slave
        self.id = self._slave.id*256 + self._address
        self._logger.info('Device %s created as %s at %s:%s'%(self.__class__, self.id, self._slave.id, self._address))

        self.get_reading()

    def __str__(self):
        device = {}
        device["Id"] = self.id
        device["Name"] = self.name
        device["Reading"] = self._reading
        device["Address"] = self._address
        device["SlaveId"] = self._slave.id
        device["Errors"] = self._errors
        device["LastRead"] = self.lastRead

        return json.dumps(device)

    def set_reading(self, reading):
        self._logger.debug('Device %s is set reading as %s at %s:%s'%(self.__class__, self.id, self._slave.id, self._address))

        if reading != self._reading:
            self._reading = reading
            self.got_news = True
            self.lastRead = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return str(self)


    def get_reading(self):
        try:
            self._logger.debug('Device %s reading as %s at %s:%s'%(self.__class__, self.id, self._slave.id, self._address))

            response = self._slave.read_holding_registers(self._address, 1)
            if response["ret"][0] != self._reading:
                self._reading = response["ret"][0]
                self.got_news = True
            self._errors += response["err"]
            self.lastRead = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except ErrorReadingDevice as e:
            self._logger.error('Device %s error reading as %s at %s:%s with %s'%(self.__class__, self.id, self._slave.id, self._address, e))

        return str(self)

    def get_address(self):
        return self._address

    def get_slave_id(self):
        return self._slave_id

class Sensor(Device):
    device_type = "sensor"

    def __init__(self, name, address, slave):
        Device.__init__(self, name, address, slave)

    def set_value(self, value):
        raise(InvalidOperation("Operation not supported."))

class Switch(Device):
    device_type = "switch"

    def __init__(self, name, address, slave):
        Device.__init__(self, name, address, slave)

    def set_value(self, value):
        self._logger.debug('Device %s writing as %s at %s:%s'%(self.__class__, self.id, self._slave.id, self._address))

        response = self._slave.write_single_register(self._address, value)
        self._reading = response["ret"][1]
        self._errors += response["err"]
        return str(self)
