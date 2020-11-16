#%%
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import (AutoDateLocator, AutoDateFormatter)
import pickle
os.chdir('/home/raki/wd/cours/projet_integre/')

#%%
df = pd.read_csv('data/publication.csv', sep = ',', encoding = 'cp1252')
print(df)

#%% Fonctions de sauvegarde et de chargement de dictionnaires avec des fichiers
# Utilisé pour gagner du temps afin de ne pas avoir à re-exécuter tout
# à chaque ré-ouverture
def save_dict(dico, filename) :
    with open("pickle/"+filename+".pickle", 'wb') as handle:
        pickle.dump(dico, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def load_dict(filename) :
    with open("pickle/"+filename+".pickle", 'rb') as handle:
        return(pickle.load(handle))
    
#%%
romain = load_dict('topic_romain')
davy = load_dict('topic_davy')

#%% Merge publication and data
davy = davy.reset_index()
davy = davy.rename(columns={'Titles_ID':'id_publication'})
romain = romain.reset_index()
romain = romain.rename(columns = {'index':'id_publication'})

dataD = pd.merge(df, davy, on='id_publication')
dataD = dataD[['date_pub', 'Dominant_Topic']]
dataD.columns = ['date', 'topic']
print(dataD)
dataR = pd.merge(df, romain, on='id_publication')
dataR = dataR[['date_pub', 'label']]
dataR.columns = ['date', 'topic']
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
    if ax is None:
        fig = plt.figure(facecolor='w', figsize=figsize)
        ax = fig.add_subplot(111)
    else:
        fig = ax.get_figure()
    fcst_t = fcst['ds'].dt.to_pydatetime()
    ax.plot(m.history['ds'].dt.to_pydatetime(), m.history['y'], '--m') # Truth plot
    ax.plot(fcst_t, fcst['yhat'], '--r')
    if 'cap' in fcst and plot_cap:
        ax.plot(fcst_t, fcst['cap'], ls='--', c='k')
    if m.logistic_floor and 'floor' in fcst and plot_cap:
        ax.plot(fcst_t, fcst['floor'], ls='--', c='k')
    if uncertainty and m.uncertainty_samples:
        ax.fill_between(fcst_t, fcst['yhat_lower'], fcst['yhat_upper'],
                        color='red', alpha=0.2)
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

#%%
from fbprophet import Prophet
from pandas import to_datetime

target = dataD

topic_list = target[['topic']]
topic_list = topic_list.drop_duplicates()
topic_list = topic_list.sort_values(by=['topic'])

for topic in topic_list.values:
    data = target.loc[target['topic'] == topic[0]]
    data['date'] = to_datetime(data['date']).dt.strftime('%Y-%m')
    data = data.sort_values(by=['date'])
    data = data.groupby('date').sum()
    data = data.reset_index()
    data.columns = ['ds', 'y']
    print(data)
    
    #data.plot(figsize=(19,4), style='b--')
    
    model = Prophet()
    model.fit(data)
    
    future = list()
    for i in range(19,21):
        for j in range(1,13):
            date = '20'+str(i)+'-'+str(j)
            future.append([date])
    future = pd.DataFrame(future)
    future.columns = ['ds']
    future['ds'] = to_datetime(future['ds'])
    
    forecast = model.predict(future)
    
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].head())
    plot(model, forecast, 'Topic n°%s Monthly Frequency' % topic[0], xlabel='Months', ylabel='Topic Count')
    plt.savefig('./davy/%s.png' % str(topic[0]))
    plt.show()
