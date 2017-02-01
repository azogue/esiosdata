# -*- coding: utf-8 -*-
"""
Test Cases para el cálculo de los perfiles de consumo de referencia para la estimación del reparto horario
del consumo eléctrico, con el fin de calcular el PVPC a aplicar al periodo considerado.

"""
from unittest import TestCase
import pandas as pd


class TestsPerfilesConsumo(TestCase):
    """Tests para el cálculo de los perfiles de consumo."""

    def test_0_perfiles_estimados_2017(self):
        """Extracción de perfiles estimados para 2017."""
        from esiosdata.perfilesconsumopvpc import get_data_perfiles_estimados_2017, get_data_perfiles_finales_mes

        perfiles_2017 = get_data_perfiles_estimados_2017(force_download=False)
        print(perfiles_2017)
        self.assertIs(perfiles_2017.empty, False)
        self.assertEqual(round(perfiles_2017.sum().sum(), 3), 4.)  # 4 cols, cada una debe sumar 1 para el año completo.

        perfiles_2017_02 = get_data_perfiles_finales_mes(2017, 2)
        print(perfiles_2017_02.head())
        self.assertIs(perfiles_2017_02.empty, False)

        # read from disk:
        perfiles_2017_bis = get_data_perfiles_estimados_2017(force_download=True)
        perfiles_2017_bis2 = get_data_perfiles_estimados_2017(force_download=False)
        assert pd.DataFrame(perfiles_2017 == perfiles_2017_bis).all().all()
        assert pd.DataFrame(perfiles_2017_bis2 == perfiles_2017_bis).all().all()

    def test_perfiles_finales(self):
        """Extracción de perfiles finales."""
        from esiosdata.perfilesconsumopvpc import get_data_perfiles_finales_mes

        perfiles_finales_2016_11 = get_data_perfiles_finales_mes(2016, 11)
        print(perfiles_finales_2016_11)
        self.assertIs(perfiles_finales_2016_11.empty, False)

    def test_perfiles_estimacion_consumo_horario(self):
        """
        Estimación de consumo horario a partir de consumo total en un intervalo.
        Ejemplo de generación de valores de consumo horario a partir de consumo total y perfiles de uso.
        """
        from esiosdata.perfilesconsumopvpc import perfiles_consumo_en_intervalo

        ts_0, ts_f = '2016-10-29', '2017-01-24'
        consumo_total_interv_kwh = 836.916
        print('Consumo horario estimado para el intervalo {} -> {}, con E={:.3f} kWh'
              .format(ts_0, ts_f, consumo_total_interv_kwh))

        # perfiles finales:
        perfs_interv = perfiles_consumo_en_intervalo(ts_0, ts_f)
        print(perfs_interv.head())
        print(perfs_interv.tail())

        # perfiles finales 1 mes:
        perfs_interv = perfiles_consumo_en_intervalo(ts_0, '2016-10-30')
        print(perfs_interv.head())
        print(perfs_interv.tail())

        # Estimación con perfil A:
        suma_perfiles_interv = perfs_interv['COEF. PERFIL A'].sum()
        consumo_estimado = pd.Series(perfs_interv['COEF. PERFIL A'] * consumo_total_interv_kwh / suma_perfiles_interv)
        print(consumo_estimado)
        self.assertIs(consumo_estimado.empty, False)
