# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 18:16:24 2015
DataBase de datos de consumo eléctrico
@author: Eugenio Panadero
"""
import argparse
import pandas as pd
from esiosdata.classdataesios import PVPC, DatosREE
from prettyprinting import print_yellow, print_secc, print_info, print_cyan, print_red

__author__ = 'Eugenio Panadero'
__copyright__ = "Copyright 2015, AzogueLabs"
__credits__ = ["Eugenio Panadero"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Eugenio Panadero"


# ------------------------------------
# MAIN CLI
# ------------------------------------
def main_cli():
    """
     Actualiza la base de datos de PVPC/DEMANDA almacenados como dataframe en local,
     creando una nueva si no existe o hubiere algún problema. Los datos registrados se guardan en HDF5
    """

    def _get_parser_args():
        p = argparse.ArgumentParser(description='Gestor de DB de PVPC/DEMANDA (esios.ree.es)')
        p.add_argument('-v', '--verbose', action='store_true', help='Shows extra info')
        p.add_argument('-d', '--dem', action='store_true', help='Select REE data')
        p.add_argument('-fu', '-FU', '--forceupdate', action='store_true', help="Force update of all available data")
        p.add_argument('-u', '-U', '--update', action='store_true', help="Updates data until today")
        p.add_argument('-p', '--plot', action='store_true', help="Plots info of DB")
        p.add_argument('-i', '--info', action='store', nargs='*', help="Shows info of DB")
        arguments = p.parse_args()
        return arguments, p

    def _parse_date(string, columns):
        try:
            ts = pd.Timestamp(string)
            print_cyan('{} es timestamp: {:%c} --> {}'.format(string, ts, ts.date()))
            columns.remove(string)
            return ts.date().isoformat()
        except ValueError:
            pass

    args, parser = _get_parser_args()
    print_secc('ESIOS PVPC')
    print_yellow(args)
    if args.dem:
        db_web = DatosREE(update=args.update, force_update=args.forceupdate, verbose=args.verbose)
    else:
        db_web = PVPC(update=args.update, force_update=args.forceupdate, verbose=args.verbose)
    data = db_web.data['data']
    if args.info is not None:
        if len(args.info) > 0:
            cols = args.info.copy()
            dates = [d for d in [_parse_date(s, cols) for s in args.info] if d]
            if len(dates) == 2:
                data = data.loc[dates[0]:dates[1]]
            elif len(dates) == 1:
                data = data.loc[dates[0]]
            if len(cols) > 0:
                try:
                    data = data[[c.upper() for c in cols]]
                except KeyError as e:
                    print_red('NO SE PUEDE FILTRAR LA COLUMNA (Exception: {})\nLAS COLUMNAS DISPONIBLES SON:\n{}'
                              .format(e, data.columns))
            print_info(data)
        else:
            print_secc('LAST 24h in DB:')
            print_info(data.iloc[-24:])
            print_cyan(data.columns)
    if args.plot:
        if args.dem:
            from esiosdata.pvpcplot import pvpcplot_tarifas_hora, pvpcplot_grid_hora
            print_red('IMPLEMENTAR PLOTS DEM')
        else:
            from esiosdata.pvpcplot import pvpcplot_tarifas_hora, pvpcplot_grid_hora
            if len(data) < 750:
                pvpcplot_grid_hora(data)
                # pvpcplot_tarifas_hora(data)
            else:
                print_red('La selección para plot es excesiva: {} samples de {} a {}\nSe hace plot de las últimas 24h'.
                          format(len(data), data.index[0], data.index[-1]))
                pvpcplot_grid_hora(db_web.data['data'].iloc[-24:])
                pvpcplot_tarifas_hora(db_web.data['data'].iloc[-24:])
                # , ax=None, show=True, ymax=None, plot_perdidas=True, fs=FIGSIZE)
    return db_web, db_web.data['data']


if __name__ == '__main__':
    datos_web, _data_dem = main_cli()
