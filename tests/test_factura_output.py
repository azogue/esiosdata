# -*- coding: utf-8 -*-
"""
Test Cases para el cálculo de facturas de suministro eléctrico conforme al PVPC.

"""
import json
import os
from unittest import TestCase
from esiosdata.facturapvpc import FacturaElec, TIPO_PEAJE_NOC, COL_CONSUMO
from esiosdata.prettyprinting import print_cyan, print_red


path_export = os.path.dirname(os.path.abspath(__file__))


def _export_html(fact, name):
    htmlw_f = fact.to_html(web_completa=True)
    # print(htmlw_f)
    path = os.path.join(path_export, 'test_factura_web_{}.html'.format(name))
    with open(path, 'w') as file:
        file.write(htmlw_f)
    return path


def _variaciones_factura_noc(fact, name_base):
    print('FACTURA CON PEAJE "{}":\n{}'.format(fact.tipo_peaje, fact))
    fact.to_html()

    # Export webs a disco:
    f_path1 = _export_html(fact, name_base + '_NOC')
    print(f_path1)

    fact.tipo_peaje = 3
    print(fact)
    f_path2 = _export_html(fact, name_base + '_VHC')
    print(f_path2)

    fact.tipo_peaje = 1
    print(fact)
    f_path3 = _export_html(fact, name_base + '_GEN')
    print(f_path3)


class TestsFacturasOutput(TestCase):
    """Tests para el cálculo de facturas de suministro eléctrico conforme al PVPC."""

    def test_output_facturas(self):
        t_0, t_f = '2016-01-01', '2017-01-09'
        f1 = FacturaElec(t_0, t_f, consumo=[500, 500], tipo_peaje=TIPO_PEAJE_NOC)
        _variaciones_factura_noc(f1, '2_tramos')

        t_0, t_f = '2016-11-01', '2016-12-09'
        f1 = FacturaElec(t_0, t_f, consumo=[500, 500], tipo_peaje=TIPO_PEAJE_NOC)
        _variaciones_factura_noc(f1, '1_tramo')

        t_0, t_f = '2016-11-01', '2016-12-09'
        f1 = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_NOC)
        _variaciones_factura_noc(f1, '1_tramo_vacia')

        t_0, t_f = '2016-01-01', '2017-01-09'
        f1 = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_NOC)
        _variaciones_factura_noc(f1, '2_tramos_vacia')

    def test_json_facturas(self):
        t_0, t_f = '2016-01-01', '2017-01-09'
        f1 = FacturaElec(t_0, t_f, consumo=[500, 500], tipo_peaje=TIPO_PEAJE_NOC)
        print(json.dumps(f1.to_dict(include_text_repr=True, include_html_repr=True)))

        t_0, t_f = '2016-11-01', '2016-12-09'
        f1 = FacturaElec(t_0, t_f, consumo=[500, 500], tipo_peaje=TIPO_PEAJE_NOC)
        print(json.dumps(f1.to_dict(include_text_repr=True, include_html_repr=True)))

        t_0, t_f = '2016-11-01', '2016-12-09'
        f1 = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_NOC)
        print(json.dumps(f1.to_dict(include_text_repr=True, include_html_repr=True)))

        t_0, t_f = '2016-01-01', '2017-01-09'
        f1 = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_NOC)
        print(json.dumps(f1.to_dict(include_text_repr=True, include_html_repr=True)))

    def test_reparto_coste(self):

        def _check_export_coste(f):
            s_coste = f.reparto_coste()
            df_coste = f.reparto_coste(detallado=True)
            total_s = s_coste.sum()
            total_df = df_coste.drop(COL_CONSUMO, axis=1).sum().round(2).sum()
            print_cyan(df_coste.head(3))
            print(df_coste.sum())
            print_red('COSTE TOTAL: {:.2f} €; s_coste: {:.2f} €; df_coste: {:.2f} €'
                      .format(f.coste_total, total_s, total_df))
            print(f)

        t_0, t_f = '2016-10-01', '2016-10-04'
        f1 = FacturaElec(t_0, t_f, consumo=[30, 40], tipo_peaje=TIPO_PEAJE_NOC)
        _check_export_coste(f1)

        f2 = FacturaElec(t_0, t_f, consumo=70)
        _check_export_coste(f2)

        t_0, t_f = '2016-10-01', '2017-02-04'
        f3 = FacturaElec(t_0, t_f, consumo=[300, 400], tipo_peaje=TIPO_PEAJE_NOC)
        _check_export_coste(f3)

        f4 = FacturaElec(t_0, t_f, consumo=700)
        _check_export_coste(f4)

        print(f4.reparto_coste())
        print(f4.reparto_coste().describe())