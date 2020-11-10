# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 12:56:49 2020

@author: louis
"""

import os

os.chdir("c:/Users/louis/OneDrive/Documents/GitHub/projetintegre/Detection communautées")

'''
Import classes
'''
from Author import Author
from Publication import Publication
import detection
import Data_filter

os.chdir("c:/Users/louis/OneDrive/Documents/Master 1/Projet Intégré")

import pandas

# publi = pandas.read_excel("test.xlsx")
# author = pandas.read_excel("test_author.xlsx")
#publi = pandas.read_csv("publication_author.csv", sep = ';', encoding = "ISO-8859-1")
#author = pandas.read_csv("author.csv", sep = ';', encoding = "ISO-8859-1")


def main():
    print('start')
    # publi_test = Publication(1, '10/02/2020', 1, 'test')
    # author_test = Author(1, 'toto')
    
    # print('publi_test: ', publi_test)
    # print('author_test: ', author_test)
    import_file()
    Data_filter.data_filter(publication_year="2018")
    # detection.start()
    
def import_file():
    publi_author = pandas.read_excel("test.xlsx")
    author = pandas.read_excel("test_author.xlsx")
    publication = pandas.read_excel("publication_test.xlsx")
    #publi_author = pandas.read_csv("publication_author.csv", sep = ';', encoding = "ISO-8859-1")
    #author = pandas.read_csv("author.csv", sep = ';', encoding = "ISO-8859-1")
    initialize_publication(publication)
    initialize_author(author)
    initialize_link_author_publi(publi_author)
    
def initialize_publication(publications):
    for index, value in publications.iterrows():
        Publication(value["id_publication"], value["date_pub"], value["nbr_authors"],value["article_title"], value["categorie"])
    
def initialize_author(authors):
    for index, value in authors.iterrows():
        Author(value["id_author"], value["name_author"], value["nbr_publication"])
        
def initialize_link_author_publi(publi_author): 
    publications = {}
    authors = {}
    for index, value in publi_author.iterrows():
        if value['id_publication'] in publications:
            publications[value['id_publication']].append(value['id_author'])
        else:
            publications[value['id_publication']] = [value['id_author']]
        if value['id_author'] in authors:
            authors[value['id_author']].append(value['id_publication'])
        else:
            authors[value['id_author']] = [value['id_publication']]
    for index, value in publications.items():
        Publication.get(index)[0].set_authors(value)
        
    for index, value in authors.items():
        Author.get(index)[0].set_publication(value)

    
if __name__ == "__main__":
    main()