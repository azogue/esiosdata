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
import json
import pandas as pd
import re
from dataweb.requestweb import get_data_en_intervalo
from esiosdata.esios_config import DATE_FMT, TZ, SERVER, HEADERS, D_TIPOS_REQ_DEM, KEYS_DATA_DEM
from esiosdata.prettyprinting import print_redb, print_err


__author__ = 'Eugenio Panadero'
__copyright__ = "Copyright 2015, AzogueLabs"
__credits__ = ["Eugenio Panadero"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Eugenio Panadero"

RG_FUNC_CONTENT = re.compile('(?P<func>.*)\((?P<json>.*)\);')


def dem_url_dia(dt_day='2015-06-22'):
    """Obtiene las urls de descarga de los datos de demanda energética de un día concreto."""

    def _url_tipo_dato(str_dia, k):
        url = SERVER + '/archives/{}/download_json?locale=es'.format(D_TIPOS_REQ_DEM[k])
        if type(str_dia) is str:
            return url + '&date=' + str_dia
        else:
            return url + '&date=' + str_dia.date().isoformat()

    urls = [_url_tipo_dato(dt_day, k) for k in D_TIPOS_REQ_DEM.keys()]
    return urls


def _extract_func_json_data(data_raw):
    try:
        busca = RG_FUNC_CONTENT.match(data_raw).groupdict()
        ind, data = busca['func'], None
        data = json.loads(busca['json'])
        if len(data.keys()) == 1:
            return ind, data[list(data.keys())[0]]
        else:
            return ind, data
    except AttributeError:
        # print('ERROR REG_EXP [{}] --> RAW: {}'.format(e, data_raw))
        return None, None


def _import_daily_max_min(data):
    # IND_MaxMinRenovEol / IND_MaxMin
    df = pd.DataFrame(data, index=[0])
    cols_ts = df.columns.str.startswith('ts')
    is_max_min_renov = any(cols_ts)
    if is_max_min_renov:
        df.index = pd.DatetimeIndex([pd.Timestamp(df['tsMaxRenov'][0]).date()], freq='D')
    else:
        df = pd.DataFrame(df.set_index(pd.DatetimeIndex([pd.Timestamp(df['date'][0]).date()], freq='D')
                                       ).drop('date', axis=1))
        cols_ts = df.columns.str.contains('timeStamp', regex=False)
    for c, is_ts in zip(df.columns, cols_ts):
        if is_ts:
            df[c] = df[c].apply(pd.Timestamp)
        else:
            df[c] = df[c].astype(float)
    return df


def _import_json_ts_data(data):
    df = pd.DataFrame(data)
    try:
        return pd.DataFrame(df.set_index(pd.DatetimeIndex(df['ts'].apply(lambda x: pd.Timestamp(x, tz=TZ)),
                                                          freq='10T', tz=TZ), verify_integrity=True
                                         ).drop('ts', axis=1)).sort_index().applymap(float)
    except ValueError:  # ES DST
        df['ts'] = pd.DatetimeIndex(start=pd.Timestamp(df['ts'].iloc[0]), periods=len(df), freq='10T', tz=TZ)
        # , ambiguous="infer")
        return df.set_index('ts', verify_integrity=True).sort_index().applymap(float)


def dem_procesa_datos_dia(key_day, response):
    """Procesa los datos descargados en JSON."""
    dfs_import, df_import, dfs_maxmin, hay_errores = [], None, [], 0
    for r in response:
        tipo_datos, data = _extract_func_json_data(r)
        if tipo_datos is not None:
            if ('IND_MaxMin' in tipo_datos) and data:
                df_import = _import_daily_max_min(data)
                dfs_maxmin.append(df_import)
            elif data:
                df_import = _import_json_ts_data(data)
                dfs_import.append(df_import)
        if tipo_datos is None or df_import is None:
            hay_errores += 1
    if hay_errores == 4:
        # No hay nada, salida temprana sin retry:
        print_redb('** No hay datos para el día {}!'.format(key_day))
        return None, -2
    else:  # if hay_errores < 3:
        # TODO formar datos incompletos!! (max-min con NaN's, etc.)
        data_import = {}
        if dfs_import:
            data_import[KEYS_DATA_DEM[0]] = dfs_import[0].join(dfs_import[1])
        if len(dfs_maxmin) == 2:
            data_import[KEYS_DATA_DEM[1]] = dfs_maxmin[0].join(dfs_maxmin[1])
        elif dfs_maxmin:
            data_import[KEYS_DATA_DEM[1]] = dfs_maxmin[0]
        if not data_import:
            print_err('DÍA: {} -> # ERRORES: {}'.format(key_day, hay_errores))
            return None, -2
        return data_import, 0


def dem_data_dia(str_dia='2015-10-10', str_dia_fin=None):
    """Obtiene datos de demanda energética en un día concreto o un intervalo, accediendo directamente a la web."""
    params = {'date_fmt': DATE_FMT, 'usar_multithread': False, 'num_retries': 1, "timeout": 10,
              'func_procesa_data_dia': dem_procesa_datos_dia, 'func_url_data_dia': dem_url_dia,
              'data_extra_request': {'json_req': False, 'headers': HEADERS}}
    if str_dia_fin is not None:
        params['usar_multithread'] = True
        data, hay_errores, str_import = get_data_en_intervalo(str_dia, str_dia_fin, **params)
    else:
        data, hay_errores, str_import = get_data_en_intervalo(str_dia, str_dia, **params)
    if not hay_errores:
        return data
    else:
        print_err(str_import)
        return None
