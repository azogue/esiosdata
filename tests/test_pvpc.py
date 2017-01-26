# -*- coding: utf-8 -*-
"""
Test Cases para datos de PVPC

"""
from unittest import TestCase


class TestsPVPC(TestCase):
    """Tests para el almacén local de datos de PVPC."""

    def test_create_db(self):
        """Test de `force_update` los datos de PVPC."""
        from esiosdata import PVPC

        pvpc = PVPC(force_update=True, verbose=True)
        print(pvpc)
        self.assertIsNotNone(pvpc.data['data'])
        self.assertEqual(pvpc.data['data'].empty, False)

    def test_resample(self):
        """Test de resamples diarios y mensuales de los datos de PVPC."""
        from esiosdata import PVPC

        pvpc = PVPC(update=True, verbose=True)
        pvpc_mean_daily, pvpc_mean_monthly = pvpc.get_resample_data()
        print(pvpc_mean_daily)
        print(pvpc_mean_monthly)
        self.assertIsNotNone(pvpc_mean_daily)
        self.assertIsNotNone(pvpc_mean_monthly)
        self.assertEqual(pvpc_mean_daily.empty, False)
        self.assertEqual(pvpc_mean_monthly.empty, False)

    def test_attrs_pvpc(self):
        """Test de attributos extra de los datos de PVPC."""
        from esiosdata import PVPC
        import pandas as pd

        pvpc = PVPC(update=True, verbose=True)
        self.assertEquals(len(pvpc.tarifas), 3)
        self.assertEquals(len(pvpc.colores_tarifas), 3)

        url = pvpc.url_data_dia('2017-01-01')
        print(url)
        assert(len(url) > 0)

        url = pvpc.url_data_dia(pd.Timestamp('2017-01-01'))
        print(url)
        assert(len(url) > 0)

        url = pvpc.url_data_dia('20170101')
        print(url)
        assert(len(url) > 0)

        self.assertEqual(pvpc.procesa_data_dia('2017-01-10', {})[0], None)

    def test_data_dia(self):
        """Test de descarga y procesado de los datos de PVPC de días concretos."""
        from esiosdata.importpvpcdata import pvpc_data_dia, pvpc_calc_tcu_cp_feu_d, pvpc_procesa_datos_dia

        data_1 = pvpc_data_dia(str_dia='2000-06-22')
        print(data_1)
        self.assertIs(type(data_1), str)

        data_1 = pvpc_data_dia(str_dia='2015-06-22')
        print(data_1)
        self.assertIsNotNone(data_1)
        self.assertEqual(data_1.empty, False)

        data_2 = pvpc_data_dia(str_dia='2017-01-22')
        print(data_2)
        self.assertIsNotNone(data_2)
        self.assertEqual(data_2.empty, False)

        data = pvpc_data_dia('2015-10-20', '2015-11-20')
        print(data)
        self.assertIsNotNone(data)
        self.assertEqual(data.empty, False)

        data_proc = pvpc_calc_tcu_cp_feu_d(data_1.copy(), verbose=True)
        print(data_proc)
        self.assertIsNotNone(data)
        self.assertEqual(data.empty, False)

        data_proc = pvpc_calc_tcu_cp_feu_d(data_2.copy(), verbose=True)
        print(data_proc)
        self.assertIsNotNone(data)
        self.assertEqual(data.empty, False)

        self.assertEqual(pvpc_procesa_datos_dia(None, data, verbose=True, calcula_extra=True)[0], None)
