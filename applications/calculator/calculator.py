from math import sqrt, pi, sin
from serial import Serial, PARITY_NONE, STOPBITS_ONE, EIGHTBITS
from json import load
from time import sleep
from os import system

"""
units:
    length = mm
    angle  = degree
    delay  = ms
"""

with open("parameters.json") as file:
    parameters = load(file)

with open("book.json") as file:
    book = load(file)

# constraints (ultrasonic)
EFFECTUAL_ANGLE: int = parameters["proximity sensor"]["effectual angle"]
MINIMUM_DISTANCE: int = parameters["proximity sensor"]["minimum distance"]
MAXIMUM_DISTANCE: int = parameters["proximity sensor"]["maximum distance"]

# model parameters
LENGTH: int = parameters["workspace"]["length"]
BREADTH: int = parameters["workspace"]["breadth"]
THETA_LENGTH: int = EFFECTUAL_ANGLE
THETA_BREADTH: int = EFFECTUAL_ANGLE
AVERAGE_OF_READINGS: int = parameters["readings"]["average of"]
DELAY_BETWEEN_READINGS: int = parameters["readings"]["delay"]

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

expression = ""


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
    dLMin: int = COUNTER_TO_LENGTH
    dLMax: int = sqrt(sq(COUNTER_TO_LENGTH + BREADTH) + sq(LENGTH / 2))
    dBMin: int = COUNTER_TO_BREADTH
    dBMax: int = sqrt(sq(COUNTER_TO_BREADTH + LENGTH) + sq(BREADTH / 2))
    return dL >= dLMin and dL <= dLMax and dB >= dBMin and dB <= dBMax


def mergeInterpolatedPoints() -> None:
    """adding interpolated points to general points and clearing interpolated and to_interpolate arrays"""
    global x, y, xInterpolated, yInterpolated, xToInterpolate, yToInterpolate
    x.extend(xInterpolated)
    y.extend(yInterpolated)
    xInterpolated, yInterpolated, xToInterpolate, yToInterpolate = [], [], [], []


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


def mapToTile(a, b):
    for page in book:
        w = book[page][0]
        x = book[page][1]
        y = book[page][2]
        z = book[page][3]
        if w <= a and a <= x and y <= b and b <= z:
            return page
    return "~"


def addToCalculator(a, b):
    global expression
    char = mapToTile(a, b)
    if char == "~":
        print("Wrong coordinates!")
    elif char == "AC":
        expression = ""
    elif char == "C":
        if len(expression) > 0:
            expression = expression[:-1]
    elif char == "=":
        system(f"python compute.py {expression}")
    else:
        expression += char


# driver code
while True:
    a, b = getCoordinate()
    addToCalculator(a, b)
