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
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from collections import defaultdict
from gensim.parsing.preprocessing import STOPWORDS

#%% Loading Data
publication = pd.read_csv('/home/raki/Cours/projet_integre/data/publication.csv', sep = ',', encoding = 'cp1252')
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
for k,v in lowered_titles.items() :
    lowered_titles[k]=re.sub('\[.*?\]','',lowered_titles[k]) # suppression de toutes les expressions entre crochets
    lowered_titles[k]=re.sub('\{.*?\}','',lowered_titles[k]) # suppression de toutes les expressions entre accolades
    lowered_titles[k]=re.sub('\(.*?\)','',lowered_titles[k]) # suppression de toutes les expressions entre parenthèses
    lowered_titles[k]=re.sub('<.+>','',lowered_titles[k])    # suppression de toute la chaine qui se trouve entre un '<' et un '>' (1ère et dernière occurence)
    lowered_titles[k]=re.sub('\$.+\$','',lowered_titles[k])  # suppression de toute la chaine qui se trouve entre un '$' et un '$' (1ère et dernière occurence)
    lowered_titles[k]=re.sub('\S*[é,è,\^,_,&,:,@,#,$,\\\]\S*',' ',lowered_titles[k]) # suppression de tous les mots contenant un @ et #.. (@ et # seule inclus aussi)
    lowered_titles[k]=re.sub('[.,\,,!,?,%,*,§,²,~,\{,\}]',' ',lowered_titles[k]) # suppression des caractères spéciaux
    lowered_titles[k]=re.sub('[;,+,/]',' ',lowered_titles[k])
    lowered_titles[k]=re.sub(' +', ' ', lowered_titles[k]) # suppression des espaces en trop
    lowered_titles[k]=re.sub('-',' ',lowered_titles[k]) # remplacement des tirets par rien # choix qui se discute
    lowered_titles[k]=re.sub('(\s\d+\s|^\d+\s|\s\d+$)','',lowered_titles[k]) # suppression de tous les chiffres qui sont seuls
    lowered_titles[k]=re.sub('(\s(.)\s)|(^.\s)|(\s.$)','',lowered_titles[k]) #suppression des caractères d'une lettre
    lowered_titles[k]=re.sub('(\'s)','',lowered_titles[k]) # suppression des 's
    lowered_titles[k]=re.sub('\S*((january)|(february)|(march)|(april)|(may)|(june)|(july)|(august)|(september)|(october)|(november)|(december))\S*','',lowered_titles[k]) # suppression des expressions qui continnent un mois

#%% Tokenizing Titles
tokenizer = nltk.RegexpTokenizer(r'\w+')
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
        print(matching)

#%% Print Area
rows_number = 10
print_dict = dict(list(lemmatized_titles.items())[0:rows_number-1])
for k,v in print_dict.items() :
    print(k, ':', v)
