# -*- coding: utf-8 -*-

from collections import OrderedDict
import os
import pytz


VERBOSE = True
current_dir = os.path.dirname(__file__)

# El token se graba como texto plano en una línea, en un fichero oculto de nombre: ".token":
TOKEN_API = open(os.path.join(current_dir, '.token'), 'r').read()
SERVER = 'https://api.esios.ree.es'
HEADERS = {'Accept': 'application/json; application/vnd.esios-api-v1+json',
           'Content-Type': 'application/json',
           'Host': 'api.esios.ree.es',
           'Authorization': 'Token token="{}"'.format(TOKEN_API)}
NUM_RETRIES = 4
TIMEOUT = 8
USAR_MULTITHREAD = True
MAX_THREADS_REQUESTS = 100

TZ = pytz.timezone('Europe/Madrid')
DATE_FMT = '%Y-%m-%d'

# -----------
# DATOS PVPC
# -----------
NAME_DATA_PVPC = 'esiospvpc.h5'
PATH_DATABASE_PVPC = os.path.join(current_dir, 'DATA', NAME_DATA_PVPC)
# Inicio de los datos en el origen
DATE_INI_PVPC = '2014-04-01'

TS_DATA_PVPC = 3600  # Muestreo en segundos
TARIFAS_DESC = OrderedDict({'GEN': 'TARIFA POR DEFECTO (PEAJE 2.0 A)'})
TARIFAS_DESC.update({'NOC': 'EFICIENCIA 2 PERIODOS (PEAJE 2.0 DHA)'})
TARIFAS_DESC.update({'VHC': 'VEHÍCULO ELÉCTRICO (PEAJE 2.0 DHS)'})
TARIFAS = list(TARIFAS_DESC.keys())
COLS_PVPC = ['', 'PMH', 'SAH', 'TEU', 'PCAP', 'INT', 'FOS', 'FOM', 'COF']  # + TARIFA; COF: coefs perfilado

# -----------
# DATOS DEM
# -----------
NAME_DATA_DEM = 'esiosdem'
PATH_DATABASE_DEM = os.path.join(current_dir, 'DATA', NAME_DATA_DEM)

FREQ_DAT_DEM = '10min'
TS_DATA_DEM = 600  # Muestreo en segundos
KEYS_DATA_DEM = ['data', 'data_dias']
# TODO Revisar qué pasa con los datos antiguos!! --> contactar con ESIOS
# DATE_INI_DEM = '2007-01-01'
DATE_INI_DEM = '2015-10-01'
DATE_FIN_DEM = None
# ZONAS = ('Peninsula', 'Baleares', 'Canarias')
# ZONAS_MT = (USAR_MULTITHREAD, USAR_MULTITHREAD, USAR_MULTITHREAD)
# ZONAS_MAX_THREAD = (MAX_THREADS_REQUESTS, MAX_THREADS_REQUESTS, MAX_THREADS_REQUESTS / 10)
#_INI_ZONAS = dict(zip(ZONAS, ['2007-01-01', '2013-05-01', '2012-03-01']))
# TZ_ZONAS = dict(zip(ZONAS, ['Europe/Madrid', 'Europe/Madrid', 'Atlantic/Canary']))
# CURVAS_ZONAS = {'Peninsula': ('DEMANDA',),
#                 'Baleares': ('MALLORCA', 'MENORCA', 'MALL-MEN', 'IBI-FORM'),
#                 'Canarias': ('TENERIFE', 'EL_HIERRO', 'GCANARIA', 'LZ_FV',
#                              'FUERTEVE', 'LA_GOMERA', 'LANZAROT', 'LA_PALMA')}
# TIPOS_REQ_DEM = ('maxMin', 'prevProg', 'demandaGeneracion', 'coeficientesCO2')
TIPOS_REQ_DEM = ('IND_MaxMinRenovEol', 'IND_MaxMin', 'IND_DemandaRealGen', 'IND_DemandaPrevProg')
IND_ARCH_JSON_DEM = (117, 116, 115, 114)
D_TIPOS_REQ_DEM = OrderedDict(zip(TIPOS_REQ_DEM, IND_ARCH_JSON_DEM))
# TIPOS_REQ_DEM = ('IND_MaxMinRenovEol', 'IND_MaxMin', 'IND_DemandaRealGen', 'IND_DemandaPrevProg',
#                  'IND_Umbrales', 'IND_PrecioFinal', 'IND_PrecioDesvios', 'IND_Interconexiones', 'IND_DemandaInterrumpible')
# IND_ARCH_JSON_DEM = (117, 116, 115, 114, 67, 66, 65, 63, 62)
#  64: IND_PotenciaInstalada (MS)

# key: (Nombre, es_produccion, es_renov)
TIPOS_ENER = {
    "nuc": (u"Nuclear", True, False),
    "gf": (u"Fuel/gas", True, False),
    "car": (u"Carbón", True, False),
    "cc": (u"Ciclo combinado", True, False),
    "die": ("Motores diesel", True, False),
    "gas": ("Turbina de gas", True, False),
    "eol": (u"Eólica", True, True),
    "hid": (u"Hidráulica", True, True),
    "aut": (u"Resto reg.esp.", True, True),  # es_renov?? "aut": u"Cogeneración y resto"
    "cogenResto": (u"Cogeneración y resto", True, False),
    "sol": (u"Solar", True, True),
    "solFot": (u"Solar fotovoltaica", True, True),
    "solTer": (u"Solar térmica", True, True),
    "termRenov": (u"Térmica renovable", True, True),
    "icb": (u"Enlace balear", False, False),
    "inter": (u"Intercambios int", False, False),
    "cb": ("Enlace peninsular", False, False),
    "tnr": ("Resto reg.esp.", True, False),
    "emm": ("Enlace interislas", False, False),
    "fot": ("Solar fotovoltaica", True, True),
    "ele": ("Eléctrica", True, False),
    "vap": ("Turbina de vapor", True, False),
    "solar_termica": ("Solar térmica", True, True)}

