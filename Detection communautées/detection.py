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
from Cluster import Cluster
from Graph import Graph

os.chdir("c:/Users/louis/OneDrive/Documents/Master 1/Projet Intégré")

import igraph

global i
global g

def start(authors_list, publications_list):
    print('authors len: ', len(authors_list))
    print('publication len: ',len(publications_list))
    g = igraph.Graph()
    g = set_graph(g, authors_list, publications_list)
    i = detection_by_infomap(g)
    Cluster.get().set_cluster(i)
    Graph.get().set_graph(g)
    networkX_graph=Display.init_graph(g, i)
    return g
    # display_graph_information(g)
    
def sub_graph(author):
    sub_graph_list = []
    sub_graph_cluster = []
    graph = Graph.get().get_graph()
    for neigh in graph.neighbors(author):
        for clust in Cluster.get().get_cluster():
            if graph.vs[neigh].index in clust and clust not in sub_graph_cluster:
                print(clust)
                sub_graph_list = sub_graph_list + clust
                sub_graph_cluster.append(clust)
    sub_graph = graph.subgraph(sub_graph_list)
    sub_graph_cluster = detection_fast_greedy(sub_graph)
    # sub_graph_cluster = detection_by_infomap(sub_graph)
    Cluster.get().set_cluster(sub_graph_cluster)
    Graph.get().set_graph(sub_graph)
    Display.init_graph(sub_graph, sub_graph_cluster)
    return
    # print(Cluster.get().get_cluster())
    # and clust not in sub_graph_list

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

def detection_fast_greedy(g):
    i = g.community_infomap(edge_weights="weight", trials=100)
    print('i: ',i)
    return i















