# -*- coding: utf-8 -*-

from collections import OrderedDict
import os
import pytz


current_dir = os.path.dirname(__file__)

NAME_DATA_PVPC = 'esiospvpc.h5'
PATH_DATABASE = os.path.join(current_dir, 'DATA', NAME_DATA_PVPC)

# El token se graba como texto plano en una línea, en un fichero oculto de nombre: ".token":
TOKEN_API = open(os.path.join(current_dir, '.token'), 'r').read()
SERVER = 'https://api.esios.ree.es'
HEADERS = {'Accept': 'application/json; application/vnd.esios-api-v1+json',
           'Content-Type': 'application/json',
           'Host': 'api.esios.ree.es',
           'Authorization': 'Token token="{}"'.format(TOKEN_API)}
NUM_RETRIES = 4
MAX_THREADS_REQUESTS = 100

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
