# -*- coding: utf-8 -*-
"""
Test Cases para datos de demanda energética

"""
from unittest import TestCase


class TestsDemanda(TestCase):
    """Tests para el almacén local de datos de demanda energética."""

    def test_create_db(self):
        """Test de `force_update` los datos de demanda energética."""
        from esiosdata import DatosREE

        dem = DatosREE(force_update=True, verbose=True)
        print(dem)
        print(dem.last_entry())
        self.assertIsNotNone(dem.data['data'])
        self.assertEqual(dem.data['data'].empty, False)

    def test_attrs_dem(self):
        """Test de attributos extra de los datos de demanda energética."""
        from esiosdata import DatosREE
        import pandas as pd

        dem = DatosREE(update=True, verbose=True)

        url = dem.url_data_dia('2017-01-01')
        print(url)
        assert(len(url) > 0)

        url = dem.url_data_dia(pd.Timestamp('2017-01-01'))
        print(url)
        assert(len(url) > 0)

        url = dem.url_data_dia('20170101')
        print(url)
        assert(len(url) > 0)

        self.assertIsNone(dem.procesa_data_dia('2017-01-10', {})[0])

        dem.integridad_data()

    def test_data_dia(self):
        """Test de descarga y procesado de los datos de DatosREE de días concretos."""
        from esiosdata.importdemdata import dem_data_dia

        data = dem_data_dia('2006-03-01')
        print(data)
        self.assertIsNone(data)

        data = dem_data_dia('2009-03-01')
        print(data)
        self.assertIsNone(data)

        data_1 = dem_data_dia('2015-03-01')
        print(data_1)
        self.assertIsNotNone(data_1)

        data_2 = dem_data_dia(str_dia='2017-01-22')
        print(data_2)
        self.assertIsNotNone(data_2)
        self.assertEqual(data_2['data_dias'].empty, False)

        data = dem_data_dia('2015-10-22', '2015-10-27')
        print(data)
        self.assertIsNotNone(data)
        self.assertEqual(data['data_dias'].empty, False)

        data = dem_data_dia('2015-03-01', '2015-04-25')
        print(data)
        self.assertIsNone(data)
        # self.assertIsNotNone(data)
        # self.assertEqual(data['data_dias'].empty, False)

        data = dem_data_dia('2007-03-01', '2007-04-25')
        print(data)
        self.assertIsNone(data)
