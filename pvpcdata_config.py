# -*- coding: utf-8 -*-

from collections import OrderedDict
import os
import pytz


# Esconder token
SERVER = 'https://api.esios.ree.es'
HEADERS = {'Accept': 'application/json; application/vnd.esios-api-v1+json',
           'Content-Type': 'application/json',
           'Host': 'api.esios.ree.es',
           'Authorization': 'Token token="5850e7063a8a852f1d245883170fc15628408072d9fe23ef964487d4f1fd9a74"'}
NUM_RETRIES = 4
MAX_THREADS_REQUESTS = 100

NAME_DATA_PVPC = 'esiospvpc.h5'
PATH_DATABASE = os.path.join(os.path.dirname(__file__), 'DATA', NAME_DATA_PVPC)

# Inicio de los datos en el origen
DATE_INI = '20140401'
DATE_FMT = '%Y%m%d'
TZ = pytz.timezone('Europe/Madrid')
TS_DATA = 3600  # Muestreo en segundos

TARIFAS_DESC = OrderedDict({'GEN': 'TARIFA POR DEFECTO (PEAJE 2.0 A)'})
TARIFAS_DESC.update({'NOC': 'EFICIENCIA 2 PERIODOS (PEAJE 2.0 DHA)'})
TARIFAS_DESC.update({'VHC': 'VEHÍCULO ELÉCTRICO (PEAJE 2.0 DHS)'})
TARIFAS = list(TARIFAS_DESC.keys())

COLS_PVPC = ['', 'PMH', 'SAH', 'TEU', 'PCAP', 'INT', 'FOS', 'FOM', 'COF']  # + TARIFA; COF: coefs perfilado
