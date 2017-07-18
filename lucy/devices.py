import json
import datetime
import logging
from lucy.exceptions import ErrorReadingDevice, InvalidOperation
from abc import ABCMeta, abstractmethod


# Abstract Class Defining the base Device Object
class Device(object):
    __metaclass__ = ABCMeta

    # Private Properties
    _reading = str()
    _address = int()
    _slave = int()
    _errors = int()
    _logger = None

    # Public Properties
    name = str()
    lastRead = str()
    id = str()
    got_news = True

    def __init__(self, name, address, slave):
        logFormat = "%(asctime)s\t%(levelname)s\t%(module)s.%(funcName)s\t%(threadName)s\t%(message)s"
        logging.basicConfig(level=logging.DEBUG, format=logFormat)

        self._logger = logging.getLogger(__name__)
        self.name = name
        self._address = address
        self._slave = slave
        self.id = self._slave.id * 256 + self._address
        self._logger.info('Device %s created as %s at %s:%s' % (self.__class__, self.id, self._slave.id, self._address))

        self.get_reading()

    # This method should return a string not a serialized json
    # TODO: Change this and implement the object as Serializable
    def __str__(self):
        device = {
            "Id": self.id,
            "Name": self.name,
            "Reading": self._reading,
            "Address": self._address,
            "SlaveId": self._slave.id,
            "Errors": self._errors,
            "LastRead": self.lastRead
        }
        return json.dumps(device)

    @property
    def slave(self):
        return self._slave

    @property
    def address(self):
        return self._address

    def get_reading(self):
        """

        :return:
        :rtype:
        """
        try:
            self._logger.debug(
                'Device %s reading as %s at %s:%s' % (self.__class__, self.id, self._slave.id, self._address))

            response = self._slave.read_holding_registers(self._address, 1)
            if response["ret"][0] != self._reading:
                self._reading = response["ret"][0]
                self.got_news = True
            self._errors += response["err"]
            self.lastRead = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except ErrorReadingDevice as e:
            self._logger.error('Device %s error reading as %s at %s:%s with %s' % (
                self.__class__, self.id, self._slave.id, self._address, e))
        return str(self)

    def get_address(self):
        """

        :return:
        :rtype:
        """
        return self._address

    @abstractmethod
    def get_slave_id(self):
        raise NotImplementedError("This method must be implemented.")

    @abstractmethod
    def set_value(self, value):
        raise NotImplementedError("This method must be implemented.")


# TODO: Those objects should be serializable implicitly. Implement it.
class Sensor(Device):
    def __init__(self, name, address, slave):
        super(Sensor, self).__init__(name, address, slave)

    def get_slave_id(self):
        return self._slave.id

    def set_value(self, value):
        raise InvalidOperation("Operation not supported.")


class Switch(Device):
    def __init__(self, name, address, slave):
        super(Switch, self).__init__(name, address, slave)

    def get_slave_id(self):
        raise InvalidOperation("Operation not supported.")

    def set_value(self, value):
        self._logger.debug(
            'Device %s writing as %s at %s:%s' % (self.__class__, self.id, self._slave.id, self._address))

        response = self._slave.write_single_register(self._address, value)
        self._reading = response["ret"][1]
        self._errors += response["err"]
        return str(self)
