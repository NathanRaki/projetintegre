import os
import json

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import re

import nltk
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet


import gensim
from gensim.parsing.preprocessing import STOPWORDS
from gensim.parsing.preprocessing import remove_stopwords


from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans


from yellowbrick.cluster import KElbowVisualizer
from collections import defaultdict, Counter
from scipy import sparse
from wordcloud import WordCloud
    
########## Fonctions pour sauvegarder et charger des objets
import pickle

def save_dict(dico, filename) :
    with open("dict2/"+filename+".pickle", 'wb') as handle:
        pickle.dump(dico, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def load_dict(filename) :
    with open("dict2/"+filename+".pickle", 'rb') as handle:
        return(pickle.load(handle))
    

    
######################################################## Fonctions de nettoyage 
def cleaning_1(article_titles):
    for i in article_titles:
        article_titles[i]=re.sub('\[.*?\]',' ',article_titles[i]) # suppression de toutes les expressions entre crochets
        article_titles[i]=re.sub('\{.*?\}',' ',article_titles[i]) # suppression de toutes les expressions entre accolades
        article_titles[i]=re.sub('\(.*?\)',' ',article_titles[i]) # suppression de toutes les expressions entre parenthèses
        article_titles[i]=re.sub('<.+>',' ',article_titles[i])    # suppression de toute la chaine qui se trouve entre un '<' et un '>' (1ère et dernière occurence)
        article_titles[i]=re.sub('\$.+\$',' ',article_titles[i])  # suppression de toute la chaine qui se trouve entre un '$' et un '$' (1ère et dernière occurence)
        article_titles[i]=re.sub('\S*[\^,_,&,@,#,$,\\\]\S*',' ',article_titles[i]) # suppression de tous les mots contenant un @ et #.. (@ et # seule inclus aussi)
        article_titles[i]=re.sub('[%,*,§,²,~,\{,\},\(,\),\[,\]]',' ',article_titles[i]) # suppression des caractères spéciaux
        article_titles[i]=re.sub('[<,>,=,;,+,/]',' ',article_titles[i])

        
        
def cleaning_2(article_titles):
    for i in article_titles:
        article_titles[i]=re.sub('[-,.,\,,!,?]',' ',article_titles[i]) # suppression tirets et ponctuation
        article_titles[i]=re.sub(r'\b\d+\b',' ',article_titles[i]) # suppression de tous les chiffres seuls
        article_titles[i]=re.sub('\S*\d[^gd]\S*',' ',article_titles[i]) # suppression de tous les chiffres et des chaines contenant un chiffre excepté les lettres d et g (ne supprime pas les g et d en trop)
        article_titles[i]=re.sub('\S*\d\w{2,}\S*',' ',article_titles[i]) # suppression des éventuels mots avec des plusieurs g ou d à la suite (suite de l'expression d'avant)
        article_titles[i]=re.sub('\S*\w+\d\S*',' ',article_titles[i]) # supression des chaines qui précédent un nombre
        article_titles[i]=re.sub('(\'s)|(\')',' ',article_titles[i]) # suppression des 's ou guillemets simple

        
        
        
def cleaning_3(article_titles):  # on veut supprimer les références à des pays et ce qui reste après nettoyage
    from country_list import countries_for_language # pip install country_list

    countries = dict(countries_for_language('en'))
    country_exclusion = [x.lower() for x in list(countries.values())]
    country_exclusion = '|'.join(country_exclusion)

    for i in article_titles.copy():
        article_titles[i]=re.sub('\S*((january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december))\S*',' ',article_titles[i]) # suppression des expressions qui continnent un mois
        #article_titles[i]=re.sub('([0-9]+)(?:st|nd|rd|th)','',article_titles[i]) # suppression des expression en rapoort avec des dates ou des n-ièmes
        article_titles[i]=re.sub('(conference)|(international)',' ',article_titles[i]) # suppression des mots conference et international qui sont particlièrement fréquents
        article_titles[i]=re.sub(country_exclusion,' ',article_titles[i])
        
        article_titles[i]=re.sub(r'\b\D{1,2}\b',' ',article_titles[i]) # On supprime les mots de moins de 3 lettres qui ne contiennent pas de chiffres qui seraient resté

        article_titles[i]=re.sub(' +', ' ', article_titles[i]) # suppression des espaces en trop à la fin du nettoyage
        if (len(article_titles[i])<3) : # suppression des titres à 0 ou 1 mots
            del article_titles[i]
        
        
        
# Sélection des articles uniquement en anglais        
def only_english(article_titles):
    ### Cette fonction prend beaucoup de temps ###   
    # On voudrait également supprimer les publications qui ne sont pas en langue anglaise

    from langdetect import detect_langs # pip install langdetect

    en_ratio = 0.5
    for k,v in article_titles.copy().items() :
        res = detect_langs(v)
        # Si le titre n'a aucune trace d'anglais
        if not [l for l in res if l.lang == 'en'] :
            del article_titles[k]
        else :
            for lang in res :
                # Si le titre a des traces d'anglais mais pas suffisamment
                if lang.lang == 'en' and lang.prob < en_ratio :
                    del article_titles[k]

                    
                    
def lemmatisation(article_titles):
    # Lemmatisation


    # Fonction qui va servir à identité la nature du mot (verbe, nom, ...)
    def get_wordnet_pos(word) :
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tags = {'J' : wordnet.ADJ,
                'N' : wordnet.NOUN,
                'V' : wordnet.VERB,
                'R' : wordnet.ADV}
        return tags.get(tag, wordnet.NOUN)

    lemmatizer = WordNetLemmatizer()
    for k,v in article_titles.items() :
        article_titles[k] = [lemmatizer.lemmatize(w, get_wordnet_pos(w)) for w in v]
                    
                    
                    
########### Fonction pour choisir le nombre de composantes pour TSVD
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





########## Fonctions associées aux kmeans

def elbow(model,min_k,max_k,matrix):
    visualizer = KElbowVisualizer(model, k=(min_k,max_k),timings=False) # timings=False : enlève la courbe de temps de calcul
    visualizer.fit(matrix)
    visualizer.show()
    return visualizer.elbow_value_

    
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