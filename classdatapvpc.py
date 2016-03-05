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


from dataweb.classdataweb import DataWeb
from esiospvpc.importpvpcdata import pvpc_url_dia, pvpc_procesa_datos_dia
from esiospvpc.pvpcdata_config import HEADERS, PATH_DATABASE, DATE_INI, DATE_FMT, TZ, TS_DATA
from esiospvpc.pvpcdata_config import NUM_RETRIES, MAX_THREADS_REQUESTS


class PVPC(DataWeb):
    def __init__(self, update=True, force_update=False, verbose=True):
        self._pvpc_mean_daily = None
        self._pvpc_mean_monthly = None
        super(PVPC, self).__init__(PATH_DATABASE,
                                   'Histórico de precios de la electricidad [PVPC] (esios.ree.es)',
                                   force_update, verbose, update=update,
                                   TZ=TZ, DATE_FMT=DATE_FMT, DATE_INI=DATE_INI, TS_DATA=TS_DATA,
                                   USAR_MULTITHREAD=True, NUM_RETRIES=NUM_RETRIES,
                                   MAX_THREADS_REQUESTS=MAX_THREADS_REQUESTS,
                                   HEADERS=HEADERS, JSON_REQUESTS=True)  # , PARAMS_REQUESTS=)
    # Definición necesaria en superclase
    def url_data_dia(self, key_dia):
        return pvpc_url_dia(key_dia)

    # Definición necesaria en superclase
    def procesa_data_dia(self, key_dia, datos_para_procesar):
        return pvpc_procesa_datos_dia(key_dia, datos_para_procesar, verbose=self.verbose)

    def get_resample_data(self):
        if self.data is not None:
            if self._pvpc_mean_daily is None:
                self._pvpc_mean_daily = self.data['data'].resample('D', how='mean')
            if self._pvpc_mean_monthly is None:
                self._pvpc_mean_monthly = self.data['data'].resample('MS', how='mean')
        return self._pvpc_mean_daily, self._pvpc_mean_monthly