import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
from math import sqrt, pi, sin
from serial import Serial, PARITY_NONE, STOPBITS_ONE, EIGHTBITS
from json import load
from time import sleep

x, y = [], []  # regular points are stored here
# interpolated points are stored in this
xInterpolated, yInterpolated = [], []

figure, axis = plt.subplots()

(interpolatedLine,) = axis.plot([], [], "b-", label="Interpolated Points")


def draw() -> None:
    axis.set_xlabel("X")
    axis.set_ylabel("Y")
    axis.set_title("Spline Interpolation")
    axis.legend()
    axis.set_xlim(0, 10)
    axis.set_ylim(0, 10)


interpolate = True


def update_interpolation():
    global xInterpolated, yInterpolated

    if interpolate and len(x) > 2:
        """condition based on differences in the readings
        is to be put, to check if to interpolate(set
        interpolate=True) or not(set interpolate=False)"""

        """ to check if the number of data points is 
        sufficient for cubic spline interpolation (k=3)"""
        if len(x) >= 3:
            xNPArray = np.array(x, dtype=np.float64)
            yNPArray = np.array(y, dtype=np.float64)
            tck, _ = splprep([xNPArray, yNPArray], k=2, s=0)
            xInterpolated, yInterpolated = splev(np.linspace(0, 1, 100), tck)
        else:
            xInterpolated = []
            yInterpolated = []
    else:
        xInterpolated = []
        yInterpolated = []
        interpolatedLine.set_data(xInterpolated, yInterpolated)


def onclick(event):
    global xInterpolated, yInterpolated
    if event.button == 1 and (event.xdata, event.ydata) not in set([(x[i], y[i]) for i in range(len(x))]):
        x.append(event.xdata)
        y.append(event.ydata)

        update_interpolation()

        axis.cla()
        axis.plot(x, y, "bo", label="Discrete Points")
        axis.plot(xInterpolated, yInterpolated, "b-", label="Interpolated Points")
        draw()
        figure.canvas.draw()


figure.canvas.mpl_connect("button_press_event", onclick)

draw()
plt.show()