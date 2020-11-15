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
# from data_filter import *-

os.chdir("c:/Users/louis/OneDrive/Documents/Master 1/Projet Intégré")

import pandas
import datetime
import flask

def main():
    print('start')
    # arg = {}
    # arg['publication_year']=None
    # arg['publication_start_date'] = None
    # arg['publication_end_date']=None
    import_file()
    # get_graph(arg)

def get_graph(args):
    data = data_filter(args)
    detection.start(data[1], data[0])
    return True
    
def import_file():
    publi_author = pandas.read_excel("test.xlsx")
    author = pandas.read_excel("test_author.xlsx")
    publication = pandas.read_excel("publication_test.xlsx")
    # publi_author = pandas.read_csv("publication_author.csv", sep = ',', encoding = "ISO-8859-1")
    # author = pandas.read_csv("author.csv", sep = ',', encoding = "ISO-8859-1")
    # publication = pandas.read_csv("publication.csv", sep = ',', encoding = "ISO-8859-1")
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

def data_filter(args):
    authors = Author.get_all_instances()
    publications = Publication.get_all_instances()
    is_filter = False
    for index, value in args.items():
        if value != None:
            is_filter = True
    if is_filter == False:
        return (publications, authors)
    authors_list = []
    publication_list = []
    if args['publication_year'] != None:
        for publication in publications:
            if str(publication.get_publication_date().year) == str(args['publication_year']):
                publication_list.append(publication)
    if args['publication_start_date'] != None:
        for publication in publications:
            if publication.get_publication_date() > datetime.datetime.strptime(args['publication_start_date'], "%Y-%m-%d"):
                publication_list.append(publication)
    if args['publication_end_date'] != None:
        for publication in publications:
            if publication.get_publication_date() < datetime.datetime.strptime(args['publication_end_date'], "%Y-%m-%d"):
                publication_list.append(publication)
    # if publication_categorie != None:
    #     for publication in publications:
    #         if publication.get_categorie() != publication_categorie:
    #             publications.remove(publication)
    authors_list = filter_author(publication_list, authors)
    return (publication_list, authors_list)
    
def filter_author(publications, authors):
    author_list = []
    for author in authors:
        concerned = False
        publication=0
        while publication < len(publications) and concerned==False:
            if author.get_author_id() in publications[publication].get_authors():
                concerned = True
            publication += 1
        if concerned == True:
            author_list.append(author)
    return author_list

app = flask.Flask(__name__, static_folder="force")

@app.route("/get_graph", methods=['GET'])
def static_proxy():
    arg = {}
    arg['publication_year']=flask.request.args.get('publication_year')
    print('request: ',flask.request.args.get('publication_start_date'))
    arg['publication_start_date'] = flask.request.args.get('publication_start_date')
    arg['publication_end_date']=flask.request.args.get('publication_end_date')
    get_graph(arg)
    return app.send_static_file("force.html")

@app.route("/get_year_list")
def get_year_list():
    year_list = []
    for publication in Publication.get_all_instances():
        if publication.get_publication_date().year not in year_list:
            year_list.append(publication.get_publication_date().year)
    return str(year_list)

if __name__ == "__main__":
    main()
    print("\nGo to http://localhost:10546 to see the example\n")
    app.run(port=10546) 