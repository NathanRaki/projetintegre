#%% Load Packages
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
import mpld3
import pickle
import pandas as pd
import FBMethods as fm
import matplotlib.pyplot as plt
from fbprophet import Prophet
from pandas import to_datetime

def save(var, filename) :
    with open(filename+".pickle", 'wb') as handle:
        pickle.dump(var, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def load(filename) :
    with open(filename+".pickle", 'rb') as handle:
        return(pickle.load(handle))

def get_topics(filename):
    data = load(filename)
    topics = data[['Dominant_Topic', 'Keywords']].drop_duplicates()
    topics['Dominant_Topic'] = topics['Dominant_Topic'].astype(int)
    topics = topics.sort_values(by=['Dominant_Topic'])
    topics = topics.reset_index()
    topics = topics.drop(columns="index")
    topics.columns = ['topic', 'tokens']
    _topics = {}
    for _, row in topics.iterrows():
        _topics[row['topic']] = row['tokens']
    return _topics

def generate_graphs(topic_number, topics_filename, id2date_filename):
    global id2date
    id2date = load(id2date_filename)
    data = load(topics_filename)
    cleaned_data = data.reset_index()
    cleaned_data = cleaned_data.rename(columns={'Titles_ID':'id_publication'})
    final_data = pd.merge(id2date, cleaned_data, on='id_publication')
    final_data = final_data[['date_pub', 'Dominant_Topic']]
    final_data.columns = ['date', 'topic']
    final_data['topic'] = final_data['topic'].astype(int)

    future = list()
    for i in range(19,22):
        for j in range(1,13):
            date = '20%s-%s' % (str(i), str(j))
            future.append([date])
    future = pd.DataFrame(future)
    future.columns = ['ds']
    future['ds'] = to_datetime(future['ds'])

    topic_data = final_data.loc[final_data['topic'] == topic_number]
    topic_data['date'] = to_datetime(topic_data['date']).dt.strftime('%Y-%m')
    topic_data = topic_data.sort_values(by=['date'])
    topic_data = topic_data.groupby('date').count()
    topic_data = topic_data.reset_index()
    topic_data.columns = ['ds', 'y']
    topic_data = topic_data[~(topic_data['ds'] < '2017-01-01')]
    model = Prophet(weekly_seasonality=False, daily_seasonality=False)
    model.fit(topic_data)
    
    forecast = model.predict(future)
    
    plot_data = {}
    plot_data['start'] = model.start
    plot_data['y_scale'] = model.y_scale
    plot_data['t_scale'] = model.t_scale
    plot_data['beta'] = model.params['beta']
    plot_data['forecast'] = forecast
    plot_data['history'] = model.history
    fig = fm.plot_components(plot_data)
    #fig = model.plot(forecast)
    #model.plot_components(forecast)
    plt.savefig('prophet')
    mpld3.save_html(fig, "figures/figure_%s.html" % topic_number)
    

## Utilisation :
# Récupération des topics =>
topics = get_topics('pickle/df_topic')
# Génération du html =>
for i in range(len(topics)):
    generate_graphs(
        topic_number = i,
        topics_filename = 'pickle/df_topic',
        id2date_filename = 'pickle/df_new_data'
    )