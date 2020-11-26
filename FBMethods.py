import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpld3 import plugins
from datetime import datetime
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import (AutoDateLocator, AutoDateFormatter, MonthLocator, num2date)

def plot_components(plot_data):
    # Lists all components to be plotted
    components = ['trend', 'yearly', 'forecast']
    # Create a Grid and Subplot for a beautiful Drawing
    gs = gridspec.GridSpec(2,2)
    fig = plt.figure(figsize=(25,8))
    ax1 = fig.add_subplot(gs[0,0])
    ax2 = fig.add_subplot(gs[0,1])
    ax3 = fig.add_subplot(gs[1,:])
    # for each component we want to plot
    for component in components:
        if component == 'trend':
            tooltip = plot_forecast_component(forecast = plot_data['forecast'],
                                              ax = ax1)
            plugins.connect(fig, tooltip) # Connect our tooltip plugin to the figure
        elif component == 'yearly':
            tooltip = plot_yearly(beta = plot_data['beta'],
                                  y_scale = plot_data['y_scale'],
                                  start = plot_data['start'],
                                  t_scale = plot_data['t_scale'],
                                  ax = ax2)
            plugins.connect(fig, tooltip) # Connect our tooltip plugin to the figure
        elif component == 'forecast':
            tooltip1, tooltip2 = plot_forecast(history=plot_data['history'],
                                               forecast=plot_data['forecast'],
                                               ax=ax3)
            plugins.connect(fig, tooltip1); plugins.connect(fig, tooltip2) # Connect our tooltip plugins to the figure

    fig.tight_layout() # Automatically adjusts subplot params so that the subplot(s) fits into the figure area
    return fig # Return the full figure

'''
    Dessine le plot de Prédiction sur un ax donné
'''
def plot_forecast(history, forecast, ax):
    # Conversion des dates en pydatetime pour les abscisses
    forecast_t = forecast['ds'].dt.to_pydatetime() # Dates des prédictions
    history_t = history['ds'].dt.to_pydatetime() # Dates des vraies données
    # Dessin d'une zone d'incertitude pour la prédiction
    ax.fill_between(forecast_t, forecast['yhat_lower'], forecast['yhat_upper'], color='red', alpha=0.2) # (dates prédites, prédiction minimale, prédiction maximale, couleur, transparence)
    # Dessin des courbes et récupération des points pour les tooltips
    p1 = ax.plot(history_t, history['y'], 'o-', ms=5, c='m')
    p2 = ax.plot(forecast_t, forecast['yhat'], 'o-', ms=5, c='r')
    # Formattage propre à Matplotlib
    locator = AutoDateLocator(interval_multiples=False)
    formatter = AutoDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    # Options pour la grille de fond
    ax.grid(True, which='major', c='gray', ls='-', lw=1, alpha=0.2)
    # Déclaration des noms pour l'abscisse et l'ordonnée
    ax.set_xlabel('Months', labelpad=10)
    ax.set_ylabel('Topic Frequency', labelpad=10)
    # Création des tooltips avec mpld3.plugins
    labels = ['%s-%s : %s' % (date.strftime("%B"), date.strftime("%Y"), str(int(y))) for date,y in zip(history_t, history['y'])]
    tooltip1 = plugins.PointLabelTooltip(p1[0], labels=labels, hoffset=10, voffset=10)
    labels = ['%s-%s : %s' % (date.strftime("%B"), date.strftime("%Y"), str(int(y))) for date,y in zip(forecast_t, forecast['yhat'])]
    tooltip2 = plugins.PointLabelTooltip(p2[0], labels=labels, voffset=10, hoffset=10)
    return tooltip1, tooltip2

'''
    Dessine le plot de Tendance sur un ax donné
'''
def plot_forecast_component(forecast, ax):
    # Conversion des dates en pydatetime pour l'abscisse
    forecast_t = forecast['ds'].dt.to_pydatetime()
    # Dessin des courbes et récupération des points pour les tooltips
    points = ax.plot(forecast_t, forecast['trend'], 'o-', ms=5, c='#0072B2')
    # Formattage propre à Matplotlib
    locator = AutoDateLocator(interval_multiples=False)
    formatter = AutoDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    # Options pour la grille de fond
    ax.grid(True, which='major', c='gray', ls='-', lw=1, alpha=0.2)
    # Déclaration des noms pour l'abscisse et l'ordonnée
    ax.set_xlabel('Months', labelpad=10)
    ax.set_ylabel('Trend')
    # Création des tooltips avec mpld3.plugins
    labels = ['%s-%s : %s' % (date.strftime("%B"), date.strftime("%Y"), str(int(y))) for date,y in zip(forecast_t, forecast['trend'])]
    tooltip = plugins.PointLabelTooltip(points[0], labels=labels, voffset=10, hoffset=10)
    return tooltip

'''
    Dessine le plot de Saisonnalité sur un ax donné
'''
def plot_yearly(beta, y_scale, start, t_scale, ax):
    # Créé une séquence de dates pour une saisonnalité du 1er Janvier au 31 Déembre
    days = pd.date_range(start='2017-01-01', periods=365)
    # Préparation d'un dataframe pour la saisonnalité
    df_dict = {'ds': days}
    df_y = pd.DataFrame(df_dict)
    df_y['ds'] = pd.to_datetime(df_y['ds'])
    df_y = df_y.sort_values('ds')
    df_y = df_y.reset_index(drop=True)
    # Calcul de la saisonnalité
    seas = predict_seasonal_components(beta=beta, y_scale=y_scale, df=df_y)
    # Conversion des dates en pydatetime pour l'abscisse
    df_y_t = df_y['ds'].dt.to_pydatetime()
    # Dessin des courbes et récupération des points pour les tooltips
    points = ax.plot(df_y_t, seas['yearly'], 'o-', ms=3, c='#0072B2')
    # Formattage propre à Matplotlib
    months = MonthLocator(range(1, 13), bymonthday=1, interval=2)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos=None: '{dt:%B} {dt.day}'.format(dt=num2date(x))))
    ax.xaxis.set_major_locator(months)
    # Options pour la grille de fond
    ax.grid(True, which='major', c='gray', ls='-', lw=1, alpha=0.2)
    # Déclaration des noms pour l'abscisse et l'ordonnée
    ax.set_xlabel('Months', labelpad=10)
    ax.set_ylabel('Seasonality')
    # Création des tooltips avec mpld3.plugins
    labels = ['%s-%s : %s' % (date.strftime("%B"), date.strftime("%Y"), str(int(y))) for date,y in zip(df_y_t, seas['yearly'])]
    tooltip = plugins.PointLabelTooltip(points[0], labels=labels, voffset=10, hoffset=10)
    return tooltip

'''
    Prédit les composants de saisonnalité
'''
def predict_seasonal_components(beta, y_scale, df):
    seasonal_features = make_seasonality_features(df['ds'], 365.25, 10, 'yearly')
    X = seasonal_features.values
    data = {}
    beta_c = beta * [1 for i in range(len(beta))]

    comp = np.matmul(X, beta_c.transpose())
    comp *= y_scale
    data['yearly'] = np.nanmean(comp, axis=1)
    return pd.DataFrame(data)

'''
    Créé un Data Frame avec les fonctionnalités de la saisonnalité
'''
def make_seasonality_features(dates, period, series_order, prefix):
    features = fourier_series(dates, period, series_order)
    columns = [ '{}_delim_{}'.format(prefix, i + 1) for i in range(features.shape[1]) ]
    return pd.DataFrame(features, columns=columns)

'''
    Fournit une Série de Fourier avec les données passées en paramètre
'''
def fourier_series(dates, period, series_order):
    # convert to days since epoch
    t = np.array((dates - datetime(1970, 1, 1)).dt.total_seconds().astype(np.float)) / (3600 * 24.)
    return np.column_stack([
        fun((2.0 * (i + 1) * np.pi * t / period))
        for i in range(series_order)
        for fun in (np.sin, np.cos)
    ])
