import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev

x = []
y = []

x_interp = []
y_interp = []

fig, ax = plt.subplots()

interp_line, = ax.plot([], [], 'b-', label='Interpolated Points')


ax.set_xlabel('X')
ax.set_ylabel('Y')

ax.set_title('Spline Interpolation')

ax.legend()

interpolate = True

ax.set_xlim(0, 10)
ax.set_ylim(0, 10)


def update_interpolation():
    global x_interp, y_interp
    
    if interpolate and len(x) > 2:
    # condition based on differences in the readings is to be put, to check if to interpolate(set interpolate=True) or not(set interpolate=False)

        if len(x) >= 3:  # to check if the number of data points is sufficient for cubic spline interpolation (k=3)
            x_arr = np.array(x, dtype=np.float64)
            y_arr = np.array(y, dtype=np.float64)
            tck, u = splprep([x_arr, y_arr], k=2, s=0)
            x_interp, y_interp = splev(np.linspace(0, 1, 100), tck)
        else:
            x_interp = []
            y_interp = []
    else:
        x_interp = []
        y_interp = []


        interp_line.set_data(x_interp, y_interp)

def onclick(event):
    global x_interp, y_interp
    if event.button == 1:
        
        x.append(event.xdata)
        y.append(event.ydata)

        update_interpolation()

        ax.cla()  

        ax.plot(x, y, 'bo', label='Discrete Points')
        ax.plot(x_interp, y_interp, 'b-', label='Interpolated Points')  

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        
        ax.set_title('Spline Interpolation')

        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)

        ax.legend()

        fig.canvas.draw()

fig.canvas.mpl_connect('button_press_event', onclick)

plt.show()

