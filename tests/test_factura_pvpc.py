# -*- coding: utf-8 -*-
"""
Test Cases para el cálculo de facturas de suministro eléctrico conforme al PVPC.

"""
import os
from unittest import TestCase
from esiosdata.facturapvpc import (FacturaElec, ROUND_PREC, TIPO_PEAJE_GEN, TIPO_PEAJE_NOC, TIPO_PEAJE_VHC,
                                   ZONA_IMPUESTOS_CANARIAS, ZONA_IMPUESTOS_PENIN_BALEARES, ZONA_IMPUESTOS_CEUTA_MELILLA)


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


class TestsFacturasPVPC(TestCase):
    """Tests para el cálculo de facturas de suministro eléctrico conforme al PVPC."""

    def test_facturas_base(self):
        """Facturas base, comprueba subtotales con resultados de simuladores:
        https://www.esios.ree.es/es/lumios? y https://facturaluz.cnmc.es/facturaluz1.html"""
        t_0, t_f = '2016-11-01', '2017-01-05'
        f1 = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_VHC, consumo=[219, 126, 154],
                         zona_impuestos=ZONA_IMPUESTOS_PENIN_BALEARES, alquiler_euros=1.62)
        print(f1)
        print(f1.consumo_total)
        _check_results_factura(f1, 65, 25.72, 53.31, 4.04, 1.62, 17.78, 102.47)

        f2 = FacturaElec(t_0, t_f, potencia_contratada=5, tipo_peaje=TIPO_PEAJE_GEN, consumo=[499],
                         zona_impuestos=ZONA_IMPUESTOS_CANARIAS, con_bono_social=False, alquiler_euros=1.62)
        print(f2)
        _check_results_factura(f2, 65, 37.28, 63.68, 5.16, 1.62, 3.30, 111.04)

        f2_b = FacturaElec(t_0, t_f, potencia_contratada=5, tipo_peaje=TIPO_PEAJE_GEN, consumo=499,
                           zona_impuestos=ZONA_IMPUESTOS_CANARIAS, con_bono_social=True, alquiler_euros=1.62)
        _check_results_factura(f2_b, 65, 37.28, 63.68, 3.87, 1.62, 2.50, 83.71)
        print(f2_b)

        t_0, t_f = '2016-11-01', '2016-12-09'
        f3 = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_NOC, consumo=[219, 280],
                         zona_impuestos=ZONA_IMPUESTOS_CEUTA_MELILLA, alquiler_euros=1.62)
        print(f3)
        _check_results_factura(f3, 38, 15.06, 51.89, 3.42, 1.62, 0.77, 72.76)

        f4 = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_VHC, consumo=[219, 126, 154],
                         zona_impuestos=ZONA_IMPUESTOS_PENIN_BALEARES, alquiler_euros=1.62)
        print(f4)
        _check_results_factura(f4, 38, 15.06, 51.75, 3.42, 1.62, 15.09, 86.94)

        t_0, t_f = '2016-02-25', '2017-01-30'
        f_dst1 = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_NOC, consumo=[4000, 2000],
                             zona_impuestos=ZONA_IMPUESTOS_PENIN_BALEARES)
        print(f_dst1)
        _check_results_factura(f_dst1, 340, 134.53, 650.84, 40.15, 9.03, 175.26, 1009.81)

        t_0, t_f = '2016-02-25', '2016-08-30'
        f_dst2 = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_NOC, consumo=[4000, 2000],
                             zona_impuestos=ZONA_IMPUESTOS_PENIN_BALEARES, alquiler_euros=9.03)
        print(f_dst2)
        _check_results_factura(f_dst2, 187, 74.11, 552.91, 32.06, 9.03, 140.30, 808.41)

    def test_exporta_fichero_consumo_ofi(self):
        """Exportación de CSV de consumo horario conforme al formato generado por las distribuidoras."""

        path_export = os.path.dirname(os.path.abspath(__file__))
        t_0, t_f = '2016-11-01', '2016-12-09'
        f3 = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_NOC, consumo=[219, 280],
                         zona_impuestos=ZONA_IMPUESTOS_CEUTA_MELILLA)
        print(f3)
        _check_results_factura(f3, 38, 15.06, 51.89, 3.42, 1.01, 0.74, 72.12)
        consumo_ofi = f3.generacion_csv_oficial_consumo_horario(path_export)
        print(consumo_ofi)

        t_0, t_f = '2017-01-01', '2017-01-30'
        f = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_GEN, consumo=600,
                        zona_impuestos=ZONA_IMPUESTOS_PENIN_BALEARES, con_bono_social=True)
        print(f)
        _check_results_factura(f, 29, 11.28, 88.76, 3.84, 0.77, 16.72, 96.36)
        consumo_ofi = f.generacion_csv_oficial_consumo_horario(path_export)
        print(consumo_ofi)

        t_0, t_f = '2016-10-30', '2017-01-30'
        f = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_GEN, consumo=800,
                        zona_impuestos=ZONA_IMPUESTOS_PENIN_BALEARES, con_bono_social=True)
        print(f)
        _check_results_factura(f, 92, 36.24, 107.14, 5.5, 2.45, 24.25, 139.73)
        consumo_ofi = f.generacion_csv_oficial_consumo_horario(path_export)
        print(consumo_ofi)

    def test_factura_vacia(self):
        t_0, t_f = '2016-11-01', '2016-12-09'
        f = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_NOC, zona_impuestos=ZONA_IMPUESTOS_CEUTA_MELILLA)
        print(f)
        print(f.consumo_total)
        _check_results_factura(f, 38, 15.06, 0., 0.77, 1.01, 0.20, 17.04)

    def test_pvpc_data(self):
        t_0, t_f = '2016-11-01', '2016-12-09'
        f = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_NOC, zona_impuestos=ZONA_IMPUESTOS_CEUTA_MELILLA)
        f.gasto_equipo_medida = 10.8
        print(f)
        _check_results_factura(f, 38, 15.06, 0., 0.77, 10.8, 0.59, 27.22)
        print(f.pvpc_horas_periodo)

    def test_cambio_tarifa(self):
        t_0, t_f = '2016-11-01', '2016-12-09'
        f = FacturaElec(t_0, t_f, consumo=1000.)
        print('FACTURA CON PEAJE "{}":\n{}'.format(f.tipo_peaje, f))
        str_1 = str(f)

        f.tipo_peaje = 2
        print('FACTURA CON PEAJE "{}":\n{}'.format(f.tipo_peaje, f))

        f.tipo_peaje = 'VHC'
        print('FACTURA CON PEAJE "{}":\n{}'.format(f.tipo_peaje, f))

        f.tipo_peaje = '2.0A'
        print('FACTURA CON PEAJE "{}":\n{}'.format(f.tipo_peaje, f))
        assert str_1 == str(f)

        f.tipo_peaje = 'lalala'
        assert str_1 == str(f)

    def test_genera_facturas(self):
        # t_0, t_f = '2016-11-01', '2016-12-09'
        d_cambio = '2016-10-30'
        t_0, t_f = '2016-09-01', '2016-12-09'
        f = FacturaElec(t_0, t_f, consumo=1000.)
        print('FACTURA CON PEAJE "{}":\n{}'.format(f.tipo_peaje, f))
        str_1 = str(f)

        # Generación con datos horarios
        consumo_horario = f.consumo_horario
        f2 = FacturaElec(consumo=consumo_horario)
        # print(f2)
        assert str_1 == str(f2)

        try:
            _ = FacturaElec()
            assert 0
        except AttributeError as e:
            print(e)

        # Generación con datos horarios sin tz:
        print(consumo_horario.loc[d_cambio].iloc[:10])
        consumo_horario_naive = consumo_horario.copy()
        consumo_horario_naive.index = consumo_horario_naive.index.tz_localize(None)
        print(consumo_horario_naive.loc[d_cambio].iloc[:10])
        print(len(consumo_horario_naive), consumo_horario_naive.index.is_unique)
        consumo_horario_naive = consumo_horario_naive.reset_index()
        consumo_horario_naive = consumo_horario_naive.loc[consumo_horario_naive.fecha.drop_duplicates(keep='first').index]
        print(len(consumo_horario_naive), consumo_horario_naive.set_index('fecha').index.is_unique)

        f3 = FacturaElec(consumo=consumo_horario_naive.set_index('fecha').kWh)
        print(f3)
        assert str_1 == str(f3)
        print(f3.consumo_horario.loc[d_cambio].iloc[:10])
        assert not f3.consumo_horario.equals(f.consumo_horario)
