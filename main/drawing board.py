from math import sqrt, pi, sin
from serial import Serial, PARITY_NONE, STOPBITS_ONE, EIGHTBITS
from json import load
from numpy import array, linspace, float64
from matplotlib.pyplot import pause, figure
from scipy.interpolate import splprep, splev
from keyboard import is_pressed
from time import sleep
from csv import writer
from sklearn.cluster import DBSCAN
from pandas import read_csv
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
SCALE_LENGTH: int = parameters["scale"]["length"]
SCALE_BREADTH: int = parameters["scale"]["breadth"]

AVERAGE_OF_READINGS: int = parameters["readings"]["average of"]
DELAY_BETWEEN_READINGS: int = parameters["readings"]["delay"]
SKIP_COUNT: int = parameters["readings"]["skip count"]

# constants related to plotting
X_MIN = 0
X_MAX = LENGTH - LENGTH_BUFFER
Y_MIN = 0
Y_MAX = BREADTH - BREADTH_BUFFER

# constants related to spine interpolation
SPLINE_MAXIMUM_POINTS: int = parameters["spline interpolation"]["maximum points"]
"""number of maximum points in a linear curve"""
SPLINE_MINIMUM_DISTANCE: int = parameters["spline interpolation"]["minimum distance"]
"""minimum distance to interpolate two points"""
SPLINE_MAXIMUM_DISTANCE: int = parameters["spline interpolation"]["maximum distance"]
"""maximum distance to interpolate two points"""

# constants for DBSCAN outlier detection algorithm
EPS: float = parameters["dbscan"]["eps"]
"""radius of neighbourhood"""
MINIMUM_SAMPLES: int = parameters["dbscan"]["minimum samples"]
"""minimum numberr of samples required in neighbourhood to be a inlier"""
INTERVAL: int = parameters["dbscan"]["interval"]

THRESHOLD: float = parameters["threshold"]

# constants related to keyboard instructions
CLEAR = "c"
INTERPOLATION_ACTIVATED = "i"
INTERPOLATION_DEACTIVATED = "a"
OUTLIER_REMOVAL = "o"
SAVE = "s"
IMPORT_FROM_CSV = "b"
BREAK_OUTLIER_DETECTION = "f"

# constants related to serial communication
PORT = parameters["serial"]["port"]
BAUD = parameters["serial"]["baud"]


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

counter = 0

a, b = 0, 0  # current points
x, y = [], []  # regular points
# points that are to be interpolated and then get added to the points
xToInterpolate, yToInterpolate = [], []
xInterpolated, yInterpolated = [], []  # interpolated points

fig = figure()
axis = fig.add_subplot(111)
axis.set_xlim(X_MIN, X_MAX)
axis.set_ylim(Y_MIN, Y_MAX)
fig.show()

(interpolatedLine,) = axis.plot([], [], "bo")
interpolate = False
outlier_detection = True
skip = SKIP_COUNT

def getSerialInput() -> str:
    """returns serial input without parsing"""
    tmp = ser.readline()
    tmp = tmp.replace(b"\n", b"").replace(b"\r", b"")
    tmp = tmp.decode("utf")
    return tmp


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


def mergeInterpolatedPoints() -> None:
    """adding interpolated points to general points and clearing interpolated and to_interpolate arrays"""
    global x, y, xInterpolated, yInterpolated, xToInterpolate, yToInterpolate
    x.extend(xInterpolated)
    y.extend(yInterpolated)
    xInterpolated, yInterpolated, xToInterpolate, yToInterpolate = [], [], [], []


def plotTheDrawing() -> None:
    """Function to plot the points"""
    axis.cla()
    axis.plot(x, y, "bo")
    axis.plot(xToInterpolate, yToInterpolate, "bo")
    axis.plot(xInterpolated, yInterpolated, "b-")
    axis.set_xlim(X_MIN, X_MAX)
    axis.set_ylim(Y_MIN, Y_MAX)
    fig.canvas.draw()


def removeOutliers() -> None:
    """removes outliers present in the plot using DBSCAN algorithm"""
    print(colored("OUTLIER DETECTION TRIGGERED", "green"))
    global x, y
    # mergeInterpolatedPoints()
    points = [[x[i], y[i]] for i in range(len(x))]
    if len(points) < MINIMUM_SAMPLES:
        return
    model = DBSCAN(eps=EPS, min_samples=MINIMUM_SAMPLES).fit(points)
    inliers = [
        points[record] for record in range(len(points)) if model.labels_[record] != -1
    ]
    x = [record[0] for record in inliers]
    y = [record[1] for record in inliers]
    plotTheDrawing()


def savePointsToCSV(fileName: str) -> None:
    """saves points to CSV file with fileName"""
    mergeInterpolatedPoints()
    points = [[x[i], y[i]] for i in range(len(x))]
    with open(fileName, "w") as file:
        writer(file).writerows(points)


def importCSVFileToPoints(fileName: str) -> None:
    """imports points present in the CSV file"""
    global x, y
    mergeInterpolatedPoints()
    points = read_csv(fileName, header=None, sep=",").iloc[:, 0:2].values
    x = [record[0] for record in points]
    y = [record[1] for record in points]
    plotTheDrawing()


def checkForKeyPress():
    global x, y, xToInterpolate, yToInterpolate, xInterpolated, yInterpolated
    global interpolate, outlier_detection
    if is_pressed(CLEAR):
        print(colored("CLEAR", "green"))
        x, y = [], []
        xToInterpolate, yToInterpolate = [], []
        xInterpolated, yInterpolated = [], []
        plotTheDrawing()
    elif is_pressed(INTERPOLATION_ACTIVATED) and not interpolate:
        interpolate = True
        print(colored("INTERPOLATION ACTIVATED", "green"))
    elif is_pressed(INTERPOLATION_DEACTIVATED) and interpolate:
        interpolate = False
        print(colored("INTERPOLATION DEACTIVATED", "green"))
        mergeInterpolatedPoints()
    elif is_pressed(OUTLIER_REMOVAL) and not outlier_detection:
        outlier_detection = True
        print(colored("OUTLIER DETECTION ACTIVATED", "green"))
        removeOutliers()
    elif is_pressed(SAVE):
        fileName: str = input(colored("Enter save file name: ", "purple")) + ".csv"
        savePointsToCSV(fileName)
    elif is_pressed(IMPORT_FROM_CSV):
        fileName: str = input(colored("Enter import file name: ", "purple")) + ".csv"
        importCSVFileToPoints(fileName)
    elif is_pressed(BREAK_OUTLIER_DETECTION) and outlier_detection:
        outlier_detection = False
        print(colored("OUTLIER DETECTION DEACTIVATED", "green"))


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
        checkForKeyPress()
        serialInput = getSerialInput()
        if not isInputValid(serialInput):
            continue
        # now we have a valid input
        dL, dB = decodeInput(serialInput)
        # dL, dB = 243, 243
        if not isReadingValid(dL, dB):
            continue
        # now we have a valid reading
        p, q = mapToCoordinate(dL, dB)
        m += p
        n += q
        validCoordinates += 1
    return (m // AVERAGE_OF_READINGS, n // AVERAGE_OF_READINGS)


def updateInterpolation() -> None:
    global xInterpolated, yInterpolated
    if interpolate and len(xToInterpolate) > 2:
        xNpArray = array(xToInterpolate, dtype=float64)
        yNpArray = array(yToInterpolate, dtype=float64)
        tck, _ = splprep([xNpArray, yNpArray], k=2, s=0)
        xInterpolated, yInterpolated = splev(
            linspace(0, 1, SPLINE_MAXIMUM_POINTS), tck
        )
    else:
        xInterpolated = []
        yInterpolated = []
        interpolatedLine.set_data(xInterpolated, yInterpolated)

def drawInterpolation() -> None:
    global xToInterpolate, yToInterpolate
    # appending new points to the coordinates
    if (a, b) not in set([(xToInterpolate[i], yToInterpolate[i]) for i in range(len(xToInterpolate))]):
        xToInterpolate.append(a)
        yToInterpolate.append(b)
    updateInterpolation()
    plotTheDrawing()


def drawPoint() -> None:
    """draws a point on the plot"""
    global x, y
    x.append(a)
    y.append(b)
    plotTheDrawing()


# driver code
while True:
    checkForKeyPress()
    if counter != 0 and counter % INTERVAL == 0 and outlier_detection:
        removeOutliers()
    a, b = getCoordinate()
    a -= LENGTH_BUFFER/2
    b -= BREADTH_BUFFER/2
    if a < 0 or b < 0:
        print(colored("Error: Wrong coordinates!", "red"))
    if interpolate:
        if skip > 0:
            skip -= 1
            continue
        drawInterpolation()
        skip = SKIP_COUNT
    else:
        drawPoint()

    counter += 1
    print(colored(f"Point: ({a}, {b})", "blue"))
    pause(0.001)