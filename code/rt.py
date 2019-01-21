from mtr import Metropolis
from pop import Population
from traf import Traffic
import numpy as np
import numpy.random as rd 
import pandas as pd
import matplotlib.pyplot as plt

trafPath = "data/over.xlsx"
popPath = "img/pop_den_trace.jpg"
stationPath = "data/Stations.xlsx"

longitudeRange = [120.85, 121.98]
latitudeRange = [30.67, 31.51]
airportLoc = [121.808603, 31.142363]

nStations = 50
nRoutes = 6
nSelect = 4
nTrafSeg = 5

kDist = 1
kTraf = 3e2
kPop = 2e5

outputPath = "data/routes.xlsx"

traf = Traffic(trafPath)
pop = Population(popPath, longitudeRange, latitudeRange)

# Manhattan distance
def manDist(pt1, pt2):
    return np.abs(pt1[0] - pt2[0]) + np.abs(pt1[1] - pt2[1])

def route():
    df = pd.DataFrame(pd.read_excel(stationPath, dtype=np.float))
    statVals = df.values

    # Define mapping function
    def samplesToRoute(samples): # samples must be an (50, 2) array
        # Intialize route 
        routes = []
        for _ in range(nRoutes):
            routes.append([airportLoc])
        # Begin searching
        stations = statVals.tolist().copy()
        count = 0
        while True:
            for rt in routes:
                # Search nearby stations of last station
                lastStat = rt[-1]
                candList = sorted(stations, key=lambda pos: manDist(pos, lastStat))

                # Select a station and append it to route
                nSelThis = min(nSelect, len(candList))
                # choice: 0, 1, 2, ... (nSelThis-1)
                idx = int(nSelThis * samples[count]) 
                select = candList[idx]
                rt.append(select)
                stations.remove(select) # this station will never be considered again
                count += 1

                # Terminate if all the stations are selected
                if count == nStations:
                    return routes

    def routeCost(routes):
        cost = 0
        for rt in routes:
            rtDist = 0
            rtTraf = 0
            rtPop = 0
            for i in range(len(rt)):
                if i != len(rt) - 1:
                    start = np.array(rt[i])
                    end = np.array(rt[i + 1])
                    # Distance term
                    dist = manDist(start, end)
                    rtDist += dist
                    # Traffic term
                    trafDen = 0
                    seg = (end - start) / nTrafSeg
                    segLen = np.abs(seg[0]) + np.abs(seg[1])
                    curPt = start
                    for _ in range(nTrafSeg):
                        segTrafDen = traf.estimateDensity(curPt, 8e-3)
                        trafDen += segTrafDen * segLen
                    trafDen /= dist
                    rtTraf += trafDen

                # Population term
                popDen = pop.estimateDensity(rt[i])
                rtPop += popDen
            # print(rtDist, rtTraf, rtPop)
            # print(kDist * rtDist, kTraf / rtTraf, kPop / rtPop)
            cost += kDist * rtDist + kTraf / rtTraf + kPop / rtPop
        return cost

    mtr = Metropolis(0.1, 0.005)
    val, samples = mtr.anneal(lambda sp: routeCost(samplesToRoute(sp)), nStations, 0.9, 1, 1e-2, 10)

    routes = samplesToRoute(samples)
    writer = pd.ExcelWriter(outputPath)
    for i in range(len(routes)):
        rt = routes[i]
        rtTrans = np.array(rt).transpose()
        plt.scatter(rtTrans[0], rtTrans[1])
        plt.plot(rtTrans[0], rtTrans[1])
        df = pd.DataFrame({"Longitude": rtTrans[0], "Latitude": rtTrans[1]})
        df.to_excel(excel_writer=writer, sheet_name=str(i), index=False)
    writer.save()
    writer.close()
    plt.show()

if __name__ == '__main__':
    route()