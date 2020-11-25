#%% Importation des librairies
import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from fbprophet import Prophet
from pandas import to_datetime
from matplotlib.dates import (AutoDateLocator, AutoDateFormatter)
os.chdir(os.path.dirname(os.path.realpath(__file__))) # On indique le dossier dans lequel on est

#%% Importation du fichier publication
df = pd.read_csv('data/publication.csv', sep = ',', encoding = 'cp1252')

#%% Fonctions de sauvegarde et de chargement de dictionnaires avec des fichiers
# Utilisé pour gagner du temps afin de ne pas avoir à re-exécuter tout
# à chaque ré-ouverture
def save_dict(dico, filename) :
    with open(filename+".pickle", 'wb') as handle:
        pickle.dump(dico, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def load_dict(filename) :
    with open(filename+".pickle", 'rb') as handle:
        return(pickle.load(handle))
    
#%%
def save(var, filename) :
    with open("prediction/"+filename+".pickle", 'wb') as handle:
        pickle.dump(var, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def load(filename) :
    with open("prediction/"+filename+".pickle", 'rb') as handle:
        return(pickle.load(handle))
    
#%% Chargement des données de Davy et Romain
romain = load_dict('pickle/topic_romain')
davy = load_dict('pickle/topic_davy')

#%%
davy_cleaned = davy.reset_index()
romain_cleaned = romain.reset_index()
davy_cleaned = davy_cleaned.rename(columns={'Titles_ID':'id_publication'})
romain_cleaned = romain_cleaned.rename(columns={'index':'id_publication'})
topics_davy = davy_cleaned[['Keywords', 'Dominant_Topic']]
topics_romain = romain_cleaned[['description', 'label']]

topics_davy = topics_davy.drop_duplicates() 
topics_romain = topics_romain.drop_duplicates()

topics_davy = topics_davy.sort_values(by=['Dominant_Topic'])
topics_davy['Dominant_Topic'] = topics_davy['Dominant_Topic'].astype(int)
topics_romain = topics_romain.sort_values(by=['label'])

print(topics_davy)
print(topics_romain)

#%% Transformation des données
dataD = pd.merge(df, davy, on='id_publication') # Fusion de publication et des données de Davy sur la colonne id_publication
dataD = dataD[['date_pub', 'Dominant_Topic']] # On garde uniquement ces deux colonnes
dataD.columns = ['date', 'topic'] # On les renomme
print(dataD)
dataR = pd.merge(df, romain, on='id_publication') # Fusion de publication et des données de Romain sur la colonne id_publication
dataR = dataR[['date_pub', 'label']] # On garde uniquement ces deux colonnes
dataR.columns = ['date', 'topic'] # On les renomme
print(dataR)

#%% Fonction plot de Prophet.model
def plot(
    m, fcst, title, ax=None, uncertainty=True, plot_cap=True, xlabel='ds', ylabel='y',
    figsize=(10, 6)
):
    """Plot the Prophet forecast.
    Parameters
    ----------
    m: Prophet model.
    fcst: pd.DataFrame output of m.predict.
    ax: Optional matplotlib axes on which to plot.
    uncertainty: Optional boolean to plot uncertainty intervals, which will
        only be done if m.uncertainty_samples > 0.
    plot_cap: Optional boolean indicating if the capacity should be shown
        in the figure, if available.
    xlabel: Optional label name on X-axis
    ylabel: Optional label name on Y-axis
    figsize: Optional tuple width, height in inches.
    Returns
    -------
    A matplotlib figure.
    """
    # Création de axes de Matplotlib
    if ax is None:
        fig = plt.figure(facecolor='w', figsize=figsize)
        ax = fig.add_subplot(111)
    else:
        fig = ax.get_figure()
    # Ajout des courbes 
    fcst_t = fcst['ds'].dt.to_pydatetime() # Conversion de la date en pydatetime pour axes
    ax.plot(m.history['ds'].dt.to_pydatetime(), m.history['y'], '--m') # Vérité # (historique des dates, historique des valeurs, style de courbe)
    ax.plot(fcst_t, fcst['yhat'], '--r') # Prédiction # (dates prédites, valeurs prédites, style de courbe)
    if 'cap' in fcst and plot_cap:
        ax.plot(fcst_t, fcst['cap'], ls='--', c='k')
    if m.logistic_floor and 'floor' in fcst and plot_cap:
        ax.plot(fcst_t, fcst['floor'], ls='--', c='k')
    # Dessin de l'incertitude
    if uncertainty and m.uncertainty_samples:
        ax.fill_between(fcst_t, fcst['yhat_lower'], fcst['yhat_upper'], color='red', alpha=0.2) # (dates prédites, prédiction minimale, prédiction maximale, couleur, transparence)
    # Specify formatting to workaround matplotlib issue #12925
    locator = AutoDateLocator(interval_multiples=False)
    formatter = AutoDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.grid(True, which='major', c='gray', ls='-', lw=1, alpha=0.2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()
    return fig

#%% A exécuter avant le '#%% Calcul de prédiction' pour utiliser les données de Davy
target = dataD
name = 'topic_davy'
#%% A exécuter avant le '#%% Calcul de prédiction' pour utiliser les données de Romain
target = dataR
name = 'topic_romain'
#%% Calcul de prédiction
# Création d'une liste de topic à partir de target pour pouvoir itérer dessus
topic_list = target[['topic']]
topic_list = topic_list.drop_duplicates() # On supprime les doublons pour n'avoir qu'une fois chaque topic
topic_list = topic_list.sort_values(by=['topic']) # On les trie par ordre croissant
indexNames = topic_list[topic_list['topic'] == 0].index # On trouve l'index qui a pour valeur topic = 0
topic_list = topic_list.drop(indexNames) # On le supprime
topic_list['topic'] = topic_list['topic'].astype(int) # Conversion de tous les topic en entiers

# Pour chaque topic dans la liste des topics
for topic in topic_list.values:
    data = target.loc[target['topic'] == topic[0]] # On prend uniquement les lignes qui ont pour valeur le bon topic
    data['date'] = to_datetime(data['date']).dt.strftime('%Y-%m') # On convertit la date au bon format (Année-Mois)
    data = data.sort_values(by=['date']) # On trie en fonction de la date
    data = data.groupby('date').count() # On regroupe les données par date, maintenant on a le nombre de fois que ce topic à été posté à telle date
    data = data.reset_index() # On enlève l'index créé par groupby
    data.columns = ['ds', 'y'] # Changement du nom des colonnes pour l'adapter au Modèle
    #data.plot(figsize=(19,4), style='b--') # Représentation des données sous forme de graphique
    save_dict(data, 'topic%s' % str(topic))
    print(data)

    #data['y'] = data['y'] - data['y'].shift(1)
    #data = data[1:]
    
    model = Prophet() # Initialisation du modèle
    model.fit(data) # On 'fit' le modèle aux données
    
    # Création d'une liste de date qu'on veut prédire
    future = list()
    # i => années (range(19,21) => 2019, 2020)
    for i in range(19,21):
        # j => mois (range(1,13) => 1...12)
        for j in range(1,13):
            date = '20'+str(i)+'-'+str(j) # date = 20i-j
            future.append([date]) # On ajoute la date à notre liste
    future = pd.DataFrame(future) # On créé un dataframe à partir de la liste
    future.columns = ['ds'] # On renomme la colonne
    future['ds'] = to_datetime(future['ds']) # On convertit la date en Datetime
    
    forecast = model.predict(future) # On appelle la fonction predict du modèle qui va calculer ça pour la période 'future'
    
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].head()) # Affichage des données de la prédiction
    plot(model, forecast, 'Topic n°%s Monthly Frequency' % topic[0], xlabel='Months', ylabel='Topic Count') # Appel de la fonction plot pour afficher la prédiction + la vérité en un graphique 
    plt.savefig('./prediction/%s/%s/data.png' % (name, str(topic[0]))) # Sauvegarde du graphique en .png   
    model.plot_components(forecast)
    plt.savefig('./prediction/%s/%s/trend.png' % (name, str(topic[0]))) # Sauvegarde du graphique en .png
    plt.show()
    save(model, '%s_model_%s' % (name, str(topic[0])))
    save(forecast, '%s_forecast_%s' % (name, str(topic[0])))
    
#%%
