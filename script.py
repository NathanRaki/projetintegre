##### Verifying Encoding #####
'''
import os

filenames = os.listdir(os.getcwd()+'/data')
filenames = [f for f in filenames if (f.lower().endswith('.csv'))]

for k in filenames :
	with open('data/'+k) as f :
		print(k, f.encoding)
#'''
##############################

##### Reading CSV files #####
#-----'''
import pandas as pd

author = pd.read_csv('data/author.csv', sep = ',', encoding = 'cp1252')
publication = pd.read_csv('data/publication.csv', sep = ',', encoding = 'cp1252')
keyword = pd.read_csv('data/keyword.csv', sep = ',', encoding = 'cp1252')
year = pd.read_csv('data/year.csv', sep = ',', encoding = 'cp1252')
publication_author = pd.read_csv('data/publication_author.csv', sep = ',', encoding = 'cp1252')
publication_keywords = pd.read_csv('data/Publication_keywords.csv', sep = ',', encoding = 'cp1252')
publication_year = pd.read_csv('data/publication_year.csv', sep = ',', encoding = 'cp1252')

del publication['categorie'] # suppression de la colonne qui ne contient que des proceeding

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.min_rows', 25)
pd.set_option('display.max_rows', 25)
#'''
#############################

##### Mananing Data #####
#'''
liste_publication = set(publication_keywords['id_publication'])
liste_publication = list(liste_publication)
liste_publication.sort()

liste_publication_copy = liste_publication.copy()

keywords_per_publication = dict()
for key in liste_publication_copy :
	keywords_per_publication[key] = []

for i in range(100) :
	elt = publication_keywords['id_publication'].iloc[i]
	if (elt == liste_publication_copy[0]) :
		keywords_per_publication[elt].append(publication_keywords['keyword'].iloc[i])
	else :
		liste_publication_copy.pop(0)

#for key in liste_publication_copy :
#	if (keywords_per_publication[key] != []) :
#		print(keywords_per_publication[key])
#'''
#########################

# Conversion des titres en minuscule
for i in range(len(publication)) :
	publication['article_title'][i] = publication['article_title'][i].lower()
	print(str(i) + ": " + publication['article_title'][i])