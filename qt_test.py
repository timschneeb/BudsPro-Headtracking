import math
import sys

import bluetooth
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUiType
from PyQt5 import QtGui, QtWidgets

from transformations import euler_from_quaternion

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import animation
from pyquaternion import Quaternion

from mpl_toolkits.mplot3d import Axes3D

import numpy as np

from SpatialSensorManager import SpatialSensorManager

Ui_MainWindow, QMainWindow = loadUiType('plot.ui')

class Kinematic(Ui_MainWindow, QMainWindow):

    def __init__(self):
        super(Kinematic, self).__init__()
        self.setupUi(self)

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111,projection = '3d')
        self.fig.tight_layout()
        self.ax.view_init(40, -45)

        # dashed coordinate system
        self.ax.plot([0,1], [0,0], [0,0], label='$X_0$', linestyle="dashed")
        self.ax.plot([0,0], [0,-1], [0,0], label='$Y_0$', linestyle="dashed")
        self.ax.plot([0,0], [0,0], [0,1], label='$Z_0$', linestyle="dashed")

        self.ax.set_xlim3d(-8,8)
        self.ax.set_ylim3d(-8,8)
        self.ax.set_zlim3d(-8,8)

        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        self.ax.scatter(0,0,0, color='k') # black origin dot

        self.canvas = FigureCanvas(self.fig)
        self.mplvl.layout().addWidget(self.canvas)

        self.quat = [0,0,0,0]
        service_matches = bluetooth.find_service(uuid="00001101-0000-1000-8000-00805F9B34FB", address=str("64:03:7F:2E:2B:3A"))

        port = host = None
        for match in service_matches:
            if match["name"] == "GEARMANAGER" or match["name"] == b"GEARMANAGER":
                port = match["port"]
                host = match["host"]
                break

        if port is None or host is None:
            print("Couldn't find the proprietary RFCOMM service")
            sys.exit(1)

        print("RFCOMM interface found. Establishing connection...")

        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((host, port))

        print("Connected to device.")

        sensor = SpatialSensorManager(sock, self.__spatial_sensor_callback, True, False)
        sensor.attach()

        self.ani = animation.FuncAnimation(self.fig, self.data_gen, init_func=self.setup_plot, blit=True)

    def __spatial_sensor_callback(self, quat, mgr):
        print(f"x={quat[0]}, y={quat[1]}, z={quat[2]}, w={quat[3]}")
        self.quat = quat

    def quaternion_to_euler_angle_vectorized1(self, w, x, y, z):
        ysqr = y * y

        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + ysqr)
        X = np.degrees(np.arctan2(t0, t1))

        t2 = +2.0 * (w * y - z * x)
        t2 = np.where(t2 > +1.0, +1.0, t2)
        # t2 = +1.0 if t2 > +1.0 else t2

        t2 = np.where(t2 < -1.0, -1.0, t2)
        # t2 = -1.0 if t2 < -1.0 else t2
        Y = np.degrees(np.arcsin(t2))

        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (ysqr + z * z)
        Z = np.degrees(np.arctan2(t3, t4))

        return X, Y, Z


    def setup_plot(self):

        self.ax.legend(loc='best')

        for line in self.lines:
            line.set_data([], [])
            line.set_3d_properties([])

        #self.vek = self.ax.quiver(0, 0, 0, 0, 0, 0, label='$g \cdot R$', pivot="tail", color="black")

        return self.vek,

    def data_gen(self, i):
        quaternion = (self.quat[3], self.quat[0], self.quat[1], self.quat[2])
        (x,y,z) = self.quaternion_to_euler_angle_vectorized1(self.quat[3], self.quat[0], self.quat[1], self.quat[2])
        #euler = euler_from_quaternion(quaternion)
        #yaw = euler[2]
        #new_x = np.sin(yaw)
        #new_y = np.cos(yaw)
        self.vek = self.ax.quiver(0, 0, 0, x, y, z, color='b')

        #b = self.bslider.value() / 100

        #vx, vy, vz = np.cos(b), np.sin(b), 0

        #self.vek = self.ax.quiver(0, 0, 0, vx, vy, vz, label='$g \cdot R$', pivot="tail", color="black")

        self.canvas.draw()

        return self.vek,

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    main = Kinematic()
    main.show()

    sys.exit(app.exec_())