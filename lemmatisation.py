#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 19:58:51 2020

@author: raki
"""

#%% Importing Libraries
import pandas as pd
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.stem.snowball import EnglishStemmer
from collections import defaultdict

#%% Loading Data
publication = pd.read_csv('/home/raki/Cours/projet_integre/data/publication.csv', sep = ',', encoding = 'cp1252').to_dict()

#%% Lowering Titles
lowered_titles = defaultdict(set)
for k,v in publication['article_title'].items() :
    lowered_titles[k] = v.lower()

#%% Tokenizing Titles
tokenizer = nltk.RegexpTokenizer(r'\w+')
tokenized_titles = defaultdict(set)
for k,v in lowered_titles.items() :
    tokenized_titles[k] = tokenizer.tokenize(v)
    
#%% Deleting Stopwords
sw = set()
sw.update(tuple(nltk.corpus.stopwords.words('english')))
optimized_titles = defaultdict(list)
for k,v in tokenized_titles.items() :
    optimized_titles[k] = [word for word in v if word not in sw]
    
#%% Lemmatization
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

#%% Stemming (Racinisation)
stemmer = EnglishStemmer()
stemmed_titles = defaultdict(list)
for k,v in lemmatized_titles.items() :
    stemmed_titles[k] = [stemmer.stem(w) for w in v]
    
#%% Print Area

for x in lemmatized_titles :
    print(x, ':', lemmatized_titles[x])
