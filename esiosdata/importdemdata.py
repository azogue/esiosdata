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
__author__ = 'Eugenio Panadero'
__copyright__ = "Copyright 2015, AzogueLabs"
__credits__ = ["Eugenio Panadero"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Eugenio Panadero"

import json
import pandas as pd
import re
from dataweb.requestweb import get_data_en_intervalo
from esiosdata.esios_config import DATE_FMT, TZ, SERVER, HEADERS, D_TIPOS_REQ_DEM, KEYS_DATA_DEM
from prettyprinting import print_redb, print_err


RG_FUNC_CONTENT = re.compile('(?P<func>.*)\((?P<json>.*)\);')


def dem_url_dia(dt_day='2015-06-22'):
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
        try:
            if len(data.keys()) == 1:
                return ind, data[list(data.keys())[0]]
        except Exception as e:
            print_err('ERROR JSON??: {} ({}) --> RAW: {} - {}'.format(e, e.__class__, ind, data_raw))
    except AttributeError as e:
        # print('ERROR REG_EXP --> RAW: {}'.format(data_raw))
        return None, None
    return ind, data


def _import_daily_max_min(data):
    # IND_MaxMinRenovEol / IND_MaxMin
    df = pd.DataFrame(data, index=[0])
    cols_ts = df.columns.str.startswith('ts')
    is_max_min_renov = any(cols_ts)
    if is_max_min_renov:
        df.index = pd.DatetimeIndex([pd.Timestamp(df['tsMaxRenov'][0]).date()], freq='D')
    else:
        try:
            df = df.set_index(pd.DatetimeIndex([pd.Timestamp(df['date'][0]).date()], freq='D')).drop('date', axis=1)
        except KeyError:
            df = df.set_index(pd.DatetimeIndex([pd.Timestamp(df['timeStampMax'][0]).date()], freq='D'))
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
        return  df.set_index(pd.DatetimeIndex(df['ts'].apply(lambda x: pd.Timestamp(x, tz=TZ)), freq='10T', tz=TZ),
                             verify_integrity=True).drop('ts', axis=1).sort_index().applymap(float)
    except ValueError:  # ES DST
        df['ts'] = pd.DatetimeIndex(start=pd.Timestamp(df['ts'].iloc[0]), periods=len(df), freq='10T', tz=TZ)
        # , ambiguous="infer")
        return df.set_index('ts', verify_integrity=True).sort_index().applymap(float)


def dem_procesa_datos_dia(key_day, response):
    try:
        dfs_import, dfs_maxmin, hay_errores = [], [], 0
        for r in response:
            tipo_datos, data = _extract_func_json_data(r)
            if tipo_datos is not None:
                if 'IND_MaxMin' in tipo_datos:
                    df_import = _import_daily_max_min(data)
                    dfs_maxmin.append(df_import)
                else:
                    df_import = _import_json_ts_data(data)
                    dfs_import.append(df_import)
            if tipo_datos is None or df_import is None:
                hay_errores += 1
                    # break
        if hay_errores == 4:
            # No hay nada, salida temprana sin retry:
            print_redb('** No hay datos para el día {}!'.format(key_day))
            return None, -2
        else:  # if hay_errores < 3:
            # TODO formar datos incompletos!! (max-min con NaN's, etc.)
            # df = dfs_import[0].join(dfs_import[1])
            data_import = {KEYS_DATA_DEM[0]: dfs_import[0].join(dfs_import[1]),
                           KEYS_DATA_DEM[1]: dfs_maxmin[0].join(dfs_maxmin[1])}
            return data_import, 0
        # else:
        #     print('NUM ERRORES EN "{}": {}'.format(key_day, hay_errores))
    except Exception as e:
        print_redb('ERROR scrapping: "{}" ({}) - {}:\n-->{}\n{}\n{}\n{}'.format(e, e.__class__, key_day, *response))
    return None, -1


def dem_data_dia(str_dia='2015-10-10', str_dia_fin=None):
    params = {'date_fmt': DATE_FMT, 'usar_multithread': False, 'num_retries': 1,
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


# TESTING:
if __name__ == '__main__':
    from prettyprinting import print_yellow, print_info, print_green
    # out = dem_data_dia('2015-12-07', '2015-12-11')
    # print(out['data_dias'])

    print_yellow(dem_data_dia('2015-10-15'))
    print_info(dem_data_dia('2015-10-22', '2015-10-27'))
    print_green(dem_data_dia('2015-03-01', '2015-04-25'))

    # res = dem_data_dia('2016-03-08')
    # print_info(res['data'])
    # print_yellow(res['data_dias'])
    # print(dem_data_dia('2015-03-01'))

    # print(out['data'])
    # print(out['data'].index)
    # print(out['data_dias'].index)