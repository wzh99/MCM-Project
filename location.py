# location.py

from mtr import Metropolis
import info
import terrain as tr
import route as rt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.mplot3d import Axes3D

MEDICALS = info.MEDICALS

HOSPITALS = info.HOSPITALS

def distSq(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2

def getDensity(pt):
    if tr.terrain.getHeight(pt) == 0:
        return 0
    sigma = 0.1
    func = lambda x: np.exp(-x / (2 * sigma ** 2))
    den = 0
    for h in HOSPITALS:
        for r in h.requirement:
            den += r * func(distSq(pt, h.location))
    return den

def plotDensity():
    nStep = 100
    X = np.linspace(-67.00, -65.50, nStep)
    Y = np.linspace(18.0, 18.7, nStep)
    gX, gY = np.meshgrid(X, Y)
    Z = np.ndarray((nStep, nStep))
    for i in range(nStep):
        for j in range(nStep):
            Z[j, i] = getDensity([X[i], Y[j]])
    fig = plt.figure(figsize=(12.8, 7.2))
    ax = Axes3D(fig)
    ax.plot_surface(gX, gY, Z, rstride=1, cstride=1, cmap=plt.cm.YlGnBu)
    #pcm = ax.pcolor(X, Y, Z, norm=colors.LogNorm(vmin=Z.min(), vmax=Z.max()), cmap='Blues')
    plt.show()

def sample():
    def mapToLocation(sp):
        longi = (1 - sp[0]) * tr.BOUND[0][0] + sp[0] * tr.BOUND[1][0]
        lati = (1 - sp[1]) * tr.BOUND[0][1] + sp[1] * tr.BOUND[1][1]
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

def optimizeLocation():
    loc = np.array([-65.65, 18.33])
    radius = 0.104260
    def samplesToLoc(samples):
        theta = samples[0] * 2 * np.pi
        r = samples[1] * radius
        pt = loc + r * np.array([np.cos(theta), np.sin(theta)])
        return pt
    def getRoadDensity(pt):
        if tr.terrain.getHeight(pt) == 0:
            return 0
        return rt.roadMap.countAround(pt, radius)

    m = Metropolis(0.1, 0.05)
    val, samples = m.anneal(lambda sp: getRoadDensity(samplesToLoc(sp)), 2, 0.9, 10000, 1000, 10)
    print(val, samplesToLoc(samples))

if __name__ == '__main__':
    #plotDensity()
    optimizeLocation()