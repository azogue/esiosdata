# -*- coding: utf-8 -*-

import os
import pytz


NAME_DATA_PVPC = 'datapvpc.h5'
PATH_DATABASE = os.path.join(os.path.dirname(__file__), 'DATA', NAME_DATA_PVPC)

ANYO_INI = 2014  # Inicio de los datos en el origen
DATE_INI = '%lu0401' % ANYO_INI  # es abril 04
DATE_FMT = '%Y%m%d'
TZ = pytz.timezone('Europe/Madrid')
FREQ_DATA = '1h'
TS_DATA = 3600  # Muestreo en segundos

NUM_RETRIES = 7
MAX_THREADS_REQUESTS = 20  # Números altos colapsan el servidor de esios.ree.es

MAGS_PVPC = {'FEU': ('Término energía PVPC', True),
             'CAPh': ('Cargo capacidad', True),
             'CCOMh': ('Financiación OM', False),
             'CCOSh': ('Financiación OS', False),
             'CDSVh': ('Coste desvíos', False),
             'INTh': ('Servicio de interrumpibilidad', False),
             'OCh': ('Total OC', True),
             'PMASh': ('Otros sistema', False),
             'Pmh': ('Total PMH', False),
             'SAh': ('Total SAH', False),
             'TCUh': ('Precio producción', True)}

mags_web = {'FEU': ('Término energía PVPC', True),
            'CP': ('Costes de producción', True),
            'mercado': ('Mercado diario e intradiario', True),
            'ajuste': ('Servicios de ajuste', False),
            'peaje_acceso': ('Peaje de acceso', False),
            'pago_capacidad': ('Pago por capacidad', False),
            'serv_inint': ('Servicio de interrumpibilidad', False),
            'OS': ('Financiación OM', True),
            'OM': ('Financiación OS', False)}


def ref_tarifa(ind_tarifa):
    if ind_tarifa == 1:
        return '2.0 A', 'Tarifa por defecto (2.0 A)'
    elif ind_tarifa == 2:
        return '2.0 A', 'Eficiencia 2 periodos (2.0 DHA)'
    else:
        return '2.0 DHS', 'Vehículo eléctrico (2.0 DHS)'


def key_tarifa(key, ind_tarifa):
    if MAGS_PVPC[key][1]:
        return key + '_Z0%lu' % ind_tarifa
    else:
        return key
