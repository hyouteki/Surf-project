# imports
from turtle import *
from time import sleep
from keyboard import is_pressed
import serial

# model parameters
length: int = 100
breadth: int = 100
scale_l: int = 2
scale_b: int = 2
marker_color: str = "black"
dot_thickness: int = 10
delay_between_readings: float = 0.3

# variable initialization
ser = serial.Serial(
    port='COM3',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0)

cur = Turtle()

# drawing board initialization
setup(length*scale_l, breadth*scale_b)
cur.hideturtle()

# methods
def draw(point) -> None:
    x, y = point
    cur.penup()
    cur.goto(x-length*scale_l/2, y-breadth*scale_b/2)
    cur.pendown()
    cur.dot(dot_thickness, marker_color)

def get_input() -> str:
    x = ser.readline()
    x = x.replace(b'\n', b'').replace(b'\r', b'')
    x = x.decode('utf')
    return x

def decode_input(x: str, inverse_a: bool = False, inverse_b: bool = False) -> None:
    x = x[:-1] 
    a: int = int(x[:x.index(',')])
    b: int = int(x[x.index(',')+1:])
    if inverse_a: a = abs(length*scale_l-a)
    if inverse_b: b = abs(breadth*scale_b-b)
    return (scale_l*a, scale_b*b)

def is_valid_input(x: str) -> bool:
    return sum([1 for z in x if z == ',']) == 2

# driver code
while True:
    if is_pressed('c'):
        print("clear")
        cur.clear()
    x = get_input()
    if is_valid_input(x):
        print(x, decode_input(x)) 
        draw(decode_input(x))
    sleep(delay_between_readings)