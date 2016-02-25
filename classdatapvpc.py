# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 18:16:24 2015
@author: Eugenio Panadero
"""
__author__ = 'Eugenio Panadero'
__copyright__ = "Copyright 2015, AzogueLabs"
__credits__ = ["Eugenio Panadero"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Eugenio Panadero"


from dataweb.classdataweb import DataWeb
from pvpc.importpvpcdata import pvpc_url_dia, pvpc_procesa_datos_dia
from pvpc.pvpcdata_config import PATH_DATABASE, DATE_INI, DATE_FMT, TZ, TS_DATA, NUM_RETRIES, MAX_THREADS_REQUESTS


class PVPC(DataWeb):
    def __init__(self, update=True, force_update=False, verbose=True):
        super(PVPC, self).__init__(PATH_DATABASE,
                                   'Histórico de precios de la electricidad [PVPC] (esios.ree.es)',
                                   force_update, verbose, update=update,
                                   TZ=TZ, DATE_FMT=DATE_FMT, DATE_INI=DATE_INI, TS_DATA=TS_DATA,
                                   NUM_RETRIES=NUM_RETRIES, MAX_THREADS_REQUESTS=MAX_THREADS_REQUESTS)

    # Definición necesaria en superclase
    def url_data_dia(self, key_dia):
        return pvpc_url_dia(key_dia)

    # Definición necesaria en superclase
    def procesa_data_dia(self, key_dia, datos_para_procesar):
        return pvpc_procesa_datos_dia(key_dia, datos_para_procesar)
