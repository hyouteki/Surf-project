import os

s=""

dic=[([0,3,0,3],"("),([3,6,0,3],"0"),([6,9,0,3],")"),([9,12,0,3],"="),
     ([0,3,3,6],"1"),([3,6,3,6],"2"),([6,9,3,6],"3"),([9,12,3,6],"+"),
     ([0,3,6,9],"4"),([3,6,6,9],"5"),([6,9,6,9],"6"),([9,12,6,9],"-"),
     ([0,3,9,12],"7"),([3,6,9,12],"8"),([6,9,9,12],"9"),([9,12,9,12],"/"),
     ([0,3,12,15],"AC"),([3,6,12,15],"%"),([6,9,12,15],"C"),([9,12,12,15],"*")]

def mapToTile(a,b):
    for i in dic:
        w=i[0][0]
        x=i[0][1]
        y=i[0][2]
        z=i[0][3]
        if(w <= a and a <= x and y <= b and b <= z):
            return i[1]
    return "~"

def addToCalculator(a,b):
    global s
    ch=mapToTile(a,b)
    if(ch=="~"):
        print("Wrong coordinates!")
    elif(ch=="AC"):
        s=""
    elif(ch=="C"):
        if(len(s)>0):
            s=s[:-1]
    elif ch == "=":
        os.system(f"python3 compute.py {s}")
    else:
        s+=ch

addToCalculator(1, 4)
addToCalculator(10, 4)
addToCalculator(4, 4)
addToCalculator(10, 1)
