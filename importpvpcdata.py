# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 18:16:24 2015
DataBase de datos de consumo eléctrico
@author: Eugenio Panadero
"""
__author__ = 'Eugenio Panadero'
__copyright__ = "Copyright 2015, AzogueLabs"
__credits__ = ["Eugenio Panadero"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Eugenio Panadero"

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from dataweb.requestweb.requestweb import get_data_en_intervalo
from pvpc.pvpcdata_config import DATE_FMT, TZ, FREQ_DATA


def pvpc_url_dia(str_dia='20150622'):  # url = 'http://www.esios.ree.es/pvpc/'
    return 'http://www.esios.ree.es/Solicitar?fileName=pvpcdesglosehorario_' + str_dia + '&fileType=xml&idioma=es'


# noinspection PyUnusedLocal
def pvpc_procesa_datos_dia(__, response):
    # Extrae pandas dataframe con valores horarios e info extra del XML PVPC
    try:  # <sinDatos/>
        if len(response) > 0:
            soup_pvpc = BeautifulSoup(response, "html5lib")
            str_horizonte = soup_pvpc.find_all('horizonte')[0]['v']
            ts = pd.Timestamp(pd.Timestamp(str_horizonte.split('/')[1]).date(), tz=TZ)
            identseriesall = soup_pvpc.find_all('terminocostehorario')
            data_horas, num_horas = {}, 24
            for serie in identseriesall:
                idunico = serie['v']
                if len(serie.find_all('tipoprecio')) > 0:
                    idunico += '_' + serie.tipoprecio['v']
                values = [float(v['v']) for v in serie.find_all('ctd')]
                num_horas = len(values)
                assert(num_horas > 10)
                data_horas[idunico] = np.array(values)
            dfdata = pd.DataFrame(data_horas, index=pd.DatetimeIndex(start=ts, periods=num_horas, freq=FREQ_DATA))
            return dfdata, 0
        else:
            # print('ERROR No se encuentra información de web:')
            return None, -1
    except Exception as e:
        print('ERROR leyendo información de web:')
        print(e)
        return None, -2


def pvpc_data_dia(str_dia='20150622', str_dia_fin=None):
    params = {'date_fmt': DATE_FMT, 'usar_multithread': False,
              'func_procesa_data_dia': pvpc_procesa_datos_dia, 'func_url_data_dia': pvpc_url_dia}
    if str_dia_fin is not None:
        params['usar_multithread'] = True
        data, hay_errores, str_import = get_data_en_intervalo(str_dia, str_dia_fin, **params)
    else:
        data, hay_errores, str_import = get_data_en_intervalo(str_dia, str_dia, **params)
    if not hay_errores:
        return data
    else:
        return str_import
