# -*- coding: utf-8 -*-
"""
Test Cases para datos de demanda energética. esiosdata CLI

"""
import sys
from unittest import TestCase
from unittest.mock import patch


class TestCaseCLI(TestCase):
    """Tests del CLI."""

    @staticmethod
    def exec_func_with_sys_argv(func_exec, custom_argv, *args_func_exec, **kwargs_func_exec):
        """
        Exec a CLI function patching sys.argv.
        For test CLI main functions with argparse

        :param func_exec:
        :param custom_argv:
        :param kwargs_func_exec:

        """
        # noinspection PyUnresolvedReferences
        with patch.object(sys, 'argv', custom_argv):
            print('TESTING CLI with sys.argv: {}'.format(sys.argv))
            func_exec(*args_func_exec, **kwargs_func_exec)

    def test_cli_main(self):
        """Test de CLI:

        p.add_argument('-v', '--verbose', action='store_true', help='Shows extra info')
        p.add_argument('-d', '--dem', action='store_true', help='Select REE data')
        p.add_argument('-fu', '-FU', '--forceupdate', action='store_true', help="Force update of all available data")
        p.add_argument('-u', '-U', '--update', action='store_true', help="Updates data until today")
        p.add_argument('-p', '--plot', action='store_true', help="Plots info of DB")
        p.add_argument('-i', '--info', action='store', nargs='*', help="Shows info of DB")
        """

        from esiosdata.__main__ import main_cli
        import matplotlib
        matplotlib.use('Agg')

        self.exec_func_with_sys_argv(main_cli, ['test_cli', '-u'])
        self.exec_func_with_sys_argv(main_cli, ['test_cli', '-v'])
        self.exec_func_with_sys_argv(main_cli, ['test_cli', '-d'])
        self.exec_func_with_sys_argv(main_cli, ['test_cli', '-i', '2016-12-01'])
        self.exec_func_with_sys_argv(main_cli, ['test_cli', '-i', '2016-10-01', '2016-10-10'])
        self.exec_func_with_sys_argv(main_cli, ['test_cli', '-p'])
        self.exec_func_with_sys_argv(main_cli, ['test_cli', '-d', '-p'])
        self.exec_func_with_sys_argv(main_cli, ['test_cli', '-i', '2016-12-01', '-d', '-p'])
        self.exec_func_with_sys_argv(main_cli, ['test_cli', '-i', '2016-12-01', '-p'])
        self.exec_func_with_sys_argv(main_cli, ['test_cli', '-i'])
        self.exec_func_with_sys_argv(main_cli, ['test_cli', '-i', 'ñañaña'])
