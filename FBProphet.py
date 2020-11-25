#%% Load Packages
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
import pickle
import pandas as pd
import FBMethods as fm
import matplotlib.pyplot as plt
from fbprophet import Prophet
from pandas import to_datetime

#%%
def save(var, filename) :
    with open(filename+".pickle", 'wb') as handle:
        pickle.dump(var, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
def load(filename) :
    with open(filename+".pickle", 'rb') as handle:
        return(pickle.load(handle))

#%%
pd.set_option('display.max_colwidth', None)
df = pd.read_csv('data/publication.csv', sep = ',', encoding = 'cp1252')

#%%
data = load('pickle/topic_davy')
print(df.head())

#%%
topics = data[['Dominant_Topic', 'Keywords']].drop_duplicates()
topics['Dominant_Topic'] = topics['Dominant_Topic'].astype(int)
topics = topics.sort_values(by=['Dominant_Topic'])
topics = topics.reset_index()
topics = topics.drop(columns="index")
topics.columns = ['topic', 'tokens']
print(topics)

#%%
cleaned_data = data.reset_index()
cleaned_data = cleaned_data.rename(columns={'Titles_ID':'id_publication'})
final_data = pd.merge(df, cleaned_data, on='id_publication')
final_data = final_data[['date_pub', 'Dominant_Topic']]
final_data.columns = ['date', 'topic']
final_data['topic'] = final_data['topic'].astype(int)
print(final_data.head())

#%%
topic_number = 7
topic0 = final_data.loc[final_data['topic'] == topic_number]
topic0['date'] = to_datetime(topic0['date']).dt.strftime('%Y-%m')
topic0 = topic0.sort_values(by=['date'])
topic0 = topic0.groupby('date').count()
topic0 = topic0.reset_index()
topic0.columns = ['ds','y']
print(topic0.head())

#%%
model = Prophet()
model.fit(topic0)

#%%
future = list()
for i in range(19,21):
    for j in range(1,13):
        date = '20%s-%s' % (str(i), str(j))
        future.append([date])
future = pd.DataFrame(future)
future.columns = ['ds']
future['ds'] = to_datetime(future['ds'])

forecast = model.predict(future)

#%%
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].head())

#%%
fm.plot_components(model, forecast)
plt.show()

#%%
fm.plot(model, forecast, 'Topic => %s' % topics.loc[topics['topic'] == topic_number]['tokens'].to_string(index=False), xlabel='Months', ylabel='Topic Count')
plt.show()

