# -*- coding: utf-8 -*-
"""
Test Cases para el cálculo de facturas de suministro eléctrico conforme al PVPC con datos horarios

"""
from unittest import TestCase
from esiosdata.facturapvpc import (FacturaElec, ROUND_PREC, TIPO_PEAJE_VHC, ZONA_IMPUESTOS_PENIN_BALEARES)


def _check_results_factura(factura,
                           num_dias_factura, coste_termino_fijo, coste_termino_consumo,
                           impuesto_electrico_general,
                           gasto_equipo_medida, coste_iva, coste_total):
    def _print_c(v1, v2):
        if v1 != v2:
            print('ERROR: {} != {}'.format(v1, v2))

    repr_factura = str(factura)
    consumo_h = factura.consumo_horario
    factura.consumo_total = consumo_h
    _print_c(round(factura.num_dias_factura, ROUND_PREC), num_dias_factura)
    _print_c(round(factura.coste_termino_fijo, ROUND_PREC), coste_termino_fijo)
    _print_c(round(factura.coste_termino_consumo, ROUND_PREC), coste_termino_consumo)
    _print_c(round(factura.impuesto_electrico_general, ROUND_PREC), impuesto_electrico_general)
    _print_c(round(factura.gasto_equipo_medida, ROUND_PREC), gasto_equipo_medida)
    _print_c(round(factura.coste_iva, ROUND_PREC), coste_iva)
    _print_c(round(factura.coste_total, ROUND_PREC), coste_total)
    assert str(factura) == repr_factura
    assert all([round(factura.num_dias_factura, ROUND_PREC) == num_dias_factura,
                round(factura.coste_termino_fijo, ROUND_PREC) == coste_termino_fijo,
                round(factura.coste_termino_consumo, ROUND_PREC) == coste_termino_consumo,
                round(factura.impuesto_electrico_general, ROUND_PREC) == impuesto_electrico_general,
                round(factura.gasto_equipo_medida, ROUND_PREC) == gasto_equipo_medida,
                round(factura.coste_iva, ROUND_PREC) == coste_iva,
                round(factura.coste_total, ROUND_PREC) == coste_total])


class TestsFacturasDH(TestCase):
    """Tests para el cálculo de facturas de suministro eléctrico conforme al PVPC."""

    def test_factura_incompleta(self):
        """Factura de datos horarios con horas perdidas."""
        from esiosdata.prettyprinting import print_ok, print_red, print_cyan, print_info

        t_0, t_f = '2016-11-01', '2017-01-05'
        params = dict(tipo_peaje=TIPO_PEAJE_VHC, zona_impuestos=ZONA_IMPUESTOS_PENIN_BALEARES, alquiler_euros=1.62)
        f1 = FacturaElec(t_0, t_f, consumo=[219, 126, 154], **params)
        print_info(f1)
        print_ok(f1.consumo_total)
        _check_results_factura(f1, 65, 25.72, 53.31, 4.04, 1.62, 17.78, 102.47)

        datos_horarios = f1.consumo_horario.copy()
        FacturaElec(consumo=datos_horarios, **params)

        # Pérdida de 2 horas. Idénticos subtotales:
        print_info(len(datos_horarios))
        datos_horarios = datos_horarios.drop(datos_horarios.index[1500:1502])
        print_red(len(datos_horarios))

        f2 = FacturaElec(consumo=datos_horarios, **params)
        print_ok(f2)
        print_ok(f2.consumo_total)
        _check_results_factura(f2, 65, 25.72, 53.31, 4.04, 1.62, 17.78, 102.47)

        # Pérdida de > horas. Resultado diferente con menos consumo:
        datos_horarios = datos_horarios.drop(datos_horarios.index[1400:1412])
        print_red(len(datos_horarios))

        f3 = FacturaElec(consumo=datos_horarios, **params)
        print_cyan(f3)
        print_cyan(f3.consumo_total)
        assert str(f3) != str(f1)
        self.assertLess(f3.coste_termino_consumo, f1.coste_termino_consumo)
