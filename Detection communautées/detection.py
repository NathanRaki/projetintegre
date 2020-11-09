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

g = igraph.Graph()

def start():
    set_graph()
    display_graph()
    # display_graph_information()

"""
Set the graph
"""
def set_graph():
    auth_dict=get_vertices()
    set_vertices(auth_dict)
    edgeslist=get_link_of_author()
    set_edges(edgeslist)
    simplify_graph()

def get_vertices():
    auth_number = 0
    auth_dict = {}
    for auth_id, auth_name in author.itertuples(index=False):
        auth_dict[auth_number] = {"author_id":auth_id,"name":str(auth_name)}
        auth_number += 1
    return auth_dict

def set_vertices(authdict):
    for author in authdict.values():
        g.add_vertices(str(author["author_id"]),{"author_name":author["name"],"id_author":author["author_id"], "name":author["author_id"]})

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
    return linked_auth_tuple

def set_tuple(authlist):
    tuple_list = []
    for i in range(0,len(authlist)):
        for j in range(i+1,len(authlist)):
            tuple_list.append((authlist[i],authlist[j]))
    return tuple_list

def simplify_graph():
    g.es["weight"]=1
    g.simplify(combine_edges="sum")
    return


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


def linked_cluster(clusters):
    cluster = []
    for i in range(0,len(clusters)):
        print(i, ' : ', clusters[i])
        for node in clusters[i]:
            for j in range (i+1, len(clusters)):
                if(node in clusters[j]):
                    cluster.append((i,j))
    print(cluster)

start()














