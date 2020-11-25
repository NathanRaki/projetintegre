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

class Cluster():

    instances = []
    
    def __init__(self):
        self.__cluster = []
        Cluster.instances=self
    
    def set_cluster(self, cluster):
        self.__cluster = cluster
        # self.__authors.append(author)
    
    def get_cluster(self):
        return self.__cluster
    
    @classmethod
    def get(cls):
        return cls.instances