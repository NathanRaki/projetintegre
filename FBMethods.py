import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import (AutoDateLocator, AutoDateFormatter, MonthLocator, num2date)
from matplotlib.ticker import FuncFormatter

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


# In[73]:


def plot_components(
    m, fcst, uncertainty=True, plot_cap=True, weekly_start=0, yearly_start=0,
    figsize=None
):
    """Plot the Prophet forecast components.

    Will plot whichever are available of: trend, holidays, weekly
    seasonality, yearly seasonality, and additive and multiplicative extra
    regressors.

    Parameters
    ----------
    m: Prophet model.
    fcst: pd.DataFrame output of m.predict.
    uncertainty: Optional boolean to plot uncertainty intervals, which will
        only be done if m.uncertainty_samples > 0.
    plot_cap: Optional boolean indicating if the capacity should be shown
        in the figure, if available.
    weekly_start: Optional int specifying the start day of the weekly
        seasonality plot. 0 (default) starts the week on Sunday. 1 shifts
        by 1 day to Monday, and so on.
    yearly_start: Optional int specifying the start day of the yearly
        seasonality plot. 0 (default) starts the year on Jan 1. 1 shifts
        by 1 day to Jan 2, and so on.
    figsize: Optional tuple width, height in inches.

    Returns
    -------
    A matplotlib figure.
    """
    # Identify components to be plotted
    components = ['trend']
    if m.train_holiday_names is not None and 'holidays' in fcst:
        components.append('holidays')
    # Plot weekly seasonality, if present
    if 'weekly' in m.seasonalities and 'weekly' in fcst:
        components.append('weekly')
    # Yearly if present
    if 'yearly' in m.seasonalities and 'yearly' in fcst:
        components.append('yearly')
    # Other seasonalities
    components.extend([
        name for name in sorted(m.seasonalities)
        if name in fcst and name not in ['weekly', 'yearly']
    ])
    regressors = {'additive': False, 'multiplicative': False}
    for name, props in m.extra_regressors.items():
        regressors[props['mode']] = True
    for mode in ['additive', 'multiplicative']:
        if regressors[mode] and 'extra_regressors_{}'.format(mode) in fcst:
            components.append('extra_regressors_{}'.format(mode))
    npanel = len(components)

    figsize = figsize if figsize else (9, 3 * npanel)
    fig, axes = plt.subplots(npanel, 1, facecolor='w', figsize=figsize)

    if npanel == 1:
        axes = [axes]

    multiplicative_axes = []

    dt = m.history['ds'].diff()
    min_dt = dt.iloc[dt.values.nonzero()[0]].min() 

    for ax, plot_name in zip(axes, components):
        if plot_name == 'trend':
            plot_forecast_component(
                m=m, fcst=fcst, name='trend', ax=ax, uncertainty=uncertainty,
                plot_cap=plot_cap,
            )
        elif plot_name in m.seasonalities:
            if (
                (plot_name == 'weekly' or m.seasonalities[plot_name]['period'] == 7)
                and (min_dt == pd.Timedelta(days=1))
            ):
                plot_weekly(
                    m=m, name=plot_name, ax=ax, uncertainty=uncertainty, weekly_start=weekly_start
                )
            elif plot_name == 'yearly' or m.seasonalities[plot_name]['period'] == 365.25:
                plot_yearly(
                    m=m, name=plot_name, ax=ax, uncertainty=uncertainty, yearly_start=yearly_start
                )
            else:
                plot_seasonality(
                    m=m, name=plot_name, ax=ax, uncertainty=uncertainty,
                )
        elif plot_name in [
            'holidays',
            'extra_regressors_additive',
            'extra_regressors_multiplicative',
        ]:
            plot_forecast_component(
                m=m, fcst=fcst, name=plot_name, ax=ax, uncertainty=uncertainty,
                plot_cap=False,
            )
        if plot_name in m.component_modes['multiplicative']:
            multiplicative_axes.append(ax)

    fig.tight_layout()
    # Reset multiplicative axes labels after tight_layout adjustment
    for ax in multiplicative_axes:
        ax = set_y_as_percent(ax)
    return fig

def plot_forecast_component(
    m, fcst, name, ax=None, uncertainty=True, plot_cap=False, figsize=(10, 6)
):
    """Plot a particular component of the forecast.

    Parameters
    ----------
    m: Prophet model.
    fcst: pd.DataFrame output of m.predict.
    name: Name of the component to plot.
    ax: Optional matplotlib Axes to plot on.
    uncertainty: Optional boolean to plot uncertainty intervals, which will
        only be done if m.uncertainty_samples > 0.
    plot_cap: Optional boolean indicating if the capacity should be shown
        in the figure, if available.
    figsize: Optional tuple width, height in inches.

    Returns
    -------
    a list of matplotlib artists
    """
    artists = []
    if not ax:
        fig = plt.figure(facecolor='w', figsize=figsize)
        ax = fig.add_subplot(111)
    fcst_t = fcst['ds'].dt.to_pydatetime()
    artists += ax.plot(fcst_t, fcst[name], ls='-', c='#0072B2')
    if 'cap' in fcst and plot_cap:
        artists += ax.plot(fcst_t, fcst['cap'], ls='--', c='k')
    if m.logistic_floor and 'floor' in fcst and plot_cap:
        ax.plot(fcst_t, fcst['floor'], ls='--', c='k')
    if uncertainty and m.uncertainty_samples:
        artists += [ax.fill_between(
            fcst_t, fcst[name + '_lower'], fcst[name + '_upper'],
            color='#0072B2', alpha=0.2)]
    # Specify formatting to workaround matplotlib issue #12925
    locator = AutoDateLocator(interval_multiples=False)
    formatter = AutoDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.grid(True, which='major', c='gray', ls='-', lw=1, alpha=0.2)
    ax.set_xlabel('ds')
    ax.set_ylabel(name)
    if name in m.component_modes['multiplicative']:
        ax = set_y_as_percent(ax)
    return artists
def seasonality_plot_df(m, ds):
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
    for name in m.extra_regressors:
        df_dict[name] = 0.
    # Activate all conditional seasonality columns
    for props in m.seasonalities.values():
        if props['condition_name'] is not None:
            df_dict[props['condition_name']] = True
    df = pd.DataFrame(df_dict)
    df = m.setup_dataframe(df)
    return df


def plot_weekly(m, ax=None, uncertainty=True, weekly_start=0, figsize=(10, 6), name='weekly'):
    """Plot the weekly component of the forecast.

    Parameters
    ----------
    m: Prophet model.
    ax: Optional matplotlib Axes to plot on. One will be created if this
        is not provided.
    uncertainty: Optional boolean to plot uncertainty intervals, which will
        only be done if m.uncertainty_samples > 0.
    weekly_start: Optional int specifying the start day of the weekly
        seasonality plot. 0 (default) starts the week on Sunday. 1 shifts
        by 1 day to Monday, and so on.
    figsize: Optional tuple width, height in inches.
    name: Name of seasonality component if changed from default 'weekly'.

    Returns
    -------
    a list of matplotlib artists
    """
    artists = []
    if not ax:
        fig = plt.figure(facecolor='w', figsize=figsize)
        ax = fig.add_subplot(111)
    # Compute weekly seasonality for a Sun-Sat sequence of dates.
    days = (pd.date_range(start='2017-01-01', periods=7) +
            pd.Timedelta(days=weekly_start))
    df_w = seasonality_plot_df(m, days)
    seas = m.predict_seasonal_components(df_w)
    days = days.day_name()
    artists += ax.plot(range(len(days)), seas[name], ls='-',
                    c='#0072B2')
    if uncertainty and m.uncertainty_samples:
        artists += [ax.fill_between(range(len(days)),
                                    seas[name + '_lower'], seas[name + '_upper'],
                                    color='#0072B2', alpha=0.2)]
    ax.grid(True, which='major', c='gray', ls='-', lw=1, alpha=0.2)
    ax.set_xticks(range(len(days)))
    ax.set_xticklabels(days)
    ax.set_xlabel('Day of week')
    ax.set_ylabel(name)
    if m.seasonalities[name]['mode'] == 'multiplicative':
        ax = set_y_as_percent(ax)
    return artists


def plot_yearly(m, ax=None, uncertainty=True, yearly_start=0, figsize=(10, 6), name='yearly'):
    """Plot the yearly component of the forecast.

    Parameters
    ----------
    m: Prophet model.
    ax: Optional matplotlib Axes to plot on. One will be created if
        this is not provided.
    uncertainty: Optional boolean to plot uncertainty intervals, which will
        only be done if m.uncertainty_samples > 0.
    yearly_start: Optional int specifying the start day of the yearly
        seasonality plot. 0 (default) starts the year on Jan 1. 1 shifts
        by 1 day to Jan 2, and so on.
    figsize: Optional tuple width, height in inches.
    name: Name of seasonality component if previously changed from default 'yearly'.

    Returns
    -------
    a list of matplotlib artists
    """
    artists = []
    if not ax:
        fig = plt.figure(facecolor='w', figsize=figsize)
        ax = fig.add_subplot(111)
    # Compute yearly seasonality for a Jan 1 - Dec 31 sequence of dates.
    days = (pd.date_range(start='2017-01-01', periods=365) +
            pd.Timedelta(days=yearly_start))
    df_y = seasonality_plot_df(m, days)
    seas = m.predict_seasonal_components(df_y)
    artists += ax.plot(
        df_y['ds'].dt.to_pydatetime(), seas[name], ls='-', c='#0072B2')
    if uncertainty and m.uncertainty_samples:
        artists += [ax.fill_between(
            df_y['ds'].dt.to_pydatetime(), seas[name + '_lower'],
            seas[name + '_upper'], color='#0072B2', alpha=0.2)]
    ax.grid(True, which='major', c='gray', ls='-', lw=1, alpha=0.2)
    months = MonthLocator(range(1, 13), bymonthday=1, interval=2)
    ax.xaxis.set_major_formatter(FuncFormatter(
        lambda x, pos=None: '{dt:%B} {dt.day}'.format(dt=num2date(x))))
    ax.xaxis.set_major_locator(months)
    ax.set_xlabel('Day of year')
    ax.set_ylabel(name)
    if m.seasonalities[name]['mode'] == 'multiplicative':
        ax = set_y_as_percent(ax)
    return artists


def plot_seasonality(m, name, ax=None, uncertainty=True, figsize=(10, 6)):
    """Plot a custom seasonal component.

    Parameters
    ----------
    m: Prophet model.
    name: Seasonality name, like 'daily', 'weekly'.
    ax: Optional matplotlib Axes to plot on. One will be created if
        this is not provided.
    uncertainty: Optional boolean to plot uncertainty intervals, which will
        only be done if m.uncertainty_samples > 0.
    figsize: Optional tuple width, height in inches.

    Returns
    -------
    a list of matplotlib artists
    """
    artists = []
    if not ax:
        fig = plt.figure(facecolor='w', figsize=figsize)
        ax = fig.add_subplot(111)
    # Compute seasonality from Jan 1 through a single period.
    start = pd.to_datetime('2017-01-01 0000')
    period = m.seasonalities[name]['period']
    end = start + pd.Timedelta(days=period)
    plot_points = 200
    days = pd.to_datetime(np.linspace(start.value, end.value, plot_points))
    df_y = seasonality_plot_df(m, days)
    seas = m.predict_seasonal_components(df_y)
    artists += ax.plot(df_y['ds'].dt.to_pydatetime(), seas[name], ls='-',
                        c='#0072B2')
    if uncertainty and m.uncertainty_samples:
        artists += [ax.fill_between(
            df_y['ds'].dt.to_pydatetime(), seas[name + '_lower'],
            seas[name + '_upper'], color='#0072B2', alpha=0.2)]
    ax.grid(True, which='major', c='gray', ls='-', lw=1, alpha=0.2)
    n_ticks = 8
    xticks = pd.to_datetime(np.linspace(start.value, end.value, n_ticks)
        ).to_pydatetime()
    ax.set_xticks(xticks)
    if period <= 2:
        fmt_str = '{dt:%T}'
    elif name == 'weekly':
        fmt_str = '{dt:%A}'
    elif period < 14:
        fmt_str = '{dt:%m}/{dt:%d} {dt:%R}'
    else:
        fmt_str = '{dt:%m}/{dt:%d}'
    ax.xaxis.set_major_formatter(FuncFormatter(
        lambda x, pos=None: fmt_str.format(dt=num2date(x))))
    ax.set_xlabel('ds')
    ax.set_ylabel(name)
    if m.seasonalities[name]['mode'] == 'multiplicative':
        ax = set_y_as_percent(ax)
    return artists

def set_y_as_percent(ax):
    yticks = 100 * ax.get_yticks()
    yticklabels = ['{0:.4g}%'.format(y) for y in yticks]
    ax.set_yticklabels(yticklabels)
    return ax