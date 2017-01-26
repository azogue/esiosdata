# -*- coding: utf-8 -*-
"""
Test Cases para el cálculo de los perfiles de consumo de referencia para la estimación del reparto horario
del consumo eléctrico, con el fin de calcular el PVPC a aplicar al periodo considerado.

"""
from unittest import TestCase


class TestsPerfilesConsumo(TestCase):
    """Tests para el cálculo de los perfiles de consumo."""

    def test_perfiles_estimados_2017(self):
        """Extracción de perfiles estimados para 2017."""
        from esiosdata.perfilesconsumopvpc import get_data_perfiles_estimados_2017, get_data_perfiles_finales_mes

        perfiles_2017 = get_data_perfiles_estimados_2017()
        print(perfiles_2017)
        self.assertIs(perfiles_2017.empty, False)
        self.assertEqual(round(perfiles_2017.sum().sum(), 3), 4.)  # 4 cols, cada una debe sumar 1 para el año completo.

        perfiles_2017_02 = get_data_perfiles_finales_mes(2017, 2)
        print(perfiles_2017_02.head())
        self.assertIs(perfiles_2017_02.empty, False)

    def test_perfiles_finales(self):
        """Extracción de perfiles finales."""
        from esiosdata.perfilesconsumopvpc import get_data_perfiles_finales_mes

        perfiles_finales_2016_11 = get_data_perfiles_finales_mes(2016, 11)
        print(perfiles_finales_2016_11)
        self.assertIs(perfiles_finales_2016_11.empty, False)

    def test_estimacion_consumo_horario(self):
        """
        Estimación de consumo horario a partir de consumo total en un intervalo.
        Ejemplo de generación de valores de consumo horario a partir de consumo total y perfiles de uso.
        """
        import pandas as pd
        from esiosdata.perfilesconsumopvpc import perfiles_consumo_en_intervalo

        ts_0, ts_f = '2016-10-29', '2017-01-24'
        consumo_total_interv_kwh = 836.916
        print('Consumo horario estimado para el intervalo {} -> {}, con E={:.3f} kWh'
              .format(ts_0, ts_f, consumo_total_interv_kwh))

        # perfiles finales:
        perfs_interv = perfiles_consumo_en_intervalo(ts_0, ts_f)
        print(perfs_interv.head())
        print(perfs_interv.tail())

        # Estimación con perfil A:
        suma_perfiles_interv = perfs_interv['COEF. PERFIL A'].sum()
        consumo_estimado = pd.Series(perfs_interv['COEF. PERFIL A'] * consumo_total_interv_kwh / suma_perfiles_interv)
        print(consumo_estimado)
        self.assertIs(consumo_estimado.empty, False)

        # TODO comprobar resultado final con el proporcionado en https://facturaluz2.cnmc.es/facturaluz2.html
        # o en https://www.esios.ree.es/es/lumios?rate=rate3&start_date=31-10-2016T00:00&end_date=24-01-2017T00:00

    def test_plots_estimaciones(self):
        """
        - Gráfica del consumo diario estimado en el intervalo.
        - Gráfica de consumo medio por día de la semana (patrón semanal de consumo).
        """
        import pandas as pd
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from esiosdata.perfilesconsumopvpc import perfiles_consumo_en_intervalo
        from esiosdata.perfilesconsumopvpc import plot_consumo_diario_estimado, plot_patron_semanal_consumo

        ts_0, ts_f = '2016-10-02', '2016-10-30'
        consumo_total_interv_kwh = 336.916
        print('Consumo horario estimado para el intervalo {} -> {}, con E={:.3f} kWh'
              .format(ts_0, ts_f, consumo_total_interv_kwh))

        # perfiles finales:
        perfs_interv = perfiles_consumo_en_intervalo(ts_0, ts_f)
        print(perfs_interv.head())
        print(perfs_interv.tail())

        # Estimación con perfil B:
        suma_perfiles_interv = perfs_interv['COEF. PERFIL B'].sum()
        s_consumo_kwh = pd.Series(perfs_interv['COEF. PERFIL B'] * consumo_total_interv_kwh / suma_perfiles_interv)
        print(s_consumo_kwh)
        self.assertIs(s_consumo_kwh.empty, False)

        plot_consumo_diario_estimado(s_consumo_kwh)
        plt.show()

        plot_patron_semanal_consumo(s_consumo_kwh)
        plt.show()

