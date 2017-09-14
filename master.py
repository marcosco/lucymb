#!/usr/bin/env python
import serial
import time
import sys

from lucy.lucyhub import LucyHub
from lucy.exceptions import DeviceNotFound, InvalidOperation

PORT = "/dev/ttyUSB0"
BAUDRATE = 57600
def main():
    global input

    rtu_connection = serial.Serial(port=PORT, baudrate=BAUDRATE, bytesize=8, parity='N', stopbits=1, xonxoff=0)
    lucy = LucyHub(rtu_connection)
    print("Lucy is online!")
    try: input = raw_input
    except NameError: pass

    lucy.start()
    try:
        print("Waiting for user input")
        while True:
            msg = input("Command To Send: ")
            if msg == "close":
                lucy.stop()
                lucy.dump()
                sys.exit(0)
    except IOError:
        print("Running as daemon")

if __name__ == "__main__":
    main()
