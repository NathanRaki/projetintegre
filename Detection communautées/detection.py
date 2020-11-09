# -*- coding: utf-8 -*-

"""
Spyder Editor

This is a temporary script file.
"""

import os

os.chdir("c:/Users/louis/OneDrive/Documents/GitHub/projetintegre/Detection communautées")

'''
Import classes
'''
from Author import Author
from Publication import Publication

os.chdir("c:/Users/louis/OneDrive/Documents/Master 1/Projet Intégré")

import pandas
import igraph

publi = pandas.read_excel("test.xlsx")
author = pandas.read_excel("test_author.xlsx")
#publi = pandas.read_csv("publication_author.csv", sep = ';', encoding = "ISO-8859-1")
#author = pandas.read_csv("author.csv", sep = ';', encoding = "ISO-8859-1")

global g

def start():
    g = igraph.Graph()
    set_graph(g)
    # display_graph()
    # display_graph_information()

"""
Set the graph
"""
def set_graph(g):
    authors = get_authors()
    publications = get_publications()
    set_vertices(g, authors)
    set_edges(g, publications)
    simplify_graph(g)

def get_authors():
    return Author.get_all_instances()

def get_publications():
    return Publication.get_all_instances()

def set_vertices(g, authors):
    for author in authors:
        g.add_vertices(str(author.get_author_id()),{"author_name":author.get_author_name(),"id_author":author.get_author_id(), "name":author.get_author_id()})


def set_edges(g, publications):
    for publication in publications:
        for auth1 in range (0, len(publication.get_authors())):
            for auth2 in range(auth1 +1 , len(publication.get_authors())):
                g.add_edges([(publication.get_authors()[auth1],publication.get_authors()[auth2])],{"publication_id":publication.get_id_publication(), "publication_title":publication.get_article_title(), "publication_date":publication.get_publication_date(), "author_number": publication.get_nb_author(), "categorie": publication.get_categorie(), "weight":1})

def simplify_graph(g):
    g.simplify(combine_edges=dict(weight="sum"))

"""
display graph
"""
def display_graph():
    print('display')
    # layout = g.layout("kk")
    # g.simplify()
    igraph.plot(g, "social_network_test.pdf")
    #igraph.plot(g, "social_network2.pdf", layout = layout)
    i = g.community_infomap(edge_weights="weight", trials=20)
    #i = g.community_edge_betweenness(None, False)
    # linked_cluster(i)
    # print(i)
    params = visualize_params()
    colors = ["#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00"]
    g.vs['color'] = [None]
    for clid, cluster in enumerate(i):
        for member in cluster:
            g.vs[member]['color'] = colors[clid%4]
            g.vs[member]['frame_width'] = -100
    g.vs['frame_width'] = 0
    igraph.plot(i, "social_network_infomap.svg", rescale=True, **params)
    igraph.plot(g, "social_network.svg", rescale=True, **params)
    # figure = igraph.plot(i, "social_network_infomap.pdf", **params)
    # figure.show()
    
def visualize_params():
    visual_style = {}
    visual_style["vertex_size"] = 10
    # visual_style["vertex_label"] = g.vs["author_name"]
    return visual_style

def display_graph_information():
    print('clique number: ', g.omega())()
    # print('modularity: ', g.modularity())
    # print('independance number: ', g.alpha())
    # print('coreness: ', g.shell_index())

# start()














