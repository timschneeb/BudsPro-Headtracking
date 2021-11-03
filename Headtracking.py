#!/usr/bin/env python3

"""
A python script to stream head-tracking data from the Samsung Galaxy Buds Pro
"""

# License: MIT
# Author: @ThePBone
# 04/26/2021
import os
import signal
import time

import bluetooth
import sys
import argparse

from SpatialSensorManager import SpatialSensorManager
from time import process_time_ns

timeAtLastEvent = -1
benchmarkHistory = []
doBenchmark = False
doBenchmarkAfterNIterations = 0
benchmarkCount = 100
benchmarkIteration = 0


def __spatial_sensor_callback(quaternion, sensor_manager):
    global timeAtLastEvent, benchmarkHistory, doBenchmark, benchmarkCount,\
        benchmarkIteration, doBenchmarkAfterNIterations
    if sensor_manager.service.isDisposing:
        return

    # This parameter is a float list describing a raw quaternion (4D vector)
    # The values are ordered like this: x, y, z, w
    # Conversion examples (C#): https://github.com/ThePBone/GalaxyBudsClient/blob/master/GalaxyBudsClient/Utils/QuaternionExtensions.cs#L48

    if not doBenchmark:
        print(f"x={quaternion[0]}, y={quaternion[1]}, z={quaternion[2]}, w={quaternion[3]}")
        return

    if timeAtLastEvent >= 0 and benchmarkIteration >= doBenchmarkAfterNIterations:
        benchmarkHistory.append((process_time_ns() - timeAtLastEvent) / 1e+6)

    if len(benchmarkHistory) >= benchmarkCount - 1:
        print("====== BENCHMARK DONE ======")
        if doBenchmarkAfterNIterations > 0:
            print("Benchmark launched after skipping " + str(doBenchmarkAfterNIterations) + " frames")
        print("Motion frames received: " + str(len(benchmarkHistory) + 1))
        print("Average time between frames: " + str(round(sum(benchmarkHistory) / len(benchmarkHistory), 6)) + "ms")
        print("Minimum time between frames: " + str(min(benchmarkHistory)) + "ms")
        print("Maximum time between frames: " + str(max(benchmarkHistory)) + "ms")
        sensor_manager.detach()
        sensor_manager.service.close()

    benchmarkIteration += 1
    timeAtLastEvent = process_time_ns()


def main():
    global timeAtLastEvent, benchmarkHistory, doBenchmark, benchmarkCount, doBenchmarkAfterNIterations
    parser = argparse.ArgumentParser(description='Stream head-tracking data from the Galaxy Buds Pro')
    parser.add_argument('mac', metavar='mac-address', type=str, nargs=1,
                        help='MAC-Address of your Buds')
    parser.add_argument('-b', '--benchmark', action='store_true', help="Perform benchmark")
    parser.add_argument('--benchmark-count', metavar="n", default=[benchmarkCount], nargs=1, type=int,
                        help="Stop benchmark after benchmarking N frames")
    parser.add_argument('--benchmark-delay', metavar="n", default=[doBenchmarkAfterNIterations], nargs=1, type=int,
                        help="Start benchmark after receiving/skipping N frames (to wait until the connection stabilizes)")
    parser.add_argument('-v', '--verbose', action='store_true', help="Print debug information")
    parser.add_argument('-t', '--trace', action='store_true', help="Trace Bluetooth serial traffic")
    args = parser.parse_args()

    doBenchmark = args.benchmark
    benchmarkCount = args.benchmark_count[0]
    doBenchmarkAfterNIterations = args.benchmark_delay[0]
    verbose = args.verbose
    trace = args.trace

    if verbose:
        print(str(bluetooth.lookup_name(args.mac[0])))
        print("Searching for RFCOMM interface...")

    service_matches = bluetooth.find_service(uuid="00001101-0000-1000-8000-00805F9B34FB", address=str(args.mac[0]))

    port = host = None
    for match in service_matches:
        if match["name"] == "GEARMANAGER" or match["name"] == b"GEARMANAGER":
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

        while not sensor.service.isDisposing:
            time.sleep(1)

    except KeyboardInterrupt:
        if sensor is not None:
            sensor.detach()


if __name__ == "__main__":
    main()
