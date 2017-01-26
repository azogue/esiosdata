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
import pandas as pd
# import pytz
from urllib.error import HTTPError


# tz = pytz.timezone('Europe/Madrid')
URL_PERFILES_2017 = 'http://www.ree.es/sites/default/files/01_ACTIVIDADES/' \
                    'Documentos/Documentacion-Simel/perfiles_iniciales_2017.xlsx'
DATA_PERFILES_2017 = None


##############################################
#       OBTENCIÓN DE PERFILES                #
##############################################
def _gen_ts(mes, dia, hora, año):
    """Generación de timestamp a partir de componentes de fecha.
    Ojo al DST y cambios de hora."""
    try:
        return dt.datetime(año, mes, dia, hora - 1)  # , tzinfo=tz)
    except ValueError as e:
        print('ERROR Cambio de hora (día con 25h): "{}"; el 2017-{}-{}, hora={}'.format(e, mes, dia, hora))
        return dt.datetime(2017, mes, dia, hora - 2)  # , tzinfo=tz)


def get_data_coeficientes_perfilado_2017():
    """Extrae la información de las dos hojas del Excel proporcionado por REE
    con los perfiles iniciales para 2017.
    :return: perfiles_2017, coefs_alpha_beta_gamma
    :rtype: tuple
    """
    # Coeficientes de perfilado y demanda de referencia (1ª hoja)
    cols_sheet1 = ['Mes', 'Día', 'Hora',
                   'Pa,0m,d,h', 'Pb,0m,d,h', 'Pc,0m,d,h', 'Pd,0m,d,h', 'Demanda de Referencia 2017 (MW)']
    perfs_2017 = pd.read_excel(URL_PERFILES_2017, header=None, skiprows=[0, 1], names=cols_sheet1)
    perfs_2017['ts'] = [_gen_ts(mes, dia, hora, 2017)
                        for mes, dia, hora in zip(perfs_2017.Mes, perfs_2017.Día, perfs_2017.Hora)]
    # Coefs Alfa, Beta, Gamma (2ª hoja):
    coefs_alpha_beta_gamma = pd.read_excel(URL_PERFILES_2017, sheetname=1)
    return perfs_2017.set_index('ts'), coefs_alpha_beta_gamma


def get_data_perfiles_estimados_2017():
    """Extrae perfiles estimados para 2017 con el formato de los CSV's mensuales con los perfiles definitivos.
    :return: perfiles_2017
    :rtype: pd.Dataframe
    """
    global DATA_PERFILES_2017
    if DATA_PERFILES_2017 is None:
        perf_demref_2017, _ = get_data_coeficientes_perfilado_2017()
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
    # print_info('Descargando perfiles finales del mes de {:%b de %Y} en {}'.format(ts, url_perfiles_finales))
    # Intenta descargar perfiles finales, y si falla, recurre a los estimados para 2017:
    try:
        perfiles_finales = pd.read_csv(url_perfiles_finales, sep=';', encoding='latin_1', compression='gzip'
                                       ).dropna(how='all', axis=1)
    except HTTPError as e:
        print('HTTPError: {}. Se utilizan perfiles estimados de 2017.'.format(e))
        perfiles_2017 = get_data_perfiles_estimados_2017()
        return perfiles_2017[(perfiles_2017.index.year == ts.year) & (perfiles_2017.index.month == ts.month)]

    cols_date = ['MES', 'DIA', 'HORA', 'AÑO']
    zip_date = zip(*[perfiles_finales[c] for c in cols_date])
    perfiles_finales['ts'] = [_gen_ts(*args) for args in zip_date]
    cols_date.append('VERANO(1)/INVIERNO(0)')
    # perfiles_finales['dst'] = perfiles_finales['VERANO(1)/INVIERNO(0)'].astype(bool)
    return perfiles_finales.set_index('ts').drop(cols_date, axis=1)


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


##############################################
#       PLOTS                                #
##############################################
def plot_consumo_diario_estimado(s_consumo_kwh):
    """Gráfica del consumo diario estimado en el intervalo.
    :param s_consumo_kwh: pd.Series con consumo horario en kWh
    :return: matplotlib axes
    """
    consumo_diario_est = s_consumo_kwh.groupby(pd.TimeGrouper('D')).sum()
    ax = consumo_diario_est.plot(figsize=(16, 9), color='blue', lw=2)
    params_lines = dict(lw=1, linestyle=':', alpha=.6)
    xlim = consumo_diario_est[0], consumo_diario_est.index[-1]
    ax.hlines([consumo_diario_est.mean()], *xlim, color='orange', **params_lines)
    ax.hlines([consumo_diario_est.max()], *xlim, color='red', **params_lines)
    ax.hlines([consumo_diario_est.min()], *xlim, color='green', **params_lines)
    ax.set_title('Consumo diario estimado (Total={:.1f} kWh)'.format(s_consumo_kwh.sum()))
    ax.set_ylabel('kWh/día')
    ax.set_xlabel('')
    ax.set_ylim((0, consumo_diario_est.max() * 1.1))
    ax.grid('on', axis='x')
    return ax


def plot_patron_semanal_consumo(s_consumo_kwh):
    """Gráfica de consumo medio por día de la semana (patrón semanal de consumo).
    :param s_consumo_kwh: pd.Series con consumo horario en kWh
    :return: matplotlib axes
    """
    media_diaria = s_consumo_kwh.groupby(pd.TimeGrouper('D')).sum()
    media_semanal = media_diaria.groupby(lambda x: x.weekday).mean().round(1)
    días_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    media_semanal.columns = días_semana

    ax = media_semanal.T.plot(kind='bar', figsize=(16, 9), color='orange', legend=False)
    ax.set_xticklabels(días_semana, rotation=0)
    ax.set_title('Patrón semanal de consumo')
    ax.set_ylabel('kWh/día')
    ax.grid('on', axis='y')
    ax.hlines([media_diaria.mean()], -1, 7, lw=3, color='blue', linestyle=':')
    return ax
