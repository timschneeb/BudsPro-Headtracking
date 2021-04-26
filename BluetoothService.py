import struct
from threading import Thread
import Crc16


class BluetoothService:

    def __init__(self, socket, message_callback=None, debug=False):
        # Constants
        self.MSG_SIZE_CRC = 2
        self.MSG_SIZE_ID = 1
        self.MSG_SIZE_MARKER = 1
        self.MSG_SIZE_TYPE = 1
        self.MSG_SIZE_BYTES = 1
        self.MSG_SOM_MARKER = 0xFD
        self.MSG_EOM_MARKER = 0xDD

        # Member variables
        self.message_cb = message_callback
        self.debug = debug
        self.socket = socket
        self.thread = Thread(target=self.__run)
        self.thread.start()

    def __run(self):
        try:
            while True:
                data = self.socket.recv(1024)
                if len(data) == 0:
                    continue

                if self.debug:
                    print(">> INCOMING: " + bytearray(data).hex(sep=' '))

                if data[0] != self.MSG_SOM_MARKER:
                    print("Warning: Invalid SOM received, corrupted message")
                    continue

                if self.message_cb is not None:
                    self.message_cb(data)

        except IOError:
            pass

    def __size(self, payload_length):
        return self.MSG_SIZE_ID + payload_length + self.MSG_SIZE_CRC

    def __totalPacketSize(self, payload_length):
        return self.__size(payload_length) + (self.MSG_SIZE_MARKER * 2) + self.MSG_SIZE_TYPE + self.MSG_SIZE_BYTES

    def sendPacket(self, msg_id, payload, is_response=False, is_fragment=False):
        b = bytearray(self.__totalPacketSize(len(payload)))
        b[0] = self.MSG_SOM_MARKER

        header_b = 0
        if is_fragment:
            header_b = (header_b | 32)

        if is_response:
            header_b = (header_b | 16)

        b[1] = self.__size(len(payload))
        b[2] = header_b
        b[3] = msg_id

        b[4:4 + len(payload)] = payload

        crc_data = bytearray(self.__size(len(payload)) - self.MSG_SIZE_CRC)
        crc_data[0] = msg_id
        crc_data[1:1 + len(payload)] = payload

        crc16 = Crc16.crc16_ccitt(crc_data)
        b[len(payload) + 4] = crc16 & 255
        b[len(payload) + 5] = (crc16 >> 8) & 255
        b[len(payload) + 6] = self.MSG_EOM_MARKER

        if self.debug:
            print("<< OUTGOING: " + bytearray(b).hex(sep=' '))

        self.socket.send(bytes(b))
