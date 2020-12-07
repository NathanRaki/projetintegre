import os
import json

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

import numpy as np
import matplotlib.pyplot as plt
import mpld3


from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans

from yellowbrick.cluster import KElbowVisualizer
from collections import defaultdict, Counter

    
########## Fonctions pour sauvegarder et charger des objets
import pickle

def save_dict(dico, filename) :
    with open("dict2/"+filename+".pickle", 'wb') as handle:
        pickle.dump(dico, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def load_dict(filename) :
    with open("dict2/"+filename+".pickle", 'rb') as handle:
        return(pickle.load(handle))
    

########## Fonctions associées aux kmeans

def elbow(model,min_k,max_k,matrix): # en utilisant la librairie KElbowVisualizer
    visualizer = KElbowVisualizer(model, k=(min_k,max_k),timings=False) # timings=False : enlève la courbe de temps de calcul
    visualizer.fit(matrix)
    visualizer.show()
    #KElbowVisualizer.save_html(visualizer, 'lda.html')
    return visualizer.elbow_value_


def elbow_plt(data,min_k,max_k): # en utilisant la librairie plt
    sum_of_squared_distances=[]
    K=range(min_k,max_k)
    for k in K:
        km = KMeans(n_clusters=k)
        km = km.fit(data)
        sum_of_squared_distances.append(km.inertia_)
    c=plt.figure()
    plt.plot(K, sum_of_squared_distances,'bx-')
    plt.xlabel('k')
    plt.ylabel('Sum of squared distances')
    plt.title('Elbow Method For Optimal k')
    mpld3.fig_to_html(c)
    mpld3.save_html(c, 'fig.html')
    plt.show()

    
def get_topics (model,dictionary,n_words):
    cluster_dict = {}
    n_clusters=model.n_clusters
    order_centroids = model.cluster_centers_.argsort()[:, ::-1]

    for i in range(n_clusters):
        topic=[]
        topic_str=""
        for ind in order_centroids[i,:n_words]:
            topic.append(dictionary[ind])
        topic_str = ', '.join(topic)
        cluster_dict["Cluster %d" %i] = topic_str
    return cluster_dict



########### Fonction pour choisir le nombre de composantes pour TSVD (n'a pas été utilisé)
def select_n_components(var_ratio, goal_var: float) -> int:
    # Set initial variance explained so far
    total_variance = 0.0
    
    # Set initial number of features
    n_components = 0
    
    # For the explained variance of each feature:
    for explained_variance in var_ratio:
        
        # Add the explained variance to the total
        total_variance += explained_variance
        
        # Add one to the number of components
        n_components += 1

        # If we reach our goal level of explained variance
        if total_variance >= goal_var:
            # End the loop
            break
    print(total_variance)
    # Return the number of components
    return n_components