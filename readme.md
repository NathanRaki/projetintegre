# Projet Intégré

## Dans le dossier Dict :
	Sauvegardes des dictionnaires à chaque étape du traitement
<<<<<<< HEAD
### Ordre des sauvegardes :
  * original_titles
  * cleaned
  * onlyenglish
  * tokenized
  * nostopwords
  * lemmatized (version finale)
=======
>>>>>>> main

## Pour charger un .pickle :
```python
import pickle

<<<<<<< HEAD
with open('dict/lemmatized.pickle', 'rb') as handle:
=======
with open('filename.pickle', 'rb') as handle:
>>>>>>> main
	article_titles = pickle.load(handle)
```

## Pré-traitement des données :
  * INPUT: fichier publication.csv
  * OUTPUT: dictionnaire de listes { idconf:[tokens], idconf:[tokens], ...}
  * Utilisation de dictionnaire : + rapide que les listes sur un gros jeu de données