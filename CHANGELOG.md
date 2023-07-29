# Changes v4
- Optimized python code
- Relocated the coordinate mapping logic from arduino to python
    > As now arduino code is completely independent from parameters. No need to reflash arduino code when changing parameters. All of that is handled in python now.
- Added `parameters.json` file which contains all the parameters.

# Changes v3
- Matplotlib to draw instead of turtle
- Spine interpolation to draw linear curves