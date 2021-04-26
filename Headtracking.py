#!/usr/bin/env python3

"""
A python script to get battery level from Samsung Galaxy Buds devices
"""

# License: MIT
# Author: @ThePBone
# 06/30/2020
import time

import bluetooth
import sys
import argparse

from SpatialSensorManager import SpatialSensorManager


def __spatial_sensor_callback(quaternion):
    # This parameter is a float list describing a raw quaternion (4D vector)
    # The values are ordered like this: x, y, z, w
    print(f"x={quaternion[0]}, y={quaternion[1]}, z={quaternion[2]}, w={quaternion[3]}")
    # Conversion examples (C#): https://github.com/ThePBone/GalaxyBudsClient/blob/master/GalaxyBudsClient/Utils/QuaternionExtensions.cs#L48


def main():
    parser = argparse.ArgumentParser(description='Stream head-tracking data from the Galaxy Buds Pro')
    parser.add_argument('mac', metavar='mac-address', type=str, nargs=1,
                        help='MAC-Address of your Buds')
    parser.add_argument('-v', '--verbose', action='store_true', help="Print debug information")
    parser.add_argument('-t', '--trace', action='store_true', help="Trace Bluetooth serial traffic")
    args = parser.parse_args()

    verbose = args.verbose
    trace = args.trace

    if verbose:
        print(str(bluetooth.lookup_name(args.mac[0])))
        print("Searching for RFCOMM interface...")

    service_matches = bluetooth.find_service(uuid="00001101-0000-1000-8000-00805F9B34FB", address=str(args.mac[0]))

    port = host = None
    for match in service_matches:
        if match["name"] == b"GEARMANAGER":
            port = match["port"]
            host = match["host"]
            break

    if port is None or host is None:
        print("Couldn't find the proprietary RFCOMM service")
        sys.exit(1)

    if verbose:
        print("RFCOMM interface found. Establishing connection...")

    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((host, port))

    if verbose:
        print("Connected to device.")

    sensor = None
    try:
        sensor = SpatialSensorManager(sock, __spatial_sensor_callback, verbose, trace)
        sensor.attach()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        if sensor is not None:
            sensor.detach()


if __name__ == "__main__":
    main()
