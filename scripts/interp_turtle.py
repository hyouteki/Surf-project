import numpy as np
import turtle
from scipy.interpolate import splprep, splev

x = []
y = []

x_interp = []
y_interp = []

screen = turtle.Screen()
screen.setup(500, 500)
screen.title('Spline Interpolation')

interpolate = True

def update_interpolation():
    global x_interp, y_interp
    
    if interpolate and len(x) > 2:
        if len(x) >= 3:
            x_arr = np.array(x, dtype=np.float64)
            y_arr = np.array(y, dtype=np.float64)
            tck, u = splprep([x_arr, y_arr], k=2, s=0)
            u_new = np.linspace(u.min(), u.max(), 100)
            spline_coords = splev(u_new, tck)
            x_interp = spline_coords[0]
            y_interp = spline_coords[1]
        else:
            x_interp = []
            y_interp = []
    else:
        x_interp = []
        y_interp = []

def onclick(x_coord, y_coord):
    global x, y, x_interp, y_interp

    x.append(x_coord)
    y.append(y_coord)

    update_interpolation()

    turtle.clear()

    turtle.penup()
    turtle.goto(x[0], y[0])
    turtle.pendown()
    turtle.color('blue')
    for i in range(len(x)):
        turtle.goto(x[i], y[i])

    turtle.penup()
    turtle.color('red')

    if len(x_interp) > 0 and len(y_interp) > 0:  # Check if interpolated points exist
        turtle.goto(x_interp[0], y_interp[0])
        turtle.pendown()
        for i in range(len(x_interp)):
            turtle.goto(x_interp[i], y_interp[i])

    turtle.penup()

turtle.onscreenclick(onclick)

turtle.mainloop()
