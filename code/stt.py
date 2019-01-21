# stt.py
from traf import Traffic
from pop import Population
from mtr import Metropolis
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd 

trafPath = "data/over.xlsx"
popPath = "img/pop_den_trace.jpg"

longitudeRange = [120.85, 121.98]
latitudeRange = [30.67, 31.51]

def plotDensity():
    traf = Traffic(trafPath)
    pop = Population(popPath, longitudeRange, latitudeRange)
    nSample = 50
    X = np.linspace(120.85, 121.98, nSample)
    Y = np.linspace(30.67, 31.51, nSample)
    gX, gY = np.meshgrid(X, Y)
    Z = np.ndarray((nSample, nSample))
    for i in range(nSample):
        for j in range(nSample):
            trafDen = traf.estimateDensity([X[i], Y[j]], 8e-3) / 350
            popDen = pop.estimateDensity([X[i], Y[j]]) / 4.8e4
            den = trafDen * popDen
            if den != 0:
                den /= (trafDen + popDen)
            Z[i, j] = den
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.plot_surface(gX, gY, Z, rstride=1, cstride=1, cmap=plt.cm.Blues)
    plt.show()

def sample():
    traf = Traffic(trafPath)
    pop = Population(popPath, longitudeRange, latitudeRange)

    def mapToLocation(sp):
        longi = (1 - sp[0]) * longitudeRange[0] + sp[0] * longitudeRange[1]
        lati = (1 - sp[1]) * latitudeRange[0] + sp[1] * latitudeRange[1]
        return np.array([longi, lati])

    def computeDensity(sp):
        loc = mapToLocation(sp)
        trafDen = traf.estimateDensity(loc, 8e-3) / 350
        popDen = pop.estimateDensity(loc) / 4.8e4
        den = trafDen * popDen
        if den != 0:
            den /= (trafDen + popDen)
        return den

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
