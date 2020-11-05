#%% Importations
import pandas as pd
import numpy as np
import nltk
#import string
import re
import os
#import gensim
import pickle

#from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
#from collections import defaultdict
from country_list import countries_for_language
from langdetect import detect_langs
from gensim.parsing.preprocessing import STOPWORDS

#%% Répertoire Nathan
os.chdir('/home/raki/Cours/projet_integre/')

#%% Changements des options de Panda
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

#%% Chargement des fichiers csv
author = pd.read_csv('data/author.csv', sep = ',', encoding = 'cp1252')
publication = pd.read_csv('data/publication.csv', sep = ',', encoding = 'cp1252')
keyword = pd.read_csv('data/keyword.csv', sep = ',', encoding = 'cp1252')
year = pd.read_csv('data/year.csv', sep = ',', encoding = 'cp1252')
author_publication = pd.read_csv('data/publication_author.csv', sep = ',', encoding = 'cp1252')
keyword_publication = pd.read_csv('data/Publication_keywords.csv', sep = ',', encoding = 'cp1252')
year_publication = pd.read_csv('data/author.csv', sep = ',', encoding = 'cp1252')

#%% Fonctions de sauvegarde et de chargement de dictionnaires avec des fichiers
# Utilisé pour gagner du temps afin de ne pas avoir à re-exécuter tout
# à chaque ré-ouverture
def save_dict(dico, filename) :
    with open("dict/"+filename+".pickle", 'wb') as handle:
        pickle.dump(dico, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def load_dict(filename) :
    with open("dict/"+filename+".pickle", 'rb') as handle:
        return(pickle.load(handle))
    
#%% Nettoyage du fichier publication
del publication['categorie'] # suppression de la colonne qui ne contient que des proceeding
publication = pd.DataFrame.drop_duplicates(publication) # suppression des doublons
delete_rows = publication[publication['article_title'].duplicated(keep='first')] # suppression des doublons sur les colonnes
publication.drop(delete_rows.index, inplace=True)
publication = publication.loc[np.random.permutation(publication.index)].reset_index(drop=True) # On mélange le dataset, servira par la suite pour d'éventuels tests

#%% Création du dictionnaire à partir du fichier publication
article_titles = publication['article_title'].str.lower() # conversion des articles en minuscule
article_titles = article_titles.tolist() # conversion des articles en liste

list_id_publication = list(publication['id_publication']) # liste des identifiants

article_titles = dict(zip(list_id_publication, article_titles)) # dictionnaire id : titre

#%% Sauvegarde original_titles
save_dict(article_titles, "original_titles")

#%% Chargement original_titles
article_titles = load_dict("original_titles")

#%% Nettoyage des titres
countries = dict(countries_for_language('en')) # Récupération d'une liste de pays
country_exclusion = [x.lower() for x in list(countries.values())]
country_exclusion = '|'.join(country_exclusion)
for i in article_titles.copy():
    article_titles[i]=re.sub('\[.*?\]','',article_titles[i]) # suppression de toutes les expressions entre crochets
    article_titles[i]=re.sub('\{.*?\}','',article_titles[i]) # suppression de toutes les expressions entre accolades
    article_titles[i]=re.sub('\(.*?\)+','',article_titles[i]) # suppression de toutes les expressions entre parenthèses
    article_titles[i]=re.sub('<.+>','',article_titles[i])    # suppression de toute la chaine qui se trouve entre un '<' et un '>' (1ère et dernière occurence)
    article_titles[i]=re.sub('\$.+\$','',article_titles[i])  # suppression de toute la chaine qui se trouve entre un '$' et un '$' (1ère et dernière occurence)
    article_titles[i]=re.sub('\S*[\^,_,&,:,@,#,$,\\\]\S*',' ',article_titles[i]) # suppression de tous les mots contenant un @ et #.. (@ et # seule inclus aussi)
    article_titles[i]=re.sub('[.,\,,!,?,%,*,§,²,~,\{,\}]',' ',article_titles[i]) # suppression des caractères spéciaux
    article_titles[i]=re.sub('[;,+,/]',' ',article_titles[i])
    article_titles[i]=re.sub('-',' ',article_titles[i]) # remplacement par un espace, se discute
    article_titles[i]=re.sub('(\s\d+\s|^\d+\s|\s\d+$)','',article_titles[i]) # suppression de tous les chiffres qui sont seuls
    article_titles[i]=re.sub('(\'s)|(\')','',article_titles[i]) # suppression des 's
    article_titles[i]=re.sub('\S*((january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december))\S*','',article_titles[i]) # suppression des expressions qui continnent un mois
    article_titles[i]=re.sub('([0-9]+)(?:st|nd|rd|th)','',article_titles[i]) # suppression des expression en rapoort avec des dates ou des n-ièmes
    article_titles[i]=re.sub('(conference)|(international)','',article_titles[i]) # suppression des mots conférence et international qui sont trop fréquents
    article_titles[i]=re.sub(country_exclusion,'',article_titles[i]) # exclusion des références à des pays
    article_titles[i]=re.sub(r'\b\D{1,2}\b',' ',article_titles[i]) # On supprime les mots de moins de 3 lettres qui ne contiennent pas de chiffres qui seraient resté
    article_titles[i]=re.sub(' +', ' ', article_titles[i]) # suppression des espaces en trop à la fin du nettoyage
    if (len(article_titles[i]) == 0) or (len(article_titles[i]) == 1) : # suppression des titres à 0 ou 1 caractère
        del article_titles[i]
        
#%% Sauvegarde cleaned
save_dict(article_titles, "cleaned")

#%% Chargement cleaned
article_titles = load_dict("cleaned")

#%% Suppression des titres non-anglais
en_ratio = 0.5
for k,v in article_titles.copy().items() :
    res = detect_langs(v)
    # Si le titre n'a aucune trace d'anglais
    if not [l for l in res if l.lang == 'en']:
        del article_titles[k]
    else :
        for lang in res :
            # Si le titre a des traces d'anglais mais pas suffisamment
            if lang.lang == 'en' and lang.prob < en_ratio :
                del article_titles[k]
                
#%% Sauvegarde onlyenglish
save_dict(article_titles, "onlyenglish")

#%% Chargement onlyenglish
article_titles = load_dict("onlyenglish")

#%% Tokenisation des titres
tokenizer = nltk.RegexpTokenizer(r'\w+')
for k,v in article_titles.items() :
    article_titles[k] = tokenizer.tokenize(v)
    
#%% Sauvegarde tokenized
save_dict(article_titles, "tokenized")

#%% Chargement tokenized
article_titles = load_dict("tokenized")

#%% Suppression des stopwords
stopwords = set()
stopwords.update(tuple(nltk.corpus.stopwords.words('english')))
all_stopwords = STOPWORDS.union(stopwords)
for k,v in article_titles.items() :
    article_titles[k] = [word for word in v if word not in all_stopwords]
    
#%% Sauvegarde nostopwords
save_dict(article_titles, "nostopwords")

#%% Chargement nostopwords
article_titles = load_dict("nostopwords")

#%% Lemmatisation
# Fonction qui va servir à identifier la nature du mot (verbe, nom, ...)
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
    
#%% Sauvegarde lemmatized
save_dict(article_titles, "lemmatized")