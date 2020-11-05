# Projet Intégré

## Dans le dossier Dict :
	Sauvegardes des dictionnaires à chaque étape du traitement
### Ordre des sauvegardes :
  * original_titles
  * cleaned
  * onlyenglish
  * tokenized
  * nostopwords
  * lemmatized (version finale)

## Pour charger un .pickle :
```python
import pickle

with open('dict/lemmatized.pickle', 'rb') as handle:
	article_titles = pickle.load(handle)
```

## Pré-traitement des données :
  * INPUT: fichier publication.csv
  * OUTPUT: dictionnaire de listes { idconf:[tokens], idconf:[tokens], ...}
  * Utilisation de dictionnaire : + rapide que les listes sur un gros jeu de données