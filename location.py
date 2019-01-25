# loc.py

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from mtr import Metropolis

BOUND = np.array([[-67.293988, 17.897988], [-65.568656, 18.539222]])

class Package:
    def __init__(self, weight, size):
        self.weight = weight
        self.size = size

MED_1 = Package(2, [14, 7, 5])
MED_2 = Package(2, [5, 8, 5])
MED_3 = Package(3, [12, 7, 4])

class Requirement:
    def __init__(self, pack, num):
        self.package = pack
        self.num = num

class Hospital:
    def __init__(self, loc, req):
        self.location = loc
        self.requirement = req

HOSPITALS = [
    Hospital([-65.65, 18.33], [Requirement(MED_1, 1), Requirement(MED_3, 1)]),
    Hospital([-66.03, 18.22], [Requirement(MED_1, 2), Requirement(MED_3, 1)]),
    Hospital([-66.07, 18.44], [Requirement(MED_1, 1), Requirement(MED_2, 1)]),
    Hospital([-66.16, 18.40], [Requirement(MED_1, 2), Requirement(MED_2, 1),
        Requirement(MED_3, 2)]),
    Hospital([-66.73, 18.47], [Requirement(MED_1, 1)])
]

def distSq(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2

def getDensity(pt):
    sigma = 0.08
    func = lambda x: np.exp(-x / (2 * sigma ** 2))
    den = 0
    for h in HOSPITALS:
        for r in h.requirement:
            den += r.num * func(distSq(pt, h.location))
    return den

def plotDensity():
    nStep = 50
    X = np.linspace(-67.00, -65.50)
    Y = np.linspace(18.0, 18.6)
    gX, gY = np.meshgrid(X, Y)
    Z = np.ndarray((nStep, nStep))
    for i in range(nStep):
        for j in range(nStep):
            Z[j, i] = getDensity([X[i], Y[j]])
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.plot_surface(gX, gY, Z, rstride=1, cstride=1, cmap=plt.cm.Blues)
    plt.show()

def sample():
    def mapToLocation(sp):
        longi = (1 - sp[0]) * BOUND[0][0] + sp[0] * BOUND[1][0]
        lati = (1 - sp[1]) * BOUND[0][1] + sp[1] * BOUND[1][1]
        return np.array([longi, lati])

    def computeDensity(sp):
        return getDensity(mapToLocation(sp))

    mt = Metropolis(0.1, 0.005)
    samples = mt.sample(computeDensity, 2, 10000)
    locs = list(map(mapToLocation, samples))
    locTran = np.array(locs).transpose()
    plt.scatter(locTran[0], locTran[1], s=0.2)
    df = pd.DataFrame({"Longitude": locTran[0], "Latitude": locTran[1]})
    df.to_excel("data/location.xlsx", sheet_name='Locations', index=False)
    plt.show()

if __name__ == '__main__':
    sample()