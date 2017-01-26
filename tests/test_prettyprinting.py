# -*- coding: utf-8 -*-
"""
Test Cases para datos de demanda energética

"""
from unittest import TestCase


class TestsPP(TestCase):
    """Tests para coloured output."""

    def test_prettyprinting(self):
        """
        Pretty printing module testing.

        """
        import esiosdata
        import esiosdata.prettyprinting as pp

        pp.print_blue("Testing prettyprinting...")
        pp.print_bold("Testing prettyprinting...")
        pp.print_boldu("Testing prettyprinting...")
        pp.print_cyan("Testing prettyprinting...")
        pp.print_err("Testing prettyprinting...")
        pp.print_green("Testing prettyprinting...")
        pp.print_grey("Testing prettyprinting...")
        pp.print_greyb("Testing prettyprinting...")
        pp.print_info("Testing prettyprinting...")
        pp.print_infob("Testing prettyprinting...")
        pp.print_magenta("Testing prettyprinting...")
        pp.print_ok("Testing prettyprinting...")
        pp.print_red("Testing prettyprinting...")
        pp.print_redb("Testing prettyprinting...")
        pp.print_secc("Testing prettyprinting...")
        pp.print_warn("Testing prettyprinting...")
        pp.print_white("Testing prettyprinting...")
        pp.print_yellow("Testing prettyprinting...")
        pp.print_yellowb("Testing prettyprinting...")

        d = {'lalala': dir(esiosdata), 'testing_pp': 'lelele'}
        pp.print_ok(pp.ppdict(d))
        pp.print_green(pp.ppdict(d, html=True))
        pp.print_green(pp.ppdict({}))
        pp.print_red(pp.ppdict(None))
