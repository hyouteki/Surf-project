import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import DBSCAN

dataFilePath: str = r"C:\Lakshay\Projects\Surf project\python\data\wine.csv"
# Reading in 2D Feature Space from csv file
featureSpace = pd.read_csv(dataFilePath, header=None, sep=",")
# Store the points as a matrix where each row is a point
data = featureSpace.iloc[:, 0:2].values.tolist()
def plot(title: str, xCoords: list, yCoords: list) -> None:
    plt.scatter(xCoords, yCoords, marker='o')
    plt.title(title, fontsize=20)
    plt.show()

oldXCoords = [i[0] for i in data]
oldYCoords = [i[1] for i in data]

plot("Before removing outliers", oldXCoords, oldYCoords)

model = DBSCAN(eps=0.8,min_samples=5).fit(data)
inliers = [data[i] for i in range(len(data)) if model.labels_[i] != -1]
newXCoords = [i[0] for i in inliers]
newYCoords = [i[1] for i in inliers]

plot("After removing outliers", newXCoords, newYCoords)