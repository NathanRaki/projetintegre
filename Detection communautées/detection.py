# -*- coding: utf-8 -*-

"""
Spyder Editor

This is a temporary script file.
"""

import os

'''
Import classes
'''

import Display

os.chdir("c:/Users/louis/OneDrive/Documents/Master 1/Projet Intégré")

import igraph

def start(authors_list, publications_list):
    print('authors len: ', len(authors_list))
    print('publication len: ',len(publications_list))
    g = igraph.Graph()
    g = set_graph(g, authors_list, publications_list)
    i = detection_by_infomap(g)
    Display.init_graph(g, i)
    # display_graph_information(g)

"""
Set the graph
"""
def set_graph(g, authors_list, publications_list):
    g=set_vertices(g, authors_list)
    g=set_edges(g, publications_list)
    g = simplify_graph(g)
    return g

def set_vertices(g, authors):
    for author in authors:
        g.add_vertices(str(author.get_author_id()),{"author_name":author.get_author_name(),"id_author":author.get_author_id(), "name":author.get_author_id()})
    return g

def set_edges(g, publications):
    for publication in publications:
        for auth1 in range (0, len(publication.get_authors())):
            for auth2 in range(auth1 +1 , len(publication.get_authors())):
                g.add_edges([(publication.get_authors()[auth1],publication.get_authors()[auth2])],{"publication_id":publication.get_id_publication(), "publication_title":publication.get_article_title(), "publication_date":publication.get_publication_date(), "author_number": publication.get_nb_author(), "categorie": publication.get_categorie(), "weight":1})
    return g

def simplify_graph(g):
    g.simplify(combine_edges=dict(weight="sum", publication_id ="concat"))
    for e in g.es:
        e["publication_id"] = e["publication_id"].split("conf/")[1:]
    return g
        
"""
Communitity detection
"""

def detection_by_infomap(g):
    i = g.community_infomap(edge_weights="weight", trials=20)
    return i















