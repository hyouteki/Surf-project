import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from pandas import read_csv

# sample test data
data = read_csv("wine-data.csv", header=None, sep=",").iloc[:, 0:2].values

oldXCoords = [record[0] for record in data]
oldYCoords = [record[1] for record in data]

scaleXAxis = int(max(oldXCoords)) + 1
scaleYAxis = int(max(oldYCoords)) + 1


def plot(title: str, xCoords: list, yCoords: list) -> None:
    """Function to plot the coordinates"""
    plt.scatter(xCoords, yCoords, marker="o")
    plt.title(title, fontsize=20)
    plt.xlim(0, scaleXAxis)
    plt.ylim(0, scaleYAxis)
    plt.show()


plot("Before removing outliers", oldXCoords, oldYCoords)

# removing outliers using DBSCAN algorithm
model = DBSCAN(eps=0.8, min_samples=8).fit(data)
inliers = [data[record] for record in range(len(data)) if model.labels_[record] != -1]
newXCoords = [record[0] for record in inliers]
newYCoords = [record[1] for record in inliers]

plot("After removing outliers", newXCoords, newYCoords)
