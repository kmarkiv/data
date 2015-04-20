__author__ = 'vikram'
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np

CAT = ["numlangs", "countryName", "continentName", "birthcity", "gender", "occupation", "industry", "domain"]
data = pd.read_csv('Pantheon.tsv', delimiter='\t')
class_le = LabelEncoder()
for cat in CAT:
    data[cat] = class_le.fit_transform(data[cat])

features = ["name", "numlangs", "countryName", "continentName", "birthyear", "birthcity", "gender", "occupation",
            "industry", "domain", "TotalPageViews", "L_star", "StdDevPageViews", "PageViewsEnglish",
            "PageViewsNonEnglish", "AverageViews", "HPI"]

data = data.fillna(data.mean())
df1 = data[
    ["domain", "gender", "occupation", "industry", "countryName", "continentName", "HPI"]]

from sklearn.decomposition import PCA

hpc = PCA(n_components=2).fit_transform(df1)
k_means = KMeans(n_clusters=8)
k_means.fit(hpc)

x_min, x_max = hpc[:, 0].min() - 5, hpc[:, 0].max() - 1
y_min, y_max = hpc[:, 1].min(), hpc[:, 1].max() + 5
xx, yy = np.meshgrid(np.arange(x_min, x_max, .2), np.arange(y_min, y_max, .2))
Z = k_means.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

plt.figure(1)
plt.clf()
plt.imshow(Z, interpolation='nearest',
           extent=(xx.min(), xx.max(), yy.min(), yy.max()),
           cmap=plt.cm.Paired,
           aspect='auto', origin='lower')

plt.plot(hpc[:, 0], hpc[:, 1], 'k.', markersize=4)
centroids = k_means.cluster_centers_
inert = k_means.inertia_
plt.scatter(centroids[:, 0], centroids[:, 1],
            marker='x', s=169, linewidths=3,
            color='w', zorder=8)
plt.xlim(x_min, x_max)
plt.ylim(y_min, y_max)
plt.xticks(())
plt.yticks(())
plt.show()

import numpy as np
from scipy.spatial.distance import cdist, pdist
from matplotlib import pyplot as plt

# Determine your k range
k_range = range(1, 18)

# Fit the kmeans model for each n_clusters = k
k_means_var = [KMeans(n_clusters=k).fit(hpc) for k in k_range]

# Pull out the cluster centers for each model
centroids = [X.cluster_centers_ for X in k_means_var]

# Calculate the Euclidean distance from
# each point to each cluster center
k_euclid = [cdist(hpc, cent, 'euclidean') for cent in centroids]
dist = [np.min(ke, axis=1) for ke in k_euclid]

# Total within-cluster sum of squares
wcss = [sum(d ** 2) for d in dist]

# The total sum of squares
tss = sum(pdist(hpc) ** 2) / hpc.shape[0]

# The between-cluster sum of squares
bss = tss - wcss

# elbow curve
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(k_range, bss / tss * 100, 'b*-')
ax.set_ylim((0, 100))
plt.grid(True)
plt.xlabel('n_clusters')
plt.ylabel('Percentage of variance explained')
plt.title('Variance Explained vs. k')
plt.xticks(())
plt.yticks(())
plt.show()