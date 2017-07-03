#!/usr/bin/env python
from __future__ import print_function

try:
    import __builtin__

    getattr(__builtin__, 'raw_input')
    # Python 2.*
    input_function = raw_input
except (ImportError, AttributeError):
    # Python 3.*
    input_function = input
    pass

import sys

import serial

from lucy.lucyhub import LucyHub

from argparse import ArgumentParser

PORT = "/dev/ttyUSB0"
BAUDRATE = 9600


def main():
    p = ArgumentParser(prog='Lucy')
    p.add_argument('-p', '--port', help='Serial Port', type=str, action='store', required=True, dest='port')
    p.add_argument('-b', '--baudrate', help='Baudrate for Serial Port', type='int', action='store', required=True,
                   dest='baudrate')
    p.parse_args()

    rtu_connection = serial.Serial(port=p.port, baudrate=p.baudrate, bytesize=8, parity='N', stopbits=1, xonxoff=0)
    lucy = LucyHub(rtu_connection)
    print("Lucy is online!")

    lucy.start()
    print("Waiting for user input")
    while True:
        msg = input_function("Command To Send: ")
        if msg == "close":
            lucy.stop()
            lucy.dump()
            sys.exit(0)


if __name__ == "__main__":
    main()
