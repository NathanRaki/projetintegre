# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 14:46:44 2020

@author: louis
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 12:39:18 2020

@author: louis
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 12:15:45 2020

@author: louis
"""

# import datetime

class Graph():

    instances = None
    
    def __init__(self):
        self.__graph = []
        Graph.instances=self
    
    def set_graph(self, graph):
        self.__graph = graph
        # self.__authors.append(author)
    
    def get_graph(self):
        return self.__graph
    
    @classmethod
    def get(cls):
        return cls.instances