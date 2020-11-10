# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 12:14:27 2020

@author: louis
"""


import os

os.chdir("c:/Users/louis/OneDrive/Documents/GitHub/projetintegre/Detection communautées")

'''
Import classes
'''
from Author import Author
from Publication import Publication

"""
Filtrage des donnees sur publication & autheur
"""
def data_filter(publication_year = "All", publication_range="All", publication_categorie="All"):
    authors = Author.get_all_instances()
    publications = Publication.get_all_instances()
    # selected_author = []
    # selected_publication = []
    if publication_year != "All":
        for publication in publications:
            if publication["__date_publication"].year() != publication_year:
                publications.remove(publication)
    if publication_range != "All":
        for publication in publications:
            if publication["__date_publication"] < publication_range[0] or publication["__date_publication"] > publication_range[1]:
                publications.remove(publication)
    if publication_categorie != "All":
        for publication in publications:
            if publication["__categorie"] != publication_categorie:
                publications.remove(publication)
    return (publications, authors)