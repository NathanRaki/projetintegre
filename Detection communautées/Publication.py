# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 12:15:45 2020

@author: louis
"""

# import datetime

class Publication():
    '''
        All publications of DBLP
        
        Attributes gave by the Publication.csv file: 
            id_publication: str --> The id of the publication
            date_publication: datetime --> The date of the publication of the article/conference
            nb_author: integer --> number of author on the publication. 
                                    The name of each author will be retreive with the 
                                    file publication_author.csv
            article_title: str --> The title of the publication
            categorie: str --> The categorie of the publication. 
                                For now the only value is proceeding but it 
                                could be other values in the futur
    
        Attributes gave by the Publication_Author.csv file
            authors: [Author] --> A list of all the authors id of the publication. 
                                All the authors of the list are instance of the class Author
    '''
    
    instances = []
    
    def __init__(self, id_publication, date_publication, nb_author, article_title, categorie='proceeding', authors = []):
        self.__id_publication = str(id_publication)
        self.__date_publication = date_publication
        self.__nb_author = nb_author
        self.__article_title = article_title
        self.__categorie = categorie
        self.__authors = authors
        Publication.instances.append(self)
    
    def set_authors(self, author):
        self.__authors = author
        # self.__authors.append(author)
    
    def get_authors(self):
        return self.__authors
    
    def get_id_publication(self):
        return self.__id_publication
    
    def get_publication_date(self):
        return self.__date_publication 

    def get_nb_author(self):
        return self.__nb_author
    
    def get_article_title(self):
        return self.__article_title
    
    def get_categorie(self):
        return self.__categorie
    
    @classmethod
    def get(cls, value):
        return [inst for inst in cls.instances if inst.__id_publication == value]
    
    @classmethod
    def get_all_instances(cls):
        return [inst for inst in cls.instances]
    
    def __str__(self):
        return self.__id_publication + ', ' + str(self.__date_publication) + ', ' + self.__article_title