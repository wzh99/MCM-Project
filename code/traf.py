import numpy as np 
import pandas as pd 

class Traffic:
    def __init__(self, path):
        # Load file
        df = pd.DataFrame(pd.read_excel(path, dtype=np.float))
        data = df.values

        # Decide grid layout
        self.dataSize = data.shape[0]
        self.nGridPerSide = int(np.sqrt(self.dataSize))
        self.hashSize = self.nGridPerSide ** 2
        tran = data.transpose()
        bnd = np.array([[min(tran[0]), max(tran[0])], [min(tran[1]), max(tran[1])]])
        # [[longMin, longMax], 
        #  [latiMin, latiMax]]
        bndTrans = bnd.transpose()
        # [[longMin, latiMin],
        #  [longMax, latiMax]
        expand = np.abs(bndTrans[1] - bndTrans[0]) / self.nGridPerSide
        self.bnd = np.array([bndTrans[0] - expand, bndTrans[1] + expand])
        # [[longMin, latiMin],
        #  [longMax, latiMax]

        # Build grid index
        self.grid = np.full((self.hashSize), self._Node())
        for ptf in data:
            pti = self.__toGridIndex(ptf)
            h = self.__hash(pti)
            node = self.grid[h]
            if node.pos is None:
                node.pos = ptf
            else:
                self.grid[h] = self._Node(ptf, node)

    def estimateDensity(self, target, radius):
        # Get grid index of search bound
        target = np.asarray(target)
        iMin = self.__toGridIndex(np.maximum(target - radius, self.bnd[0]))
        iMax = self.__toGridIndex(np.minimum(target + radius, self.bnd[1]))
        
        # Search through all possible nodes
        sigma = radius / 3
        filtFunc = lambda x: np.exp(-x / (2 * (sigma ** 2)))
        den = 0
        for x in range(iMin[0], iMax[0] + 1):
            for y in range(iMin[1], iMax[1] + 1):
                h = self.__hash([x, y])
                node = self.grid[h]
                while node is not None and node.pos is not None:
                    pos = node.pos
                    distSq = self.__distSq(pos, target)
                    if np.sqrt(distSq) < radius:
                        den += filtFunc(distSq)
                    node = node.next
        return den

    def __toGridIndex(self, ptf):
        off = self.__boundOffset(ptf)
        pti = [self.__clamp(int(off[0] * self.nGridPerSide), 0, self.nGridPerSide - 1), 
               self.__clamp(int(off[1] * self.nGridPerSide), 0, self.nGridPerSide - 1)]
        return np.array(pti)

    class _Node:
        def __init__(self, pos = None, next = None):
            self.pos = pos
            self.next = next

    def __hash(self, pti):
        h = (np.int64(pti[0]) * 73856093) ^ (np.int64(pti[1]) * 19349663)
        return int(h % self.hashSize)

    def __boundOffset(self, pt):
        return (pt - self.bnd[0]) / (self.bnd[1] - self.bnd[0])

    @staticmethod
    def __distSq(pt1, pt2):
        return (pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2

    @staticmethod
    def __clamp(val, min, max):
        return np.minimum(np.maximum(val, min), max)
