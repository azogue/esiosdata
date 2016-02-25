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


import argparse
from pvpc.classdatapvpc import PVPC
# from importpvpcdata import pvpc_data_dia


#############################
# Main
#############################
def get_parser_args():
    p = argparse.ArgumentParser(description='Gestor de DB de PyMoney')
    p.add_argument('-v', '--verbose', action='store_true', help='Shows extra info')
    p.add_argument('-fu', '-FU', '--forceupdate', action='store_true', help="Force update of all data until today")
    p.add_argument('-u', '-U', '--update', action='store_true', help="Updates data until today")
    arguments = p.parse_args()
    # print('\n\t** ARGUMENTOS: {}\n'.format(arguments))
    # ** ARGUMENTOS: Namespace(download=True, info=True, tvshow=['rick', 'morty'], update=True)
    # if len(arguments.tvshow) > 0:
    #     str_busca = ' '.join(arguments.tvshow)
    #     bool_selec = True
    # else:
    #     str_busca = ''
    #     bool_selec = False
    return arguments, p  # , bool_selec, str_busca


# ------------------------------------
# MAIN CLI
# ------------------------------------
def main():
    """
     Actualiza la base de datos de PVPC almacenados como dataframe en local,
     creando una nueva si no existe o hubiere algún problema. Los datos registrados se guardan en HDF5
    """

    # data_ej = pvpc_data_dia('20141026')
    # print(data_ej)
    args, parser = get_parser_args()

    data_pvpc = PVPC(update=args.update, force_update=args.forceupdate, verbose=args.verbose)  # ,False)
    data_pvpc.close()
    return data_pvpc, data_pvpc.data['data']


if __name__ == '__main__':
    # pvpc = main()
    # print(pvpc)
    datos_pvpc, data = main()
    print('Se devuelven variables: datos_pvpc, data.')


# tocInit = time.time()
#
# DATA = PVPC(False)
# DATA.info_data()
# print(cjoin.FEU_Z02)
# #dcjoin.FEU_Z02.plot()
#
#
# ind_tarifa = 2
# keys = [key_tarifa(k, ind_tarifa) for k in MAGS_PVPC.keys()]
# print(eys)
# pvpc_data = dcjoin[keys]
# print(vpc_data.ix['2014-10-25 20:00:00'])
#
# AAC = (pvpc_data.FEU_Z02 - pvpc_data.TCUh_Z02)
# CP = (pvpc_data.SAh + pvpc_data.Pmh + pvpc_data.OCh_Z02)
# PERD = pvpc_data.TCUh_Z02 / CP - 1
# MERC = pvpc_data.Pmh * (1+PERD)
# AJUS = pvpc_data.SAh  * (1+PERD)
# CAP = (pvpc_data.OCh_Z02 - pvpc_data.CCOMh - pvpc_data.CCOSh - pvpc_data.INTh) * (1+PERD)
#
# pvpc_data['mercado'] = MERC
# pvpc_data['ajuste'] = AJUS
# pvpc_data['acceso'] = AAC.copy()
# pvpc_data['capacidad'] = CAP
# pvpc_data['sint'] = pvpc_data.INTh  * (1+PERD)
# pvpc_data['fos'] = pvpc_data.CCOSh  * (1+PERD)
# pvpc_data['fom'] = pvpc_data.CCOMh  * (1+PERD)
#
# print pvpc_data.ix['2014-10-25 20:00:00']
#
# #plt.style.use('ggplot')
# plt.style.context('fivethirtyeight')
#
# lista = ['mercado','ajuste','acceso','capacidad','sint','fos', 'fom']
# colors = ['0C212C', '103B52', '103B52', '236E9B', '5193B2', '89B6CC', 'C4DAE4']
# #pd.DataFrame.
# fig, ax = plt.subplots(1,1)
# pvpc_data.plot(y=key_tarifa('FEU', ind_tarifa), ax=ax, lw=2, color='#1C5A8B')
# ax.hold(True)
# pvpc_data.plot(y=lista[::-1], ax=ax, kind='area', color=['#'+c for c in colors])
# plt.show()
#
# # ax.annotate('Test', (mdates.date2num(x[1]), y[1]), xytext=(15, 15),
# #             textcoords='offset points', arrowprops=dict(arrowstyle='-|>'))
# #
# # fig.autofmt_xdate()
# # descrColumnas = {'Dia','Hora','Peaje','Periodo',...
# #               'FEU','TEU','TCU',...
# #               'PERD_PVPC','PERD_STD','CP','OC',...
# #               'OS','OM','Cargo_cap','Serv_interr',...
# #               'SAH','Otros_sistema','Coste_desvios',...
# #               'Coste_banda','Coste_reserva','Coste_restr_tec',...
# #               'PMH','Comp_intradia','Mercado_diario',...
# #               'NULL','Coef_perfilado'};
# # descrColumnas = {'Día','Hora','Peaje','Periodo',...
# #               'FEU','TEU','TCU',...
# #               'PERD_PVPC','PERD_STD','CP','Total OC',...
# #               'OS','OM','Cargo capacidad','Servicio interrumpibilidad',...
# #               'Total SAH','Otros sistema','Coste desvíos',...
# #               'Coste banda','Coste reserva','Coste restricciones técnicas diario',...
# #               'Total PMH','Componente intradiario 1','Mercado diario',...
# #               '','Coeficiente perfilado'};
# # udsColumnas = [{'','h','','',...
# #               '?/MWh consumo','?/MWh consumo','?/MWh consumo',...
# #               '%','%'},rellena({'?/MWh bc'},15), {'',''}];
# # plt.plot(dcjoin.FEU_Z02)
# # plt.show()

