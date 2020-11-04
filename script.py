#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 19:58:51 2020

@author: raki
"""

#%% Importing Libraries
import pandas as pd
import nltk
import re
import pickle
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from collections import defaultdict
from gensim.parsing.preprocessing import STOPWORDS

#%% Loading Data
publication = pd.read_csv('/home/raki/Cours/projet_integre/publication.csv', sep = ',', encoding = 'cp1252')
publication = pd.DataFrame.drop_duplicates(publication) # suppression des doublons
delete_rows = publication[publication['article_title'].duplicated(keep='first')]
publication.drop(delete_rows.index, inplace=True)

# On créé un dictionnaire (id_publ : title)
list_id_publication = list(publication['id_publication'])
articles_titles = publication['article_title'].tolist()
titles = dict(zip(list_id_publication, articles_titles))

#%% Lowering Titles
lowered_titles = defaultdict(set)
for k,v in titles.items() :
    lowered_titles[k] = v.lower()
    
#%% Cleaning titles
cleaned_titles = defaultdict(set)
for k,v in lowered_titles.items() :
    cleaned_titles[k] = lowered_titles[k]
    cleaned_titles[k] = re.sub('\[.*?\]', '', cleaned_titles[k]) # suppression de toutes les expressions entre crochets
    cleaned_titles[k] = re.sub('\{.*?\}', '', cleaned_titles[k]) # suppression de toutes les expressions entre accolades
    cleaned_titles[k] = re.sub('\(.*?\)', '', cleaned_titles[k]) # suppression de toutes les expressions entre parenthèses
    cleaned_titles[k] = re.sub('<.+>', '', cleaned_titles[k])    # suppression de toute la chaine qui se trouve entre un '<' et un '>' (1ère et dernière occurence)
    cleaned_titles[k] = re.sub('\$.+\$', '', cleaned_titles[k])  # suppression de toute la chaine qui se trouve entre un '$' et un '$' (1ère et dernière occurence)
    cleaned_titles[k] = re.sub('\S*[é,è,\^,_,&,:,@,#,$,\\\]\S*', ' ', cleaned_titles[k]) # suppression de tous les mots contenant un @ et #.. (@ et # seule inclus aussi)
    cleaned_titles[k] = re.sub('[.,\,,!,?,%,*,§,²,~,\{,\}]', ' ', cleaned_titles[k]) # suppression des caractères spéciaux
    cleaned_titles[k] = re.sub('[;,+,/]', ' ', cleaned_titles[k])
    cleaned_titles[k] = re.sub(' +', ' ', cleaned_titles[k]) # suppression des espaces en trop
    cleaned_titles[k] = re.sub('-', ' ', cleaned_titles[k]) # remplacement des tirets par rien # choix qui se discute
    cleaned_titles[k] = re.sub('(\s\d+\s|^\d+\s|\s\d+$)', '', cleaned_titles[k]) # suppression de tous les chiffres qui sont seuls
    cleaned_titles[k] = re.sub('(\s(.)\s)|(^.\s)|(\s.$)', '', cleaned_titles[k]) #suppression des caractères d'une lettre
    cleaned_titles[k] = re.sub('(\'s)', '', cleaned_titles[k]) # suppression des 's
    cleaned_titles[k] = re.sub('\S*((january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december))\S*', '', cleaned_titles[k]) # suppression des expressions qui continnent un mois
    cleaned_titles[k] = re.sub('([0-9]+)(?:st|nd|rd|th)?', '', cleaned_titles[k]) # supprime les nombres ainsi que les 2nd, 14th, 21st, ...
    cleaned_titles[k] = re.sub('[*µ*]', '', cleaned_titles[k]) # supprime tout ce qui contient µ
    if (len(cleaned_titles[k]) == 0) or (len(cleaned_titles[k]) == 1) :
        del cleaned_titles[k]

#%%
en_ratio = 0.5
count = 0
from langdetect import detect_langs
for k,v in cleaned_titles.items() :
    print('v: ', v, '\n')
    res = detect_langs(v)
    for lang in res :
        if lang.lang == 'en' and lang.prob >= en_ratio :
            count = count + 1
print(count)

#%%
st = "  banishing the spectre of a meltdown with leakage free speculation "
print(len(st))
st = re.sub(' +', ' ', st)
print(len(st))

#%% Tokenizing Titles
tokenizer = nltk.RegexpTokenizer(r'\w+') # Création du tokenizer, \w+ supprime les mots vides (sinon nltk.pos_tag() a une erreur)
tokenized_titles = defaultdict(set)
for k,v in lowered_titles.items() :
    tokenized_titles[k] = tokenizer.tokenize(v)
    
#%% Deleting Stopwords
# sw has 179 words, STOPWORDS has 337 and the union all_sw has 390 stopwords
sw = set()
sw.update(tuple(nltk.corpus.stopwords.words('english')))
all_sw = STOPWORDS.union(sw)
optimized_titles = defaultdict(list)
for k,v in tokenized_titles.items() :
    optimized_titles[k] = [word for word in v if word not in all_sw]
    
#%% Lemmatization
# On choisi la lemmatization étant donné qu'on a du temps pour traiter les données et qu'elle fait
# mieux le job que la racinisation
def get_wordnet_pos(word) :
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tags = {'J' : wordnet.ADJ,
            'N' : wordnet.NOUN,
            'V' : wordnet.VERB,
            'R' : wordnet.ADV}
    return tags.get(tag, wordnet.NOUN)

lemmatizer = WordNetLemmatizer()
lemmatized_titles = defaultdict(list)
for k,v in optimized_titles.items() :
    lemmatized_titles[k] = [lemmatizer.lemmatize(w, get_wordnet_pos(w)) for w in v]
    
#%% Matching
for k,v in lemmatized_titles.items() :
    matching = [s for s in v if 'multitask' in s]
    if matching :
        print(v)
        
#%% Tests
maximum = 0
for k,v in lemmatized_titles.items() :
    if len(v) > maximum :
        print(len(v), ' : ', v, '\n')
        maximum = len(v)

#%% Print Area
rows_number = 10
print_dict = dict(list(lemmatized_titles.items())[0:rows_number-1])
for k,v in print_dict.items() :
    print(k, ':', v)
    
# Problèmes :
## Symboles non-anglophones : Allemand, Français, Langues de l'Est, symbole µ (minoritaire)
## Les titres trèèès longs (max 36 tokens) peuvent plus influencer les tendances que d'autres
## Il y a des listes de token vides

# Corrigé :
## Il reste des termes comme 12th, 11th, 1st, 2nd, 30th, ...
## Il reste des 100GB, 000, 24fps, et toute sorte de termes pleins de chiffres
