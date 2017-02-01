# -*- coding: utf-8 -*-
"""
Created on Sat Feb  27 18:16:24 2015
@author: Eugenio Panadero

A raíz del cambio previsto:

DESCONEXIÓN DE LA WEB PÚBLICA CLÁSICA DE E·SIOS
La Web pública clásica de e·sios (http://www.esios.ree.es) será desconectada el día 29 de marzo de 2016.
Continuaremos ofreciendo servicio en la nueva Web del Operador del Sistema:
    https://www.esios.ree.es.
Por favor, actualice sus favoritos apuntando a la nueva Web.

IMPORTANTE!!!
En la misma fecha (29/03/2016), también dejará de funcionar el servicio Solicitar y Descargar,
utilizado para descargar información de la Web pública clásica de e·sios.
Por favor, infórmese sobre descarga de información en
    https://www.esios.ree.es/es/pagina/api
y actualice sus procesos de descarga.
"""
import datetime as dt
import numpy as np
import pandas as pd
from dataweb.requestweb import get_data_en_intervalo
from esiosdata.esios_config import DATE_FMT, TZ, SERVER, HEADERS, TARIFAS, COLS_PVPC


__author__ = 'Eugenio Panadero'
__copyright__ = "Copyright 2015, AzogueLabs"
__credits__ = ["Eugenio Panadero"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Eugenio Panadero"


def pvpc_url_dia(dt_day):
    """Obtiene la url de descarga de los datos de PVPC de un día concreto.

    Anteriormente era: 'http://www.esios.ree.es/Solicitar?fileName=pvpcdesglosehorario_' + str_dia
    + '&fileType=xml&idioma=es', pero ahora es en JSON y requiere token_auth en headers.
    """
    if type(dt_day) is str:
        return SERVER + '/archives/70/download_json?locale=es' + '&date=' + dt_day
    else:
        return SERVER + '/archives/70/download_json?locale=es' + '&date=' + dt_day.date().isoformat()


def pvpc_calc_tcu_cp_feu_d(df, verbose=True, convert_kwh=True):
    """Procesa TCU, CP, FEU diario.

    :param df:
    :param verbose:
    :param convert_kwh:
    :return:
    """
    if 'TCU' + TARIFAS[0] not in df.columns:
        # Pasa de €/MWh a €/kWh:
        if convert_kwh:
            cols_mwh = [c + t for c in COLS_PVPC for t in TARIFAS if c != 'COF']
            df[cols_mwh] = df[cols_mwh].applymap(lambda x: x / 1000.)
        # Obtiene columnas TCU, CP, precio día
        gb_t = df.groupby(lambda x: TARIFAS[np.argmax([t in x for t in TARIFAS])], axis=1)
        for k, g in gb_t:
            if verbose:
                print('TARIFA {}'.format(k))
                print(g.head())

            # Cálculo de TCU
            df['TCU{}'.format(k)] = g[k] - g['TEU{}'.format(k)]

            # Cálculo de CP
            # cols_cp = [c + k for c in ['FOS', 'FOM', 'INT', 'PCAP', 'PMH', 'SAH']]
            cols_cp = [c + k for c in COLS_PVPC if c not in ['', 'COF', 'TEU']]
            df['CP{}'.format(k)] = g[cols_cp].sum(axis=1)

            # Cálculo de PERD --> No es posible así, ya que los valores base ya vienen con PERD
            # dfs_pvpc[k]['PERD{}'.format(k)] = dfs_pvpc[k]['TCU{}'.format(k)] / dfs_pvpc[k]['CP{}'.format(k)]
            # dfs_pvpc[k]['PERD{}'.format(k)] = dfs_pvpc[k]['INT{}'.format(k)] / 1.92

            # Cálculo de FEU diario
            cols_k = ['TEU' + k, 'TCU' + k, 'COF' + k]
            g = df[cols_k].groupby('TEU' + k)
            pr = g.apply(lambda x: x['TCU' + k].dot(x['COF' + k]) / x['COF' + k].sum())
            pr.name = 'PD_' + k
            df = df.join(pr, on='TEU' + k, rsuffix='_r')
            df['PD_' + k] += df['TEU' + k]
    return df


def _process_json_pvpc_hourly_data(df):
    # Forma DateTimeIndex:
    params_dt = dict(freq='H', tz=TZ)
    if len(df) == 25 or len(df) == 23:  # Día con cambio de hora (DST)
        fecha = dt.datetime.strptime(df['Dia'][0], '%d/%m/%Y')
        df['fecha'] = pd.DatetimeIndex(start=fecha, end=fecha + dt.timedelta(days=1, hours=-1), **params_dt)
        print('Fichero irregular nº horas != 24: --> {:%d-%m-%Y} -> {} medidas'.format(fecha, len(df['fecha'])))
    else:
        df['fecha'] = pd.DatetimeIndex([dt.datetime.strptime(x, '%d/%m/%Y %H')
                                        for x in df['Dia'].str.cat(df['Hora'].str.slice(0, 2), sep=' ')], **params_dt)
    df = df.drop(['Dia', 'Hora'], axis=1).set_index('fecha', verify_integrity=True).sort_index()
    # Pasa a float:
    df = df.applymap(lambda x: float(x.replace('.', '').replace(',', '.')))  # / 1000.)
    return df


def pvpc_procesa_datos_dia(_, response, verbose=True):
    """Procesa la información JSON descargada y forma el dataframe de los datos de un día."""
    try:
        d_data = response['PVPC']
        df = _process_json_pvpc_hourly_data(pd.DataFrame(d_data))
        return df, 0
    except Exception as e:
        if verbose:
            print('ERROR leyendo información de web: {}'.format(e))
        return None, -2


def pvpc_data_dia(str_dia, str_dia_fin=None):
    """Obtiene datos de PVPC en un día concreto o un intervalo, accediendo directamente a la web."""
    params = {'date_fmt': DATE_FMT, 'usar_multithread': False,
              'func_procesa_data_dia': pvpc_procesa_datos_dia, 'func_url_data_dia': pvpc_url_dia,
              'data_extra_request': {'json_req': True, 'headers': HEADERS}}
    if str_dia_fin is not None:
        params['usar_multithread'] = True
        data, hay_errores, str_import = get_data_en_intervalo(str_dia, str_dia_fin, **params)
    else:
        data, hay_errores, str_import = get_data_en_intervalo(str_dia, str_dia, **params)
    if not hay_errores:
        return data
    else:
        return str_import
