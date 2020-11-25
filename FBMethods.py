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

def plot_forecast(history, forecast, ax):
    # Création de axes de Matplotlib
    fig = ax.get_figure()
    # Ajout des courbes 
    forecast_t = forecast['ds'].dt.to_pydatetime() # Conversion de la date en pydatetime pour axes
    history_t = history['ds'].dt.to_pydatetime()
    # Dessin de l'incertitude
    #ax.plot(forecast_t, forecast['yhat'], '--r') # Prédiction # (dates prédites, valeurs prédites, style de courbe)
    ax.fill_between(forecast_t, forecast['yhat_lower'], forecast['yhat_upper'], color='red', alpha=0.2) # (dates prédites, prédiction minimale, prédiction maximale, couleur, transparence)
    #uncert_points = ax.scatter(forecast_t, forecast['yhat'], c='r', s=30)
    p1 = ax.plot(history_t, history['y'], 'o-', ms=5, c='m')
    p2 = ax.plot(forecast_t, forecast['yhat'], 'o-', ms=5, c='r')
    # Specify formatting to workaround matplotlib issue #12925
    locator = AutoDateLocator(interval_multiples=False)
    formatter = AutoDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.grid(True, which='major', c='gray', ls='-', lw=1, alpha=0.2)
    ax.set_xlabel('Months', labelpad=10)
    ax.set_ylabel('Topic Frequency', labelpad=10)
    fig.tight_layout()
    labels = ['%s-%s : %s' % (date.strftime("%B"), date.strftime("%Y"), str(int(y))) for date,y in zip(history_t, history['y'])]
    tooltip1 = plugins.PointLabelTooltip(p1[0], labels=labels, hoffset=10, voffset=10)
    labels = ['%s-%s : %s' % (date.strftime("%B"), date.strftime("%Y"), str(int(y))) for date,y in zip(forecast_t, forecast['yhat'])]
    tooltip2 = plugins.PointLabelTooltip(p2[0], labels=labels, voffset=10, hoffset=10)
    return tooltip1, tooltip2

def plot_forecast_component(forecast, ax):
    forecast_t = forecast['ds'].dt.to_pydatetime()
    points = ax.plot(forecast_t, forecast['trend'], 'o-', ms=5, c='#0072B2')
    # Specify formatting to workaround matplotlib issue #12925
    locator = AutoDateLocator(interval_multiples=False)
    formatter = AutoDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.grid(True, which='major', c='gray', ls='-', lw=1, alpha=0.2)
    ax.set_xlabel('Months', labelpad=10)
    ax.set_ylabel('Trend')
    labels = ['%s-%s : %s' % (date.strftime("%B"), date.strftime("%Y"), str(int(y))) for date,y in zip(forecast_t, forecast['trend'])]
    tooltip = plugins.PointLabelTooltip(points[0], labels=labels, voffset=10, hoffset=10)
    return tooltip

def plot_yearly(beta, y_scale, start, t_scale, ax):
    # Compute yearly seasonality for a Jan 1 - Dec 31 sequence of dates.
    days = (pd.date_range(start='2017-01-01', periods=365) + pd.Timedelta(days=0))
    df_y = seasonality_plot_df(start, t_scale, days)
    seas = predict_seasonal_components(beta=beta, y_scale=y_scale, df=df_y)
    #print(seas[name])
    df_y_t = df_y['ds'].dt.to_pydatetime()
    points = ax.plot(df_y_t, seas['yearly'], 'o-', ms=3, c='#0072B2')
    ax.grid(True, which='major', c='gray', ls='-', lw=1, alpha=0.2)
    months = MonthLocator(range(1, 13), bymonthday=1, interval=2)
    ax.xaxis.set_major_formatter(FuncFormatter(
        lambda x, pos=None: '{dt:%B} {dt.day}'.format(dt=num2date(x))))
    ax.xaxis.set_major_locator(months)
    ax.set_xlabel('Months', labelpad=10)
    ax.set_ylabel('Seasonality')
    labels = ['%s-%s : %s' % (date.strftime("%B"), date.strftime("%Y"), str(int(y))) for date,y in zip(df_y_t, seas['yearly'])]
    tooltip = plugins.PointLabelTooltip(points[0], labels=labels, voffset=10, hoffset=10)
    return tooltip

def seasonality_plot_df(start, t_scale, ds):
    """Prepare dataframe for plotting seasonal components.

    Parameters
    ----------
    m: Prophet model.
    ds: List of dates for column ds.

    Returns
    -------
    A dataframe with seasonal components on ds.
    """
    df_dict = {'ds': ds, 'cap': 1., 'floor': 0.}
    df = pd.DataFrame(df_dict)
    df = setup_dataframe(start, t_scale, df)
    return df

def setup_dataframe(start, t_scale, df):
    """Prepare dataframe for fitting or predicting.

    Adds a time index and scales y. Creates auxiliary columns 't', 't_ix',
    'y_scaled', and 'cap_scaled'. These columns are used during both
    fitting and predicting.

    Parameters
    ----------
    df: pd.DataFrame with columns ds, y, and cap if logistic growth. Any
        specified additional regressors must also be present.
    initialize_scales: Boolean set scaling factors in self from df.

    Returns
    -------
    pd.DataFrame prepared for fitting or predicting.
    """
    df['ds'] = pd.to_datetime(df['ds'])

    df = df.sort_values('ds')
    df = df.reset_index(drop=True)
    
    df['t'] = (df['ds'] - start) / t_scale

    return df

def predict_seasonal_components(beta, y_scale, df):
    """Predict seasonality components, holidays, and added regressors.

    Parameters
    ----------
    df: Prediction dataframe.

    Returns
    -------
    Dataframe with seasonal components.
    """
    seasonal_features = make_seasonality_features(df['ds'], 365.25, 10, 'yearly')
    X = seasonal_features.values
    data = {}
    beta_c = beta * [1 for i in range(len(beta))]

    comp = np.matmul(X, beta_c.transpose())
    comp *= y_scale
    data['yearly'] = np.nanmean(comp, axis=1)
    return pd.DataFrame(data)

def make_seasonality_features(dates, period, series_order, prefix):
    """Data frame with seasonality features.

    Parameters
    ----------
    cls: Prophet class.
    dates: pd.Series containing timestamps.
    period: Number of days of the period.
    series_order: Number of components.
    prefix: Column name prefix.

    Returns
    -------
    pd.DataFrame with seasonality features.
    """
    features = fourier_series(dates, period, series_order)
    columns = [
        '{}_delim_{}'.format(prefix, i + 1)
        for i in range(features.shape[1])
    ]
    return pd.DataFrame(features, columns=columns)

def fourier_series(dates, period, series_order):
    """Provides Fourier series components with the specified frequency
    and order.

    Parameters
    ----------
    dates: pd.Series containing timestamps.
    period: Number of days of the period.
    series_order: Number of components.

    Returns
    -------
    Matrix with seasonality features.
    """
    # convert to days since epoch
    t = np.array(
        (dates - datetime(1970, 1, 1))
            .dt.total_seconds()
            .astype(np.float)
    ) / (3600 * 24.)
    return np.column_stack([
        fun((2.0 * (i + 1) * np.pi * t / period))
        for i in range(series_order)
        for fun in (np.sin, np.cos)
    ])
