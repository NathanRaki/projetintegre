# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 08:51:36 2020

@author: louis
"""

class Author():
    '''
        Author description
        
        Attributes gave by the author.csv file:
            id_patient: str --> the Id of the author in DBLP
            name: str --> the name and surname of the author
            nb_publications: integer --> the number of publication of the author
            
        Attributes gave by the publication_author.csv file:
            publications: [Publication] --> A list of all the publicaiton id of the author. 
                                    All the publication of the list are instance of the class Publication
    '''
    instances = []
    
    def __init__(self, id_author, name, nbr_publications=0, publications=[]):
        self.__id_author=str(id_author)
        self.__name = name
        self.__nb_publications = nbr_publications
        self.__publications = publications
        Author.instances.append(self)

    def set_publication(self, publication):
        self.__publications = publication
        
    def get_author_id(self):
        return self.__id_author        

    def get_author_name(self):
        return self.__name
    
    def get_author_publications(self):
        return self.__publications
    
    @classmethod
    def get(cls, value):
         return [inst for inst in cls.instances if inst.__id_author == value]
    
    @classmethod
    def get_all_instances(cls):
        return [inst for inst in cls.instances]
        
    def __str__(self):
        return self.__id_author + ', ' + self.__name + ', ' + str(self.__nb_publications) 