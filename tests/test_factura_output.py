# -*- coding: utf-8 -*-
"""
Test Cases para el cálculo de facturas de suministro eléctrico conforme al PVPC.

"""
import json
import os
from unittest import TestCase
from esiosdata.facturapvpc import FacturaElec, TIPO_PEAJE_NOC


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

