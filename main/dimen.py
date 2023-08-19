from math import sin
l = int(input("Enter length: "))
b = int(input("Enter length: "))
theta = 15 # degrees
degree_to_radian = lambda n: n*0.0174533
cl = l/(2*sin(degree_to_radian(theta)))
cb = b/(2*sin(degree_to_radian(theta)))
print(f"cl: {int(cl)}")
print(f"cb: {int(cb)}")