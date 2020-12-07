import os
import json

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import re
import mpld3

import nltk
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet


import gensim
from gensim.parsing.preprocessing import STOPWORDS

from collections import defaultdict, Counter
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

def cleaning_1(article_titles): # prend en entrée un dictionnaire
    for i in article_titles:
        # suppression de toutes les expressions entre crochets
        article_titles[i]=re.sub('\[.*?\]',' ',article_titles[i]) 
        # suppression de toutes les expressions entre accolades
        article_titles[i]=re.sub('\{.*?\}',' ',article_titles[i]) 
        # suppression de toutes les expressions entre parenthèses
        article_titles[i]=re.sub('\(.*?\)',' ',article_titles[i]) 
        # suppression de toute la chaine qui se trouve entre un '<' et un '>' (1ère et dernière occurence)
        article_titles[i]=re.sub('<.+>',' ',article_titles[i])  
        # suppression de toute la chaine qui se trouve entre un '$' et un '$' (1ère et dernière occurence)
        article_titles[i]=re.sub('\$.+\$',' ',article_titles[i])
        # suppression de tous les mots contenant un @ et #.. (@ et # seule inclus aussi)
        article_titles[i]=re.sub('\S*[\^,%,_,&,@,#,$,\\\]\S*',' ',article_titles[i])
        # suppression des caractères spéciaux
        article_titles[i]=re.sub('[§,²,~,\{,\},\(,\),\[,\]]',' ',article_titles[i])
        article_titles[i]=re.sub('[<,>,=,;,+,/,*]',' ',article_titles[i])

        
        
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
        # suppression des expressions qui continnent un mois
        article_titles[i]=re.sub('\S*((january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december))\S*',' ',article_titles[i])
        article_titles[i]=re.sub('(conference)|(international)',' ',article_titles[i]) # suppression des mots conference et international qui sont particlièrement fréquents
        article_titles[i]=re.sub(country_exclusion,' ',article_titles[i])
        
        article_titles[i]=re.sub(r'\b\D{1,2}\b',' ',article_titles[i]) # On supprime les mots de moins de 3 lettres qui ne contiennent pas de chiffres qui seraient resté

        article_titles[i]=re.sub(' +', ' ', article_titles[i]) # suppression des espaces en trop à la fin du nettoyage
        
        if (len(article_titles[i]))<3 : # suppression des titres à moins de 3 caractères
            del article_titles[i]
        
        
# Suppression des articles qui ne sont pas en anglais       
def only_english(article_titles): 

    from langdetect import detect_langs 

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

                    
# Lemmatisation                   
def lemmatisation(article_titles): # prend en entrée un dictionnaire tokénisé 
    
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
                    
                  
                
# Suppression des mots vides
def delete_stopwords(article_titles): # prend en entrée un dictionnaire tokénisé
    stopwords = set()
    stopwords.update(tuple(nltk.corpus.stopwords.words('english')))
    all_stopwords = STOPWORDS.union(stopwords) # gensim
    
    for k,v in article_titles.items() :
        article_titles[k] = [word for word in v if word not in all_stopwords]