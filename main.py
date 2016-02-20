from functions import *

prepare_json()
merge_json()
#The first parameter is the number of cluster you want
#The second parameter is the epsilon (>0)
clusters = k_means(3, 0.001)
save_clusters(clusters)
