from BluetoothService import BluetoothService
from RepeatedTimer import RepeatedTimer

import struct

class SpatialSensorManager:
    def __init__(self, socket, data_callback, verbose=False, debug=False):
        # Constants
        self.CID_ATTACH = 0
        self.CID_DETACH = 1
        self.CID_ATTACH_ACK = 2
        self.CID_DETACH_ACK = 3
        self.CID_KEEP_ALIVE = 4
        self.CID_WEAR_ON_OFF = 5

        self.DID_BUDGRV = 32
        self.DID_GYROCAL = 35
        self.DID_SENSOR_STUCK = 36
        self.DID_WEAR_OFF = 34
        self.DID_WEAR_ON = 33

        self.MSG_SPATIAL_AUDIO_ENABLE = 124
        self.MSG_SPATIAL_AUDIO_DATA = 194
        self.MSG_SPATIAL_AUDIO_CONTROL = 195

        # Member variables
        self.data_cb = data_callback
        self.verbose = verbose
        self.service = BluetoothService(socket, self.__onMessageReceived, debug)
        self.timer = None

    def attach(self):
        self.service.sendPacket(self.MSG_SPATIAL_AUDIO_ENABLE, bytes(1))
        self.service.sendPacket(self.MSG_SPATIAL_AUDIO_CONTROL, bytes(self.CID_ATTACH))
        self.timer = RepeatedTimer(2, self.__keepAlive)

    def detach(self):
        self.service.sendPacket(self.MSG_SPATIAL_AUDIO_CONTROL, bytes(self.CID_DETACH))
        self.service.sendPacket(self.MSG_SPATIAL_AUDIO_ENABLE, bytes(0))
        self.timer.stop()

    def __keepAlive(self):
        self.service.sendPacket(self.MSG_SPATIAL_AUDIO_CONTROL, bytes(self.CID_KEEP_ALIVE))

    def __extract_data(self, byte, i, i2, z):
        if len(byte) >= i + i2:
            i4 = 0
            i3 = 0
            if z:
                while i4 < i2:
                    i3 += (byte[i + i4] & 255) << (((i2 - 1) - i4) * 8)
                    i4 += 1
            else:
                while i4 < i2:
                    i3 += (byte[i + i4] & 255) << (i4 * 8)
                    i4 += 1
            return i3
        else:
            return -2

    def __onMessageReceived(self, data):
        if data[3] == self.MSG_SPATIAL_AUDIO_CONTROL:
            cid = data[4]
            if self.verbose and cid == self.CID_ATTACH_ACK:
                print("Attach successful (ACK)")
            elif self.verbose and cid == self.CID_DETACH_ACK:
                print("Detach successful (ACK)")
        elif data[3] == self.MSG_SPATIAL_AUDIO_DATA:
            event = data[4]
            if event == self.DID_SENSOR_STUCK and self.verbose:
                print("Warning: Sensor stuck")
            elif event == self.DID_GYROCAL and self.verbose:
                # For more information refer to https://github.com/ThePBone/GalaxyBudsClient/blob/master/GalaxyBudsClient/Message/Decoder/SpatialAudioDataParser.cs#L56
                print("Received gyro bias info from device")
            elif event == self.DID_BUDGRV:
                
                payload = data[5:len(data) - 3]
                input =  payload[:-1]
                if len(input)==8:
                    quaternion =[ one/10000.0 for one in struct.unpack('hhhh', payload[:-1])]
                    if self.data_cb is not None:
                        self.data_cb(quaternion)
                else:
                    if self.verbose:
                        print("diff length: ", len(input))
                

                

