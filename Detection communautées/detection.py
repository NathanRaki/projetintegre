# -*- coding: utf-8 -*-

"""
Spyder Editor

This is a temporary script file.
"""

import os

os.chdir("c:/Users/Louis/Documents/Cours M1/Projet Intégré/Data")

import pandas
import igraph
#import cairocffi
#import pycairo

publi = pandas.read_excel("test.xlsx")
author = pandas.read_excel("test_author.xlsx")
#publi = pandas.read_csv("publication_author.csv", sep = ';', encoding = "ISO-8859-1")
#author = pandas.read_csv("author.csv", sep = ';', encoding = "ISO-8859-1")


g = igraph.Graph()

def start():
    set_graph()
    display_graph()
    


"""
Set the graph
"""
def set_graph():
    auth_list=get_vertices()
    set_vertices(auth_list)
    edgeslist=get_link_of_author()
    set_edges(edgeslist)

def get_vertices():
    auth_list = []
    for auth in author.id_author:
        auth_list.append(auth)
    return auth_list

def set_vertices(authlist):
    for vertice in authlist:
        g.add_vertices(vertice)
    g.vs["label"] = g.vs["name"]

def set_edges(edgeslist):
    return g.add_edges(edgeslist)

def get_link_of_author():
    cur_publi = publi['id_publication'][1]
    link_auth = []
    index = 0
    linked_auth_tuple = []
    for auth in publi.id_author:
        if(cur_publi==publi.id_publication[index]):
            link_auth.append(auth)
        else:
            for tup in set_tuple(link_auth):
                linked_auth_tuple.append(tup)
            link_auth=[auth]
            cur_publi=publi.id_publication[index]
        index += 1
    for tup in set_tuple(link_auth):
        linked_auth_tuple.append(tup)
    print(linked_auth_tuple)
    return linked_auth_tuple

def set_tuple(authlist):
    tuple_list = []
    for i in range(0,len(authlist)):
        for j in range(i+1,len(authlist)):
            tuple_list.append((authlist[i],authlist[j]))
    return tuple_list

"""
get information on the graph
"""

def get_max_edge():
    ebs = g.edge_betweenness()
    max_eb = max(ebs)
    return [g.es[idx].tuple for idx, eb in enumerate(ebs) if eb == max_eb]


"""
display graph
"""

def display_graph():
    print('display')
    #g.simplify()
    layout = g.layout("kk")
    igraph.plot(g, "social_network_test.pdf")
    #igraph.plot(g, "social_network2.pdf", layout = layout)
    #test_com_bet = g.community_edge_betweenness(False)
    #igraph.plot(test_com_bet, "test_com_bet.pdf", layout = layout)
    i = g.community_infomap()
    #i = g.community_edge_betweenness(None, False)
    #print(i)
    colors = ["#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00"]
    g.vs['color'] = [None]
    for clid, cluster in enumerate(i):
        for member in cluster:
            g.vs[member]['color'] = colors[clid%4]
    g.vs['frame_width'] = 0
    igraph.plot(g, "social_network_clusted2.pdf")

start()














