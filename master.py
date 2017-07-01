#!/usr/bin/env python
import serial
import time
import sys

from lucy.lucyhub import LucyHub
from lucy.exceptions import DeviceNotFound, InvalidOperation

PORT = "/dev/ttyUSB0"
#BAUDRATE = 57600
BAUDRATE = 9600
def main():
	rtu_connection = serial.Serial(port=PORT, baudrate=BAUDRATE, bytesize=8, parity='N', stopbits=1, xonxoff=0)
	lucy = LucyHub(rtu_connection)
	print "Lucy is online!"

	lucy.start()
	print("Waiting for user input")
	while True:
		msg = raw_input("Command To Send: ")
		if msg == "close":
			lucy.stop()
			lucy.dump()
			sys.exit(0)


if __name__ == "__main__":
    main()
