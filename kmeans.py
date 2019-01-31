import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pylab as plt
data= pd.read_excel('location.xlsx')

from sklearn.cluster import KMeans
k=3
model = KMeans(n_clusters = k, n_jobs = -1, max_iter = 700).fit(data) 
np.savetxt('XXX.csv', model.cluster_centers_, delimiter = ',')