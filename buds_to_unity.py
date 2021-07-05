# -*- coding: utf-8 -*-
"""
Created on Tue Jun 22 23:13:48 2021

@author: JY
"""

import time
import socket

import bluetooth
import sys
import argparse

from SpatialSensorManager import SpatialSensorManager

SENDING_STR = "0.00,0.00,0.00,0.00"
import numpy as np

def quaternion_to_euler_angle_vectorized1(w, x, y, z):
    ysqr = y * y

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    X = np.degrees(np.arctan2(t0, t1))

    t2 = +2.0 * (w * y - z * x)
    t2 = np.where(t2>+1.0,+1.0,t2)
    #t2 = +1.0 if t2 > +1.0 else t2

    t2 = np.where(t2<-1.0, -1.0, t2)
    #t2 = -1.0 if t2 < -1.0 else t2
    Y = np.degrees(np.arcsin(t2))

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    Z = np.degrees(np.arctan2(t3, t4))

    return X, Y, Z 


def __spatial_sensor_callback(quaternion):
    global SENDING_STR
    # This parameter is a float list describing a raw quaternion (4D vector)
    # The values are ordered like this: x, y, z, w
    
    euler_ = quaternion_to_euler_angle_vectorized1(quaternion[3], quaternion[0], quaternion[1], quaternion[2])
    SENDING_STR = f"{euler_[0]:0.03f},{euler_[1]:0.03f},{euler_[2]:0.03f} | "
    SENDING_STR += f"{quaternion[0]},{quaternion[1]},{quaternion[2]},{quaternion[3]}"
    print(SENDING_STR)
    
    # Conversion examples (C#): https://github.com/ThePBone/GalaxyBudsClient/blob/master/GalaxyBudsClient/Utils/QuaternionExtensions.cs#L48

# UDP part
UDP_IP = "127.0.0.1"
UDP_PORT = 12562
MESSAGE = "Hello, World!"

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)

data_type = "dffffffffffqd"

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP


# buds part
mac = "64:03:7F:85:D3:0C"
verbose = True
trace = False


if verbose:
    print(str(bluetooth.lookup_name(mac)))
    print("Searching for RFCOMM interface...")

service_matches = bluetooth.find_service(uuid="00001101-0000-1000-8000-00805F9B34FB", address=mac)

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
        udp_sock.sendto(bytes(SENDING_STR, "utf-8"), (UDP_IP, UDP_PORT))
        time.sleep(0.01)

except KeyboardInterrupt:
    if sensor is not None:
        sensor.detach()
        
        #%%
# simple inquiry example
import bluetooth

nearby_devices = bluetooth.discover_devices(lookup_names=True)
print("Found {} devices.".format(len(nearby_devices)))

for addr, name in nearby_devices:
    print("  {} - {}".format(addr, name))