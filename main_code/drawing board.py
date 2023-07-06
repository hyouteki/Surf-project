from numpy import array, linspace, float64
from matplotlib.pyplot import pause, figure
from scipy.interpolate import splprep, splev
from keyboard import is_pressed
from time import sleep
from math import sqrt
from serial import Serial, PARITY_NONE, STOPBITS_ONE, EIGHTBITS

# constants related to the model
LENGTH: int = 100
BREADTH: int = 100
DELAY_BETWEEN_READINGS: float = 0.2

# constants related to plotting
X_MIN = -10
X_MAX = LENGTH+10
Y_MIN = -10
Y_MAX = BREADTH+10

# constants related to spine interpolation
MAX_POINTS: int = 5
""" number of maximum points in a linear curve """ 
MIN_DIS: int = 5
""" minimum distance to interpolate two points """ 

# constants related to keyboard instructions
CLEAR = 'c'
INTERPOLATE = 'i'

# constants related to serial communication
PORT = "COM3"
BAUD = 9600

# serial port initialization
ser = Serial(
    port=PORT,
    baudrate=BAUD,
    parity=PARITY_NONE,
    stopbits=STOPBITS_ONE,
    bytesize=EIGHTBITS,
    timeout=0)

a, b = 0, 0 # current points 
x, y = [], [] # regular points
# points that are to be interpolated and then get added to the points
xToInterpolate, yToInterpolate = [], []
xInterpolated, yInterpolated = [], [] # interpolated points

fig = figure()
axis = fig.add_subplot(111)
axis.set_xlim(X_MIN, X_MAX)
axis.set_ylim(Y_MIN, Y_MAX)
fig.show()

interpolatedLine, = axis.plot([], [], 'bo')
interpolate = False

def getInput() -> str:
    """ returns serial input without parsing"""
    tmp = ser.readline()
    tmp = tmp.replace(b'\n', b'').replace(b'\r', b'')
    tmp = tmp.decode('utf')
    return tmp

def decodeInput(tmp: str):
    """ decodes input and returns a 2d point """
    tmp = tmp[:-1] 
    a: int = int(tmp[:tmp.index(',')])
    b: int = int(tmp[tmp.index(',')+1:])
    return (a, b)

def isInputValid(tmp: str) -> bool:
    """ checks whether input is valid or not """
    return sum([1 for z in tmp if z == ',']) == 2 and len(tmp) >= 4

sq = lambda n: n*n

def distanceBetweenPoints(a1, b1, a2, b2):
    return sqrt(sq(abs(a1-a2))+sq(abs(b1-b2)))

def update_interpolation() -> None:
    global xInterpolated, yInterpolated
    if interpolate and len(xToInterpolate) > 2:
        """ if distance is less than min distance then return """
        if (distanceBetweenPoints(xToInterpolate[-1], yToInterpolate[-1], 
                                  xToInterpolate[-2], yToInterpolate[-2])) < MIN_DIS: return
        # to check if the number of data points is sufficient for cubic spline interpolation (k=3)
        if len(xToInterpolate) >= 3:  
            xNpArray = array(xToInterpolate, dtype=float64)
            yNpArray = array(yToInterpolate, dtype=float64)
            tck, _ = splprep([xNpArray, yNpArray], k=2, s=0)
            xInterpolated, yInterpolated = splev(linspace(0, 1, MAX_POINTS), tck)
        else:
            xInterpolated = []
            yInterpolated = []
    else:
        xInterpolated = []
        yInterpolated = []
        interpolatedLine.set_data(xInterpolated, yInterpolated)

def drawInterpolation() -> None:
    global xToInterpolate, yToInterpolate
    # appending new points to the coordinates
    xToInterpolate.append(a)
    yToInterpolate.append(b)
    # removing duplicate points
    tmp = set([(xToInterpolate[i], yToInterpolate[i]) for i in range(len(xToInterpolate))])
    xToInterpolate, yToInterpolate = [], []
    for t in tmp:
        xToInterpolate.append(t[0])
        yToInterpolate.append(t[1])
    update_interpolation()
    plotTheDrawing()

def drawPoint() -> None:
    global x, y
    x.append(a)
    y.append(b)
    plotTheDrawing()
    
def plotTheDrawing() -> None:
    axis.plot(x, y, 'bo') 
    axis.plot(xToInterpolate, yToInterpolate, 'bo') 
    axis.plot(xInterpolated, yInterpolated, 'bo')
    fig.canvas.draw()

def mergeInterpolatedPoints() -> None:
    """ adding interpolated points to general points 
    and clearing interpolated and to_interpolate arrays """
    global x, y, xInterpolated, yInterpolated, xToInterpolate, yToInterpolate
    x.extend(xInterpolated)
    y.extend(yInterpolated)
    xInterpolated, yInterpolated, xToInterpolate, yToInterpolate = [], [], [], []

# driver code
while True:
    if is_pressed(CLEAR):
        print("clear")
        x, y = [], []
        xToInterpolate, yToInterpolate, xInterpolated, yInterpolated = [], [], [], []
        axis.cla()
        axis.set_xlim(X_MIN, X_MAX)
        axis.set_ylim(Y_MIN, Y_MAX)
    if is_pressed(INTERPOLATE):
        # interpolation is on or off until key pressed again
        interpolate = not interpolate
        print(f"Interpolate = {interpolate}")
        if not interpolate:
            mergeInterpolatedPoints()
    got = getInput()
    if isInputValid(got):
        a, b = decodeInput(got)
        print(a, b) 
        if interpolate:
            drawInterpolation()
        else:
            drawPoint()
    sleep(DELAY_BETWEEN_READINGS)
    pause(0.001)