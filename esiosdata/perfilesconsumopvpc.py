# -*- coding: utf-8 -*-
"""
# Perfiles de consumo del PVPC para clientes sin registro horario

## Descarga de CSV's mensuales con los perfiles finales de consumo

En la web de REE están **disponibles para descarga los perfiles finales de consumo**, mediante ficheros CSV comprimidos
para cada mes, publicados antes de que transcurran cinco días desde el final del mes de consumo al que se refieren.
Las correcciones de los datos de demanda, que puedan producirse con posterioridad a la publicación de los perfiles
de consumo, serán tenidas en cuenta únicamente a los efectos informativos que correspondan, sin afectar en ningún caso
al cálculo de estos perfiles.
link: http://www.ree.es/es/actividades/operacion-del-sistema-electrico/medidas-electricas

**Archivos CSV**: 'http://www.ree.es/sites/default/files/simel/perff/PERFF_{año}{mes}.gz'

Para el año **2017**, se suministran los coeficientes y demanda de referencia para calcular los perfiles iniciales.
PDF con la última resolución con la demanda de referencia: **[Resolución de 28 de diciembre de 2016 de la Dirección
General de Política Energética y Minas (PDF, 2,37 MB)]
(http://www.ree.es/sites/default/files/01_ACTIVIDADES/Documentos/Documentacion-Simel/resolucion_28122016.pdf)**

## Fichero excel con coeficientes para los perfiles iniciales para 2017:

Establecidos en la resolución anteriormente indicada, disponibles en formato Excel para su consulta en
[Demanda de referencia y perfiles iniciales para el año 2017 (XLSX, 705 KB)]
(http://www.ree.es/sites/default/files/01_ACTIVIDADES/Documentos/Documentacion-Simel/perfiles_iniciales_2017.xlsx)

@author: Eugenio Panadero
"""
import datetime as dt
import os
import pandas as pd
from urllib.error import HTTPError
from esiosdata.esios_config import TZ, STORAGE_DIR


URL_PERFILES_2017 = 'http://www.ree.es/sites/default/files/01_ACTIVIDADES/' \
                    'Documentos/Documentacion-Simel/perfiles_iniciales_2017.xlsx'
DATA_PERFILES_2017 = None


##############################################
#       OBTENCIÓN DE PERFILES                #
##############################################
def get_data_coeficientes_perfilado_2017(force_download=False):
    """Extrae la información de las dos hojas del Excel proporcionado por REE
    con los perfiles iniciales para 2017.
    :param force_download: Descarga el fichero 'raw' del servidor, en vez de acudir a la copia local.
    :return: perfiles_2017, coefs_alpha_beta_gamma
    :rtype: tuple
    """
    path_perfs = os.path.join(STORAGE_DIR, 'perfiles_consumo_2017.h5')

    if force_download or not os.path.exists(path_perfs):
        # Coeficientes de perfilado y demanda de referencia (1ª hoja)
        cols_sheet1 = ['Mes', 'Día', 'Hora',
                       'Pa,0m,d,h', 'Pb,0m,d,h', 'Pc,0m,d,h', 'Pd,0m,d,h', 'Demanda de Referencia 2017 (MW)']
        perfs_2017 = pd.read_excel(URL_PERFILES_2017, header=None, skiprows=[0, 1], names=cols_sheet1)
        perfs_2017['ts'] = pd.DatetimeIndex(start='2017-01-01', freq='H', tz=TZ, end='2017-12-31 23:59')
        perfs_2017 = perfs_2017.set_index('ts').drop(['Mes', 'Día', 'Hora'], axis=1)

        # Coefs Alfa, Beta, Gamma (2ª hoja):
        coefs_alpha_beta_gamma = pd.read_excel(URL_PERFILES_2017, sheetname=1)
        print('Escribiendo perfiles 2017 en disco, en {}'.format(path_perfs))
        with pd.HDFStore(path_perfs, 'w') as st:
            st.put('coefs', coefs_alpha_beta_gamma)
            st.put('perfiles', perfs_2017)
        print('HDFStore de tamaño {:.3f} KB'.format(os.path.getsize(path_perfs) / 1000))
    else:
        with pd.HDFStore(path_perfs, 'r') as st:
            coefs_alpha_beta_gamma = st['coefs']
            perfs_2017 = st['perfiles']
    return perfs_2017, coefs_alpha_beta_gamma


def get_data_perfiles_estimados_2017(force_download=False):
    """Extrae perfiles estimados para 2017 con el formato de los CSV's mensuales con los perfiles definitivos.
    :param force_download: bool para forzar la descarga del excel de la web de REE.
    :return: perfiles_2017
    :rtype: pd.Dataframe
    """
    global DATA_PERFILES_2017
    if (DATA_PERFILES_2017 is None) or force_download:
        perf_demref_2017, _ = get_data_coeficientes_perfilado_2017(force_download=force_download)
        # Conversión de formato de dataframe de perfiles 2017 a finales (para uniformizar):
        cols_usar = ['Pa,0m,d,h', 'Pb,0m,d,h', 'Pc,0m,d,h', 'Pd,0m,d,h']
        perfs_2017 = perf_demref_2017[cols_usar].copy()
        perfs_2017.columns = ['COEF. PERFIL {}'.format(p) for p in 'ABCD']
        DATA_PERFILES_2017 = perfs_2017
        return perfs_2017
    return DATA_PERFILES_2017


def get_data_perfiles_finales_mes(año, mes=None):
    """Lee el fichero CSV comprimido con los perfiles finales de consumo eléctrico para
    el mes dado desde la web de REE. Desecha columnas de fecha e información de DST.
    :param año: :int: año ó :datetime_obj: ts
    :param mes: :int: mes (OPC)
    :return: perfiles_mes
    :rtype: pd.Dataframe
    """
    mask_ts = 'http://www.ree.es/sites/default/files/simel/perff/PERFF_{:%Y%m}.gz'
    if (type(año) is int) and (mes is not None):
        ts = dt.datetime(año, mes, 1, 0, 0)
    else:
        ts = año
    url_perfiles_finales = mask_ts.format(ts)
    cols_drop = ['MES', 'DIA', 'HORA', 'AÑO', 'VERANO(1)/INVIERNO(0)']
    # print_info('Descargando perfiles finales del mes de {:%b de %Y} en {}'.format(ts, url_perfiles_finales))
    # Intenta descargar perfiles finales, y si falla, recurre a los estimados para 2017:
    try:
        perfiles_finales = pd.read_csv(url_perfiles_finales, sep=';', encoding='latin_1', compression='gzip'
                                       ).dropna(how='all', axis=1)
        perfiles_finales['ts'] = pd.DatetimeIndex(start='{:%Y-%m}-01'.format(ts), freq='H', tz=TZ,
                                                  end='{:%Y-%m-%d} 23:59'.format((ts + dt.timedelta(days=31)
                                                                                  ).replace(day=1)
                                                                                 - dt.timedelta(days=1)))
        return perfiles_finales.set_index('ts').drop(cols_drop, axis=1)
    except HTTPError as e:
        print('HTTPError: {}. Se utilizan perfiles estimados de 2017.'.format(e))
        perfiles_2017 = get_data_perfiles_estimados_2017()
        return perfiles_2017[(perfiles_2017.index.year == ts.year) & (perfiles_2017.index.month == ts.month)]


def perfiles_consumo_en_intervalo(t0, tf):
    """Descarga de perfiles horarios para un intervalo dado
    Con objeto de calcular el precio medio ponderado de aplicación para dicho intervalo.
    :return: perfiles_intervalo
    :rtype: pd.Dataframe
    """
    t_ini = pd.Timestamp(t0)
    t_fin = pd.Timestamp(tf)
    assert (t_fin > t_ini)
    marca_fin = '{:%Y%m}'.format(t_fin)
    marca_ini = '{:%Y%m}'.format(t_ini)
    if marca_ini == marca_fin:
        perfiles = get_data_perfiles_finales_mes(t_ini)
    else:
        dates = pd.DatetimeIndex(start=t_ini.replace(day=1),
                                 end=t_fin.replace(day=1), freq='MS')
        perfiles = pd.concat([get_data_perfiles_finales_mes(t) for t in dates])
    return perfiles.loc[t_ini:t_fin].iloc[:-1]
    # return perfiles.loc[t_ini:t_fin.date() + pd.Timedelta('1D')].iloc[:-1] # incluye horas en t_fin.date()
