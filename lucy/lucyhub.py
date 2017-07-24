from __future__ import print_function
from __future__ import print_function

import logging
import threading
from lucy.exceptions import DeviceNotFound, InvalidOperation
from threading import Thread

import paho.mqtt.client as mqtt
import schedule
from modbus_tk import modbus_rtu

from devicefactory import DeviceFactory
from devices import Device
from slave import Slave


# noinspection PyShadowingBuiltins
class LucyHub(object):
    _connection = ""
    _slaves = {}
    _devices = {}
    _logger = ""
    _poller_thread_stop = ""
    _poller_thread = ""
    _broker = ""

    DISCOVERY_RETRIES = 3
    COMMUNICATION_RETRIES = 5

    def __init__(self, serial):
        format = "%(asctime)s\t%(levelname)s\t%(module)s.%(funcName)s\t%(threadName)s\t%(message)s"
        logging.basicConfig(level=logging.INFO, format=format)
        self._logger = logging.getLogger(__name__)

        self._connection = self._connect(serial)

        self.discovery()
        self._logger.info("Lucy got %d devices in %d slaves." % (len(self._devices), len(self._slaves)))
        self._connect_to_broker()
        schedule.every(1).minutes.do(self.discovery)
        self.dump()

    def _connect_to_broker(self):
        self._logger.info("Lucy is connecting to the message broker.")
        self._broker = mqtt.Client()
        self._broker.on_connect = self.on_broker_connect
        self._broker.on_message = self.on_broker_message

        self._broker.connect("127.0.0.1", 1883, 60)

        self._broker.loop_start()

    @staticmethod
    def _connect(serial):
        master = modbus_rtu.RtuMaster(serial)
        master.set_timeout(0.5)
        master.set_verbose(False)

        return master

    def dump(self):
        for k in self._slaves:
            print(self._slaves[k])
        for k in self._devices:
            print(self._devices[k])

    def discovery(self, limit=3):
        self._logger.info("Starting discovery operation")
        for slave_id in range(1, limit + 1):
            if slave_id not in self._slaves:
                self._logger.info("Looking for slave at id %s" % slave_id)
                s = Slave(slave_id, self._connection, retries=self.DISCOVERY_RETRIES)
                s.MAX_RETRIES = self.COMMUNICATION_RETRIES
                if s.nodes:
                    self._slaves[slave_id] = s
                    for node_address, node_type in s.nodes.items():
                        device = DeviceFactory.create(node_address, node_type, s)
                        if isinstance(device, Device) and device.id not in self._devices:
                            self._devices[device.id] = device

        return self._slaves

    def status(self):
        for key, device in self._devices.items():
            print("%s is %s" % (device.name, device.get_reading()))

    def get_reading(self, device=None, id=None):
        if device is not None:
            self._logger.debug('LucyHub is reading device %s as %s at %s:%s' % (
                device.__class__, device.id, device.slave.id, device.address))
            response = device.get_reading()
            self._broker.publish("lucy/devices/" + str(device.id), response)
            return response

        if id:
            try:
                device = self._devices[id]

                self._logger.debug('LucyHub is reading device %s as %s at %s:%s' % (
                    device.__class__, device.id, device.slave.id, device.address))
                response = device.get_reading()
                self._broker.publish("lucy/devices/" + str(device.id), response)
                return response
            except KeyError:
                self._logger.error("Device %s not found." % id)
            except IndexError:
                self._logger.error("Device %s not found." % id)

        r = []
        for key, device in self._devices.items():
            self._logger.debug('LucyHub is reading device %s as %s at %s:%s' % (
                device.__class__, device.id, device.slave.id, device.address))
            response = device.get_reading()
            self._broker.publish("lucy/devices/" + str(device.id), response)
            r.append(response)

        return r

    def set_value(self, value, device=None, id=None):
        if device:
            try:
                self._logger.debug('LucyHub is writing device %s as %s at %s:%s' % (
                    device.__class__, device.id, device.slave.id, device.address))
                response = device.set_value(value)
                self._broker.publish("lucy/devices/" + str(device.id), response)
                return response
            except DeviceNotFound:
                self._logger.warning("Id %s not found." % device.id)
            except InvalidOperation as e:
                self._logger.warning("Invalid operation for %s:%s" % (device.id, e))
            except Exception as e:
                self._logger.error("Exception %s" % e)

            return ""

        if id:
            try:
                device = self._devices[id]
                self._logger.debug('LucyHub is writing device %s as %s at %s:%s' % (
                    device.__class__, device.id, device.slave.id, device.address))
                response = device.set_value(value)
                self._broker.publish("lucy/devices/" + str(device.id), response)
                return response
            except InvalidOperation as e:
                self._logger.warning("Invalid operation for %s:%s" % (device.id, str(e)))
            except KeyError:
                self._logger.error("Device %s not found." % id)
            except IndexError:
                self._logger.error("Device %s not found." % id)
            except Exception as e:
                self._logger.error("Exception %s" % e)

            return ""

        r = []
        for key, device in self._devices.items():
            try:
                self._logger.debug('LucyHub is writing device %s as %s at %s:%s' % (
                    device.__class__, device.id, device.slave.id, device.address))
                response = device.set_value(value)
                self._broker.publish("lucy/devices/" + str(device.id), response)
                r.append(response)
            except InvalidOperation as e:
                self._logger.warning("Invalid operation for %s:%s" % (device.name, e))
            except Exception as e:
                self._logger.error("Exception %s" % e)

        return r

    def start(self):
        self.start_poller()

    def stop(self):
        self.stop_poller()
        self._broker.loop_stop()

    def start_poller(self):
        self._logger.info('LucyHub is starting poller.')
        self._poller_thread_stop = threading.Event()
        self._poller_thread = Thread(target=self._poller, name="Poller", args=(self._poller_thread_stop,))
        self._poller_thread.setDaemon(False)
        self._poller_thread.start()

    def stop_poller(self):
        self._poller_thread_stop.set()

    def _poller(self, stop_event):
        while not stop_event.is_set():
            schedule.run_pending()
            for key, device in self._devices.items():
                self._logger.debug('LucyHub poller is reading device %s as %s at %s:%s' % (
                    device.__class__, device.id, device.slave.id, device.address))
                device_reading = device.get_reading()
                if device.got_news:
                    self._broker.publish("lucy/devices/" + str(device.id), device_reading, retain=True)
                    device.got_news = False
                    # time.sleep(0.01)

    # The callback for when the client receives a CONNACK response from the server.
    def on_broker_connect(self, client, userdata, flags, rc):
        self._logger.info("Connected with result code " + str(rc))
        self._broker.subscribe("lucy/commands/#")

    # The callback for when a PUBLISH message is received from the server.
    def on_broker_message(self, client, userdata, msg):
        self._logger.info(msg.topic + " " + str(msg.payload))
        request = msg.topic.split("/")
        if request[0] == "lucy" and request[1] == "commands" and request[2] == "devices":
            self.set_value(int(msg.payload), id=int(request[3]))
