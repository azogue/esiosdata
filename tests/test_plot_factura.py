# -*- coding: utf-8 -*-
"""
Test Cases.

"""
import os
from unittest import TestCase


class TestsPlotsFactura(TestCase):
    """Tests de plots de FacturaElec."""

    def test_plots_estimaciones(self):
        """
        - Gráfica del consumo diario estimado en el intervalo.
        - Gráfica de consumo medio por día de la semana (patrón semanal de consumo).
        """
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from esiosdata import FacturaElec

        dest_path = os.path.dirname(os.path.abspath(__file__))
        params_savefig = dict(dpi=150, orientation='landscape', transparent=True, pad_inches=0.01)

        ts_0, ts_f = '2016-10-02', '2016-10-30'
        consumo_total_interv_kwh = 336.916
        print('Consumo horario estimado para el intervalo {} -> {}, con E={:.3f} kWh'
              .format(ts_0, ts_f, consumo_total_interv_kwh))

        factura = FacturaElec(ts_0, ts_f, consumo=consumo_total_interv_kwh)
        print(factura)

        s_consumo_kwh = factura.consumo_horario
        print(s_consumo_kwh)
        self.assertIs(s_consumo_kwh.empty, False)

        factura.plot_consumo_diario()
        fig = plt.gcf()
        fig.savefig(os.path.join(dest_path, 'test_factura_plot_consumo_diario.png'), **params_savefig)

        factura.plot_patron_semanal_consumo()
        fig = plt.gcf()
        fig.savefig(os.path.join(dest_path, 'test_factura_plot_patron_semanal.png'), **params_savefig)
