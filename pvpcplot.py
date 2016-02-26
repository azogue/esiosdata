# -*- coding: utf-8 -*-
"""
Created on Fri Feb  26 18:16:24 2015
DataBase de datos de consumo eléctrico
@author: Eugenio Panadero
"""
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, MonthLocator, HourLocator
import seaborn as sns
# from matplotlib.ticker import MultipleLocator


__author__ = 'Eugenio Panadero'
__copyright__ = "Copyright 2015, AzogueLabs"
__credits__ = ["Eugenio Panadero"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Eugenio Panadero"


UDS = '€/kWh'
COMPS_PLOT = ['PVPC',
              'MERCADO DIARIO E INTRADIARIO',
              'SERVICIOS DE AJUSTE',
              'PEAJE DE ACCESO',
              'PAGO POR CAPACIDAD',
              'SERVICIO DE INTERRUMPILIDAD',
              'FINANCIACIÓN OS',
              'FINANCIACIÓN OM']

COLS_DAT = ['FEU_Z0XX', 'Pmh', 'SAh', 'TEU_Z0XX', 'CAPh_Z0XX', 'INTh', 'CCOSh', 'CCOMh', 'PERD_XX']
TARIFAS_DESC = {1: 'TARIFA POR DEFECTO (PEAJE 2.0 A)',
                2: 'EFICIENCIA 2 PERIODOS (PEAJE 2.0 DHA)',
                3: 'VEHÍCULO ELÉCTRICO (PEAJE 2.0 DHS)'}
TARIFAS_COL = {1: '#dd4b39', 2: '#1aa2d8', 3: '#76b823'}
TARIFAS = list(sorted(TARIFAS_DESC.keys()))

FIGSIZE = (18, 10)


# MAKE DATA AS WEB: https://www.esios.ree.es/es/pvpc?date=22-02-2016
def _prep_pvpc_data_for_plot_web_esios(df):
    df_full = df.copy()
    for i in TARIFAS:
        df_full['TEU_Z0{}'.format(i)] = df_full['FEU_Z0{}'.format(i)] - df_full['TCUh_Z0{}'.format(i)]
        df_full['CP_{}'.format(i)] = df_full['SAh'] + df_full['Pmh'] + df_full['OCh_Z0{}'.format(i)] + df_full['INTh']
        df_full['PERD_{}'.format(i)] = df_full['TCUh_Z0{}'.format(i)] / df_full['CP_{}'.format(i)]
    return df_full.tz_localize(None).sort_index()


def pvpcplot_fill_tarifa(df, ind_tarifa=1, ax=None, show=True, ymax=None):
    if not any(['PERD' in c for c in df.columns]):
        df = _prep_pvpc_data_for_plot_web_esios(df)
    data_p = df[[c.replace('XX', str(ind_tarifa)) for c in COLS_DAT]]
    excluded_corr = ['FEU_Z0{}'.format(ind_tarifa), 'TEU_Z0{}'.format(ind_tarifa)]
    data_p = data_p.apply(lambda x: x * data_p['PERD_{}'.format(ind_tarifa)] if x.name not in excluded_corr else x)
    if ax is None:
        fig, ax = plt.subplots(figsize=(14,10))
    sns.set_style("whitegrid")
    colors = list(reversed(sns.light_palette(TARIFAS_COL[ind_tarifa], n_colors=7)))
    init = np.zeros(len(data_p.index))
    for c, label, col in zip(list(data_p.columns)[1:-1], COMPS_PLOT[1:], colors):
        ax.fill_between(data_p.index, data_p[c].values + init, init, color=col, label=label)
        init = data_p[c].values + init
    ax.plot(data_p.index, data_p['FEU_Z0{}'.format(ind_tarifa)].values, color=colors[0], label=COMPS_PLOT[0], lw=2)
    if ymax is not None:
        ax.set_ylim([0, ymax])
    ax.yaxis.label.set_text('{} [{}]'.format(TARIFAS_DESC[ind_tarifa], UDS))
    if len(df) < 30:
        ax.xaxis.set_major_formatter(DateFormatter('%H'))
        ax.xaxis.set_major_locator(HourLocator(byhour=range(0, 24, 2))) #byhour=4)) #MultipleLocator(4)), tz=TZ
    ax.grid(axis='y', color='grey', linestyle='--', linewidth=.5)
    ax.grid(axis='x', b='off')
    ax.set_axisbelow(False)
    ax.legend(fontsize='x-small', loc=3, frameon=True, framealpha=.6, ncol=2, borderaxespad=1.)
    if show:
        plt.show()


def pvpcplot_tarifas_hora(df, ax=None, show=True, ymax=None, plot_perdidas=True, fs=FIGSIZE):
    if ax is None:
        fig, ax = plt.subplots(figsize=fs)
    sns.set_style("whitegrid")
    for ind_tarifa in TARIFAS:
        ax.plot(df.index, df['FEU_Z0{}'.format(ind_tarifa)].values,
                color=TARIFAS_COL[ind_tarifa], label=TARIFAS_DESC[ind_tarifa], lw=4)
    if ymax is not None:
        ax.set_ylim([0, ymax])
    if len(df) < 30:
        ax.xaxis.set_major_formatter(DateFormatter('%H'))
        ax.xaxis.set_major_locator(HourLocator(byhour=range(24))) #byhour=4)) #MultipleLocator(4)), tz=TZ
    ax.grid(axis='x', b='off')
    ax.grid(axis='y', color='grey', linestyle='--', linewidth=.5)
    ax.set_axisbelow(False)
    ax.legend(loc=0, fontsize='large', frameon=True, framealpha=.8)
    if plot_perdidas:
        if not any(['PERD' in c for c in df.columns]):
            df = _prep_pvpc_data_for_plot_web_esios(df)
        ax_2 = ax.twinx()
        ax_2.grid('off')
        for ind_tarifa in TARIFAS:
            ax_2.plot(df.index, (df['PERD_{}'.format(ind_tarifa)] - 1).values,
                      color=TARIFAS_COL[ind_tarifa], label='% Pérdidas T{}'.format(ind_tarifa), lw=3, ls=':', alpha=.7)
        ax_2.legend(loc=4, fontsize='medium', frameon=True, framealpha=.7)
    if show:
        plt.show()


# PLOT FIGURE 1x3 + 3
def pvpcplot_grid_hora(df_day, plot_perdidas=True, fs=FIGSIZE):
    if not any(['PERD' in c for c in df_day.columns]):
        df_day = _prep_pvpc_data_for_plot_web_esios(df_day)
    ymax = np.ceil(df_day[[c for c in df_day.columns if c.startswith('FEU')]].max().max() / .02) * .02
    plt.figure(figsize=fs)
    ax1 = plt.subplot2grid((2, 3), (0, 0), colspan=3)
    axes = [plt.subplot2grid((2, 3), (1, x)) for x in [0, 1, 2]]
    pvpcplot_tarifas_hora(df_day, ax=ax1, show=False, ymax=None, plot_perdidas=plot_perdidas)
    for a, i in zip(axes, TARIFAS):
        pvpcplot_fill_tarifa(df_day, ind_tarifa=i, ax=a, show=False, ymax=ymax)
    plt.show()


# SCATTER PLOT EV. PVPC
def pvpcplot_ev_scatter(pvpc_mean_daily, pvpc_mean_monthly, ind_tarifa=1, superposic_anual=True, ax=None, plot=True):
    cols_feu_b = pvpc_mean_monthly.columns.str.contains('FEU')
    pvpc_diario = pvpc_mean_daily.loc[:, cols_feu_b].copy()
    pvpc_diario['year'] = pvpc_diario.index.year
    pvpc_mensual = pvpc_mean_monthly.loc[:, cols_feu_b].copy()
    pvpc_mensual['year'] = pvpc_mean_monthly.index.year

    if ax is None:
        fig, ax = plt.subplots(figsize=FIGSIZE)
    sns.set_style("whitegrid")

    if superposic_anual:
        base_t = pd.Timestamp(dt.datetime(year=dt.datetime.now().year, month=1, day=1), tz='Europe/Madrid')
        gr_dia = pvpc_diario.groupby('year')
        cols = sns.light_palette(TARIFAS_COL[ind_tarifa], n_colors=len(gr_dia) + 2)[2:]
        for group_d, group_m, color in zip(gr_dia, pvpc_mensual.groupby('year'), cols):
            year, df_d = group_d
            year_m, df_m = group_m
            assert(year == year_m)
            base_ti = pd.Timestamp(dt.datetime(year=year, month=1, day=1), tz='Europe/Madrid')
            delta = base_t - base_ti
            df_s = df_d.set_index(df_d.index + delta)
            df_p = df_m.set_index(df_m.index + delta + pd.Timedelta(days=14))
            ax.scatter(df_s.index, df_s['FEU_Z0{}'.format(ind_tarifa)],
                       label='FEU_{} diario ({})'.format(ind_tarifa, year), color=color)
            ax.plot(df_p.index, df_p['FEU_Z0{}'.format(ind_tarifa)],
                    label='FEU_{} mensual ({})'.format(ind_tarifa, year), color=color, lw=5, ls=':')
        ax.xaxis.set_major_formatter(DateFormatter('%b'))
        ax.xaxis.set_major_locator(MonthLocator())
        plt.xlim(base_t, pd.Timestamp(dt.datetime(year=base_t.year + 1, month=1, day=1), tz='Europe/Madrid'))
    else:
        envolv_dia = pvpc_diario.set_index(pvpc_diario.index.tz_localize(None)).resample('W', how=[np.min, np.max, np.argmax, np.argmin])
        x = envolv_dia.loc[:, 'FEU_Z0{}'.format(ind_tarifa)]['argmax'].tolist() + envolv_dia.loc[:, 'FEU_Z0{}'.format(ind_tarifa)]['argmin'].tolist()[::-1]
        y = envolv_dia.loc[:, 'FEU_Z0{}'.format(ind_tarifa)]['amax'].tolist() + envolv_dia.loc[:, 'FEU_Z0{}'.format(ind_tarifa)]['amin'].tolist()[::-1]
        ax.fill(x, y, color=TARIFAS_COL[ind_tarifa], alpha=.25)
        ax.scatter(pvpc_diario.index, pvpc_diario[['FEU_Z0{}'.format(ind_tarifa)]],
                   label='FEU_{} diario'.format(ind_tarifa), color=TARIFAS_COL[ind_tarifa])
        ax.plot(pvpc_mensual.index + pd.Timedelta(days=14), pvpc_mensual[['FEU_Z0{}'.format(ind_tarifa)]],
                label='FEU_{} mensual'.format(ind_tarifa), color=TARIFAS_COL[ind_tarifa], lw=6)
        ax.xaxis.set_major_formatter(DateFormatter("%b'%y"))
        ax.xaxis.set_major_locator(MonthLocator(interval=2))

    ax.grid(color='grey', linestyle='--', linewidth=.5)
    ax.legend(loc='best', fontsize='large', frameon=True, framealpha=.7)
    if plot:
        plt.show()


if __name__ == '__main__':
    # ADQUISICIÓN DE DATOS:
    from pvpc.classdatapvpc import PVPC

    pvpc = PVPC(update=True, force_update=False, verbose=True)
    df_pvpc = pvpc.data['data']
    pvpc_mean_daily, pvpc_mean_monthly = pvpc.get_resample_data()

    # PLOTS DIARIOS (O DE INTERVALO HORARIO):
    df_day = df_pvpc.loc['2016-02-23']
    pvpcplot_grid_hora(df_day)
    pvpcplot_grid_hora(df_pvpc.loc['2016-02-10':'2016-02-23'])

    pvpcplot_tarifas_hora(df_pvpc.loc['2016-02-10':'2016-02-23'], plot_perdidas=False)
    pvpcplot_tarifas_hora(df_pvpc.loc['2015-02-10':'2015-02-23'], plot_perdidas=True)

    # PLOTS EV. DIARIA Y MENSUAL:
    pvpcplot_ev_scatter(pvpc_mean_daily, pvpc_mean_monthly, ind_tarifa=3, superposic_anual=False)
    pvpcplot_ev_scatter(pvpc_mean_daily, pvpc_mean_monthly, ind_tarifa=1)
    pvpcplot_ev_scatter(pvpc_mean_daily, pvpc_mean_monthly, ind_tarifa=2)

    fig, ax = plt.subplots(figsize=FIGSIZE)
    for i in TARIFAS:
        pvpcplot_ev_scatter(pvpc_mean_daily, pvpc_mean_monthly, ind_tarifa=i, superposic_anual=False, ax=ax, plot=False)
    plt.show()

    # Print Resumen Data
    FEU_m = pvpc_mean_monthly[pvpc_mean_monthly.columns[pvpc_mean_monthly.columns.str.contains('FEU')]].copy()
    FEU_m['delta_12'] = FEU_m.FEU_Z01 - FEU_m.FEU_Z02
    FEU_m['delta_13'] = FEU_m.FEU_Z01 - FEU_m.FEU_Z03
    FEU_m['delta_32'] = FEU_m.FEU_Z03 - FEU_m.FEU_Z02
    print(FEU_m.describe())
