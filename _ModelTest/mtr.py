# mtr.py
import numpy as np 
import numpy.random as rd
import matplotlib.pyplot as plt

class Metropolis:
    def __init__(self, pLarge, sigma):
        self.pLarge = pLarge # probability of large step
        self.sigma = sigma # standard deviation of perturbation

    def sample(self, func, dim, nSamples):
        samples = []
        prevSample = rd.rand(dim)
        prevVal = func(prevSample)
        total = 0
        while total < nSamples:
            newSample = self.__mutate(prevSample, dim)
            newVal = func(newSample)
            if newVal < prevVal:
                if prevVal == 0: # newVal = preVal = 0, must try again
                    continue
                elif rd.rand() > newVal / prevVal:
                    samples.append(prevSample) # reject new sample
                    total += 1
                    continue
            # otherwise accept
            prevSample = newSample
            prevVal = newVal
            samples.append(newSample) 
            total += 1
        return np.array(samples)

    # Input a function of samples in primary sample space and get the minimum cost
    def anneal(self, func, dim, r, T, T_min, nIte):
        # Initialize samples
        prevSample = rd.rand(dim)
        bestSample = prevSample
        prevVal = func(prevSample)
        bestVal = prevVal

        # Begin annealing loop
        curT = T
        print("Begin annealing")
        while curT > T_min:
            print("T:", curT)
            for _ in range(nIte):
                # Generate new sample
                curSample = self.__mutate(prevSample, dim)

                # Record if best solution so far is found
                curVal = func(curSample)
                if curVal < bestVal:
                    prevVal = bestVal = curVal
                    prevSample = bestSample = curSample
                    print("Best:", bestVal)
                    continue

                # Accept samples or not
                dE = curVal - prevVal
                if dE < 0 or (dE > 0 and rd.rand() < np.exp(-dE / curT)):
                    prevVal = curVal
                    prevSample = curSample
                    print("Accepted: ", curVal)

            curT *= r # anneal

        return bestVal, bestSample

    def __mutate(self, sample, dim):
        if rd.rand() < self.pLarge: # large step
            return rd.rand(dim)
        else: # small step
            return self.__wrap(sample + rd.randn(dim) * self.sigma, 0, 1)

    @staticmethod
    def __wrap(val, low, high):
        step = high - low
        ret = []
        for v in val:
            if v < low:
                while v < low:
                    v += step
            elif v >= high:
                while v >= high:
                    v -= step
            ret.append(v)
        return np.array(ret)

if __name__ == '__main__':
    mtr = Metropolis(0.1, 0.005)
    print(mtr.anneal(lambda x: 7 * np.sin(8 * x) + 6 * np.cos(5 * x), 1, 0.9, 1, 0.01, 100))
    X = mtr.sample(lambda x: np.sin(np.pi * x), 1, 10000)
    plt.hist(np.transpose(X).tolist())
    plt.show()
