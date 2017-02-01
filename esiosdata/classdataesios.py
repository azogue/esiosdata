# -*- coding: utf-8 -*-
"""
Web Scraper para datos de demanda, producción y coste de la energía eléctrica en España.

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
import pandas as pd
from dataweb.classdataweb import DataWeb
from esiosdata.esios_config import (HEADERS, NUM_RETRIES, MAX_THREADS_REQUESTS, USAR_MULTITHREAD, DATE_FMT, TZ, VERBOSE,
                                    PATH_DATABASE_PVPC, DATE_INI_PVPC, TS_DATA_PVPC, PATH_DATABASE_DEM, DATE_INI_DEM,
                                    TS_DATA_DEM, KEYS_DATA_DEM, FREQ_DAT_DEM)
from esiosdata.importdemdata import dem_url_dia, dem_procesa_datos_dia
from esiosdata.importpvpcdata import pvpc_url_dia, pvpc_procesa_datos_dia


__author__ = 'Eugenio Panadero'
__credits__ = ["Eugenio Panadero"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Eugenio Panadero"


class PVPC(DataWeb):
    """Handler de datos de PVPC en fichero local."""

    def __init__(self, update=True, force_update=False, verbose=VERBOSE):
        self._pvpc_mean_daily = None
        self._pvpc_mean_monthly = None
        super(PVPC, self).__init__(PATH_DATABASE_PVPC,
                                   'Histórico de precios de la electricidad [PVPC] (esios.ree.es)',
                                   forzar_update=force_update, verbose=verbose, update_init=update,
                                   TZ=TZ, DATE_FMT=DATE_FMT, DATE_INI=DATE_INI_PVPC, TS_DATA=TS_DATA_PVPC,
                                   USAR_MULTITHREAD=USAR_MULTITHREAD, NUM_RETRIES=NUM_RETRIES,
                                   MAX_THREADS_REQUESTS=MAX_THREADS_REQUESTS,
                                   HEADERS=HEADERS, JSON_REQUESTS=True)  # , PARAMS_REQUESTS=)

    # Definición necesaria en superclase
    def url_data_dia(self, key_dia):
        """Devuelve la url de descarga de datos para `key_dia`."""
        return pvpc_url_dia(key_dia)

    # Definición necesaria en superclase
    def procesa_data_dia(self, key_dia, datos_para_procesar):
        """Procesa los datos descargados correspondientes a un día `key_dia`."""
        return pvpc_procesa_datos_dia(key_dia, datos_para_procesar, verbose=self.verbose)

    def get_resample_data(self):
        """Obtiene los dataframes de los datos de PVPC con resampling diario y mensual."""
        if self.data is not None:
            if self._pvpc_mean_daily is None:
                self._pvpc_mean_daily = self.data['data'].resample('D').mean()
            if self._pvpc_mean_monthly is None:
                self._pvpc_mean_monthly = self.data['data'].resample('MS').mean()
        return self._pvpc_mean_daily, self._pvpc_mean_monthly

    @property
    def tarifas(self):
        """Devuelve los códigos de las tarifas monofásicas de < 10 kW."""
        return ['GEN', 'NOC', 'VHC']

    @property
    def colores_tarifas(self):
        """Devuelve un dict con los colores (hex values) por tarifa."""
        return {'GEN': '#00A1DA', 'NOC': '#DF4A32', 'VHC': '#74BA04'}


class DatosREE(DataWeb):
    """Handler de datos de demanda energética en fichero local."""

    def __init__(self,  # zona=ZONAS[0], curva=CURVAS_ZONAS[ZONAS[0]][0],
                 update=True, force_update=False, verbose=VERBOSE,
                 fecha_inicio=DATE_INI_DEM, fecha_fin=None,
                 usar_multithread=USAR_MULTITHREAD, max_n_threads=MAX_THREADS_REQUESTS):
        self.verbose = verbose
        # TODO incorporar resto de zonas y curvas:
        self.zona = 'PENINSULA'
        self.curva = 'DEMANDA'
        # path_store = '{}_{}_{}.h5'.format(PATH_DATABASE, self.zona, self.curva)
        path_store = '{}_{}.h5'.format(PATH_DATABASE_DEM, self.zona)
        titulo = 'Histórico de demanda y producción eléctrica en Zona: {}\n' \
                 '(demanda.ree.es, curva: {})'.format(self.zona, self.curva)
        params = {'update_init': update, 'TZ': TZ,  # pytz.timezone(TZ_ZONAS[zona]),
                  'DATE_FMT': DATE_FMT, 'DATE_INI': fecha_inicio, 'DATE_FIN': fecha_fin,
                  'TS_DATA': TS_DATA_DEM, 'keys_data_web': KEYS_DATA_DEM,
                  'NUM_RETRIES': NUM_RETRIES,
                  'USAR_MULTITHREAD': usar_multithread, 'MAX_THREADS_REQUESTS': max_n_threads}
        super(DatosREE, self).__init__(path_store, titulo, force_update, verbose, **params)

    # Definición necesaria en superclase
    def url_data_dia(self, key_dia):
        """Devuelve la url de descarga de datos para `key_dia`."""
        return dem_url_dia(key_dia)  # , self.zona, self.curva)

    # Definición necesaria en superclase
    def procesa_data_dia(self, str_dia, datos_para_procesar):
        """Procesa los datos descargados correspondientes a un día `key_dia`."""
        return dem_procesa_datos_dia(str_dia, datos_para_procesar)  # self.TZ

    # Definición opcional
    def post_update_data(self):
        """
        Definición opcional para analizar la información descargada en busca de errores,
        que quedan almacenados en `self.data['errores']`.
        """
        if self.data is not None:
            self.data['errores'] = self.busca_errores_data()

    # Definición específica
    def last_entry(self, data_revisar=None, key_revisar=None):
        """
        Definición específica para filtrar por datos de demanda energética (pues los datos se extienden más allá del
        tiempo presente debido a las columnas de potencia prevista y programada.

        :param data_revisar: (OPC) Se puede pasar un dataframe específico
        :param key_revisar: (OPC) Normalmente, para utilizar 'dem'
        :return: tmax, num_entradas
        """
        if data_revisar is None and key_revisar is None:
            data_revisar = self.data[self.masterkey][pd.notnull(self.data[self.masterkey]['dem'])]
            super(DatosREE, self).printif('Últimos valores de generación y demanda:', 'info')
            super(DatosREE, self).printif(data_revisar.tail(), 'info')
            return super(DatosREE, self).last_entry(data_revisar, 'dem')
        else:
            return super(DatosREE, self).last_entry(data_revisar, key_revisar)

    # Definición específica
    def integridad_data(self, data_integr=None, key=None):
        """
        Definición específica para comprobar timezone y frecuencia de los datos, además de comprobar
        que el index de cada dataframe de la base de datos sea de fechas, único (sin duplicados) y creciente
        :param data_integr:
        :param key:
        """
        if data_integr is None and key is None and all(k in self.data.keys() for k in KEYS_DATA_DEM):
            assert(self.data[KEYS_DATA_DEM[0]].index.freq == FREQ_DAT_DEM
                   and self.data[KEYS_DATA_DEM[0]].index.tz == self.TZ)
            if self.data[KEYS_DATA_DEM[1]] is not None:
                assert(self.data[KEYS_DATA_DEM[1]].index.freq == 'D')
        super(DatosREE, self).integridad_data(data_integr, key)

    def busca_errores_data(self):
        """
        Busca errores o inconsistencias en los datos adquiridos
        :return: Dataframe de errores encontrados
        """
        data_busqueda = self.append_delta_index(TS_DATA_DEM, data_delta=self.data[self.masterkey].copy())
        idx_desconex = (((data_busqueda.index < 'now') & (data_busqueda.index >= self.DATE_INI)) &
                        ((data_busqueda.delta_T > 1) | data_busqueda['dem'].isnull() |
                         data_busqueda['pre'].isnull() | data_busqueda['pro'].isnull()))
        sosp = data_busqueda[idx_desconex].copy()
        assert len(sosp) == 0
        # if len(sosp) > 0:
        #     cols_show = ['bad_dem', 'bad_pre', 'bad_T', 'delta', 'delta_T', 'dem', 'pre', 'pro']
        #     cols_ss = cols_show[:3]
        #     how_r = {k: pd.Series.sum if k == 'delta' else 'sum' for k in cols_show}
        #     sosp[cols_show[0]] = sosp['dem'].isnull()
        #     sosp[cols_show[1]] = sosp['pre'].isnull()
        #     sosp[cols_show[2]] = sosp['delta_T'] > 1
        #     if verbose:
        #         print(sosp[cols_show].tz_localize(None).resample('D', how=how_r).dropna(how='all', subset=cols_ss))
        #         print(sosp[cols_show].tz_localize(None).resample('MS', how=how_r).dropna(how='all', subset=cols_ss))
        #     return sosp
        return pd.DataFrame()
