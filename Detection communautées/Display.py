# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 09:26:14 2020

@author: louis
"""

import os

os.chdir("c:/Users/louis/OneDrive/Documents/GitHub/projetintegre/Detection communautées")

# import Author
import Publication

import json
import random

import networkx as nx
from networkx.readwrite import json_graph

def init_graph(g, i):
    G = nx.Graph()
    for v in  g.vs:
        publication_list = []
        for e in v.all_edges():
            for publi in e['publication_id']:
                is_in = check_list_publication(Publication.Publication.get('conf/'+publi)[0].get_article_title(), publication_list)
                if is_in == False:
                    publication_list.append([Publication.Publication.get('conf/'+publi)[0].get_article_title(),str(Publication.Publication.get('conf/'+publi)[0].get_publication_date())])
        G.add_nodes_from([(v.index,{"id_author":v['id_author'], "author_name":v["author_name"], "publications":publication_list})])
    r = lambda: random.randint(0,255)
    attr = {}
    for clust in i:
        color = '#{:02x}{:02x}{:02x}'.format(r(), r(), r())
        for clu_node in clust:
            attr[clu_node] = {'color':color}
        nx.set_node_attributes(G, attr)
    for e in g.es:
        G.add_edges_from([(e.source, e.target), {"publications":e['publication_id'],"weight":e["weight"]}])
    d = json_graph.node_link_data(G)
    json.dump(d, open("c:/Users/louis/OneDrive/Documents/GitHub/projetintegre/Detection communautées/force/force.json", "w"))
    return d


def check_list_publication(publication_name, publication_list):
    for i in publication_list:
        if publication_name in i:
            return True
    return False