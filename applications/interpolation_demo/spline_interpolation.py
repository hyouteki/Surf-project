import numpy as np
from matplotlib.pyplot import pause, figure, subplots
from scipy.interpolate import splprep, splev
from math import sqrt, pi, sin
from serial import Serial, PARITY_NONE, STOPBITS_ONE, EIGHTBITS
from json import load
from time import sleep
# from random import randrange
from termcolor import colored

"""
units:
    length = mm
    angle  = degree
    delay  = ms
"""

with open("parameters.json") as file:
    parameters = load(file)

# constraints (ultrasonic)
EFFECTUAL_ANGLE: int = parameters["proximity sensor"]["effectual angle"]
MINIMUM_DISTANCE: int = parameters["proximity sensor"]["minimum distance"]
MAXIMUM_DISTANCE: int = parameters["proximity sensor"]["maximum distance"]

# model parameters
LENGTH: int = parameters["workspace"]["length"]
BREADTH: int = parameters["workspace"]["breadth"]
LENGTH_BUFFER: int = parameters["workspace"]["length buffer"]
BREADTH_BUFFER: int = parameters["workspace"]["breadth buffer"]
THETA_LENGTH: int = EFFECTUAL_ANGLE
THETA_BREADTH: int = EFFECTUAL_ANGLE
AVERAGE_OF_READINGS: int = parameters["readings"]["average of"]
DELAY_BETWEEN_READINGS: int = parameters["readings"]["delay"]
SKIP_COUNT: int = parameters["readings"]["skip count"]

# constants related to serial communication
PORT = parameters["serial"]["port"]
BAUD = parameters["serial"]["baud"]

# constants related to plotting
X_MIN = 0
X_MAX = LENGTH - LENGTH_BUFFER
Y_MIN = 0
Y_MAX = BREADTH - BREADTH_BUFFER

# helper methods
degreeToRadian = lambda degree: degree * pi / 180
sq = lambda n: n * n
distanceBetweenPoints = lambda a1, b1, a2, b2: sqrt(sq(a1 - a2) + sq(b1 - b2))

# derived model parameters
COUNTER_TO_LENGTH: int = LENGTH / (2 * sin(degreeToRadian(THETA_LENGTH)))
COUNTER_TO_BREADTH: int = BREADTH / (2 * sin(degreeToRadian(THETA_BREADTH)))

# serial port initialization
ser = Serial(
    port=PORT,
    baudrate=BAUD,
    parity=PARITY_NONE,
    stopbits=STOPBITS_ONE,
    bytesize=EIGHTBITS,
    timeout=0,
)

skip = SKIP_COUNT

fig = figure()
axis = fig.add_subplot(111)
axis.set_xlim(X_MIN, X_MAX)
axis.set_ylim(Y_MIN, Y_MAX)
fig.show()

def getSerialInput() -> str:
    """returns serial input without parsing"""
    tmp = ser.readline()
    tmp = tmp.replace(b"\n", b"").replace(b"\r", b"")
    tmp = tmp.decode("utf")
    return tmp
    # return f"{randrange(350, 450)},{randrange(350, 450)},"
    # return "450,450,"

def decodeInput(tmp: str):
    """decodes input and returns a 2d point"""
    tmp = tmp[:-1]
    a: int = int(tmp[: tmp.index(",")])
    b: int = int(tmp[tmp.index(",") + 1 :])
    return (a, b)

def isInputValid(tmp: str) -> bool:
    """checks whether input is valid or not"""
    return (
        sum([1 for i in tmp.split(",") if i != ""]) == 2
        and sum([1 for i in tmp if i == ","]) == 2
    )

def isReadingValid(dL: int, dB: int) -> bool:
    """check whether the provided distances are valid or not in accordance with specified parameters"""
    dLMin: int = COUNTER_TO_LENGTH + BREADTH_BUFFER / 2
    dLMax: int = sqrt(
        sq(COUNTER_TO_LENGTH + BREADTH - BREADTH_BUFFER / 2)
        + sq(LENGTH / 2 - LENGTH_BUFFER / 2)
    )
    dBMin: int = COUNTER_TO_BREADTH + LENGTH_BUFFER / 2
    dBMax: int = sqrt(
        sq(COUNTER_TO_BREADTH + LENGTH - LENGTH_BUFFER / 2)
        + sq(BREADTH / 2 - BREADTH_BUFFER / 2)
    )
    return dL >= dLMin and dL <= dLMax and dB >= dBMin and dB <= dBMax

def mapToCoordinate(dL: int, dB: int):
    """maps the provided distances to a interger coordinate/point in the first quadrant of the cartesian plane"""
    p: float = dL
    q: float = LENGTH / 2
    r: float = BREADTH + COUNTER_TO_LENGTH
    u: float = dB
    v: float = LENGTH + COUNTER_TO_BREADTH
    w: float = BREADTH / 2
    e: float = sqrt(sq(q - v) + sq(r - w))
    f: float = (sq(p) - sq(u) + sq(e)) / (2 * e)
    g: float = sqrt(sq(p) - sq(f))
    return (
        int((f / e) * (v - q) + (g / e) * (w - r) + q) % LENGTH,
        int((f / e) * (w - r) - (g / e) * (v - q) + r) % BREADTH,
    )

def getCoordinate():
    validCoordinates: int = 0
    m, n = 0, 0
    while validCoordinates < AVERAGE_OF_READINGS:
        sleep(0.02)
        serialInput = getSerialInput()
        if not isInputValid(serialInput):
            continue
        # now we have a valid input
        dL, dB = decodeInput(serialInput)
        if not isReadingValid(dL, dB):
            continue
        # now we have a valid reading
        p, q = mapToCoordinate(dL, dB)
        m += p
        n += q
        validCoordinates += 1
    return (m // AVERAGE_OF_READINGS, n // AVERAGE_OF_READINGS)

x, y = [], []  # regular points are stored here
# interpolated points are stored in this
xInterpolated, yInterpolated = [], []

(interpolatedLine,) = axis.plot([], [], "b-", label="Interpolated Points")

def draw() -> None:
    axis.set_xlabel("X")
    axis.set_ylabel("Y")
    axis.set_title("Spline Interpolation Demo")
    axis.legend()
    axis.set_xlim(X_MIN, X_MAX)
    axis.set_ylim(Y_MIN, Y_MAX)

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


def addPoint(a, b):
    global xInterpolated, yInterpolated
    if (a, b) not in set([(x[i], y[i]) for i in range(len(x))]):
        x.append(a)
        y.append(b)

        update_interpolation()

        axis.cla()
        axis.plot(x, y, "bo", label="Discrete Points")
        axis.plot(xInterpolated, yInterpolated, "b-", label="Interpolated Points")
        draw()
        fig.canvas.draw()

def onclick(event):
    if event.button == 1:
        addPoint(event.xdata, event.ydata)

# driver code
while True:
    a, b = getCoordinate()
    a -= LENGTH_BUFFER/2
    b -= BREADTH_BUFFER/2
    if a < 0 or b < 0:
        print(colored("Error: Wrong coordinates!", "red"))
    if skip > 0:
        skip -= 1
        continue
    addPoint(a, b)
    print(colored(f"Point: ({a}, {b})", "blue"))
    skip = SKIP_COUNT
    pause(0.001)