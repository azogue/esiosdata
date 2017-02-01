# -*- coding: utf-8 -*-
"""
Facturación de datos de consumo eléctrico para particulares según PVPC.

* Documentos de origen con los valores de los peajes de acceso a baja tensión (≤1kV) y baja potencia (≤10kW):
  - [Tarifas 2015 (IDAE)](http://www.idae.es/uploads/documentos/documentos_Tarifas_Reguladas_ene_2015_9195098b.pdf)
  - [Tarifas 2016 (IDAE)](http://www.idae.es/uploads/documentos/documentos_Tarifas_Reguladas_ene_2016_a197c904.pdf)

* Periodo de facturación:
  A partir de 31/03/2014. El día de lectura inicial está excluido y el día de lectura final está incluido.

* Discriminación horaria:

  - '2.0DHA': Potencia máxima 10 kW, con dos periodos:
    P1 (Punta) Invierno: 12-22h / Verano: 13-23h | P2 (Valle) Invierno: 22-12h / Verano: 23-13h.

  - '2.0DHS': Tarifa vehículo eléctrico. Potencia máxima 10 kW, con
    P1 (Punta) 13-23h | P2 (Valle) 23-01h / 07-13h | P3 (Supervalle) 01-07h.

  - El horario Valle de 14 horas abarca de 22 a 12 h en invierno y de 23 a 13 h en verano.
  - El horario Punta de 10 horas abarca de 12 a 22 h en invierno y de 13 a 23 h en verano.

@author: Eugenio Panadero
"""
import os
import pandas as pd
# from esiosdata.perfilesconsumopvpc import perfiles_consumo_en_intervalo  # Se obtienen directamente de PVPC ('COF*')
from esiosdata.classdataesios import PVPC
from esiosdata.importpvpcdata import pvpc_calc_tcu_cp_feu_d
from esiosdata.prettyprinting import print_warn, print_cyan, print_yellow, print_info, print_err, print_ok


TEMPLATE_FACTURA = '''FACTURA ELÉCTRICA:
--------------------------------------------------------------------------------
* Fecha inicio             	{ts_ini:%d/%m/%Y}
* Fecha final              	{ts_fin:%d/%m/%Y}
* Peaje de acceso          	{cod_peaje} ({desc_peaje})
* Potencia contratada      	{p_contrato:.2f} kW
* Consumo periodo          	{consumo_total:.2f} kWh
* ¿Bono Social?            	{con_bono}
* Equipo de medida         	{coste_medida:.2f} €
* Impuestos                	{desc_impuesto}
* Días facturables         	{dias_fact}
--------------------------------------------------------------------------------

- CÁLCULO DEL TÉRMINO FIJO POR POTENCIA CONTRATADA:
  {detalle_term_fijo}
{total_termino_fijo}

- CÁLCULO DEL TÉRMINO VARIABLE POR ENERGÍA CONSUMIDA (TARIFA {cod_peaje}):
  {detalle_term_variable}
{total_termino_variable}
{detalle_descuento}
- IMPUESTO ELÉCTRICO:
{detalle_term_impuesto_elec}

{total_equipo_medida}

- IVA O EQUIVALENTE:
{detalle_iva}

################################################################################
{total_factura}
################################################################################
'''

MASK_T_BONO = "\n- DESCUENTO POR BONO SOCIAL:   	                                    {:.2f} €\n"
MASK_T_FIJO = "  {pot:.2f} kW * {coef_t_fijo} €/kW/año * {dias} días ({y}) / {dias_y} = {coste:.2f} €"
MASK_T_VAR_PERIOD_TRAMO = " *Tramo {ind_tramo}, de {ts_ini:%d/%m/%Y} a {ts_fin:%d/%m/%Y}:"
# MASK_T_IMP_ELEC = '''  {}% x ({:.2f}€ + {:.2f}€)                                 {:.2f} €'''
MASK_T_IMP_ELEC = '''    {}% x ({:.2f}€ + {:.2f}€)'''
# MASK_T_IVA_M = '''  {:.0f}% de {:.2f}€ + {:.0f}% de {:.2f}€                                    {:.2f} €'''
# MASK_T_IVA_U = '''  {:.0f}% de {:.2f}€                                                         {:.2f} €'''
MASK_T_IVA_M = '''    {:.0f}% de {:.2f}€ + {:.0f}% de {:.2f}€'''
MASK_T_IVA_U = '''    {:.0f}% de {:.2f}€'''
# MASK_T_VAR_PERIOD = '''  Periodo {ind_periodo}: {valor_medio_periodo:.6f} €/kWh                          -> {coste_periodo:.2f}€(P{ind_periodo})
#     - Peaje de acceso: {consumo_periodo:.0f}kWh * {valor_med_tea:.6f}€/kWh = {coste_tea:.2f}€
#     - Coste de la energía: {consumo_periodo:.0f}kWh * {valor_med_tcu:.6f}€/kWh = {coste_tcu:.2f}€'''

MASK_T_VAR_PERIOD = "  Periodo {ind_periodo}: {valor_medio_periodo:.6f} €/kWh"
MASK_T_VAR_PERIOD += "                          -> {coste_periodo:.2f}€(P{ind_periodo})\n"
MASK_T_VAR_PERIOD += "    - Peaje de acceso: {consumo_periodo:.0f}kWh * {valor_med_tea:.6f}€/kWh = {coste_tea:.2f}€\n"
MASK_T_VAR_PERIOD += "    - Coste de la energía: {consumo_periodo:.0f}kWh * {valor_med_tcu:.6f}€/kWh = {coste_tcu:.2f}€"

# TODO cambiar distinción tarifaria de 'año' a periodo reglamentario,

ROUND_PREC = 2  # 0,01 €
ROUND_PREC_INTERN = 6
DEFAULT_CUPS = 'ES00XXXXXXXXXXXXXXDB'
DEFAULT_POTENCIA_CONTRATADA_KW = 3.45
DEFAULT_BONO_SOCIAL = False
# DEFAULT_IMPUESTO_ELECTRICO = 0.0511269642  # 4,864% por 1,05113
DEFAULT_IMPUESTO_ELECTRICO = 0.0511269632  # 4,864% por 1,05113
DEFAULT_ALQUILER_CONT_MES = 0.81  # € / mes para monofásico

TIPO_PEAJE_GEN = '2.0A'
TIPO_PEAJE_NOC = '2.0DHA'
TIPO_PEAJE_VHC = '2.0DHS'
DATOS_TIPO_PEAJE = {TIPO_PEAJE_GEN: ('General', 'COEF. PERFIL A', 'GEN', 1),
                    TIPO_PEAJE_NOC: ('Nocturna', 'COEF. PERFIL B', 'NOC', 2),
                    TIPO_PEAJE_VHC: ('Vehículo eléctrico', 'COEF. PERFIL D', 'VHC', 3)}
CODES_TARIFAS = [x[2] for x in DATOS_TIPO_PEAJE.values()]

ZONA_IMPUESTOS_PENIN_BALEARES = 'IVA'
ZONA_IMPUESTOS_CANARIAS = 'IGIC'
ZONA_IMPUESTOS_CEUTA_MELILLA = 'IPSI'
DATOS_ZONAS_IMPUESTOS = {ZONA_IMPUESTOS_PENIN_BALEARES: ('Península y Baleares (IVA)', 'IVA', .21, .21),
                         ZONA_IMPUESTOS_CANARIAS: ('Canarias (IGIC)', 'IGIC', .03, .07),
                         ZONA_IMPUESTOS_CEUTA_MELILLA: ('Ceuta y Melilla (IPSI)', 'IPSI', .01, .04)}

MARGEN_COMERCIALIZACIÓN_EUR_KW_AÑO_MCF = 4.  # € /(kW·año)
TERM_POT_PEAJE_ACCESO_EUR_KW_AÑO_TPA = {2014: 35.648148,
                                        2015: 38.043426,    # 3,503618833 * 12 - 4
                                        2016: 38.043426,    # (3,1702855 + 0,33333) * 12
                                        2017: 37.156426}
TERM_ENER_PEAJE_ACCESO_EUR_KWH_TEA = {2014: {TIPO_PEAJE_GEN: [0.044027],
                                             TIPO_PEAJE_NOC: [0.062012, 0.002215],
                                             TIPO_PEAJE_VHC: [0.074568, 0.017809, 0.006596]},
                                      2015: {TIPO_PEAJE_GEN: [0.044027],
                                             TIPO_PEAJE_NOC: [0.062012, 0.002215],
                                             TIPO_PEAJE_VHC: [0.074568, 0.017809, 0.006596]},
                                      2016: {TIPO_PEAJE_GEN: [0.044027],
                                             TIPO_PEAJE_NOC: [0.062012, 0.002215],
                                             TIPO_PEAJE_VHC: [0.062012, 0.002879, 0.000886]},
                                      2017: {TIPO_PEAJE_GEN: [0.044027],
                                             TIPO_PEAJE_NOC: [0.062012, 0.002215],
                                             TIPO_PEAJE_VHC: [0.062012, 0.002879, 0.000886]}}


def _asigna_periodos_discr_horaria(series, tipo_peaje):
    num_periodos = DATOS_TIPO_PEAJE[tipo_peaje][3]
    if num_periodos > 1:  # DISCRIMINACIÓN HORARIA
        df = pd.DataFrame(series)
        tt = df.index
        name = series.name
        p_cierre_periodos = dict(include_start=True, include_end=False)
        idx_13_23h = tt[tt.indexer_between_time('13:00', '23:00', **p_cierre_periodos)]
        if num_periodos == 3:  # '2.0DHS': Tarifa vehículo eléctrico
            df['P1'] = df['P2'] = df['P3'] = False
            idx_23_01h = tt[tt.indexer_between_time('23:00', '01:00', **p_cierre_periodos)]
            idx_01_07h = tt[tt.indexer_between_time('01:00', '07:00', **p_cierre_periodos)]
            idx_07_13h = tt[tt.indexer_between_time('07:00', '13:00', **p_cierre_periodos)]
            df.loc[idx_13_23h, 'P1'] = True
            df.loc[idx_23_01h.union(idx_07_13h), 'P2'] = True
            df.loc[idx_01_07h, 'P3'] = True
            assert df[['P1', 'P2', 'P3']].sum(axis=1).sum() == len(df)
        else:  # '2.0DHA': Tarifa nocturna, con dos periodos
            assert num_periodos == 2
            idx_verano = tt[[x.dst().total_seconds() > 0 for x in tt]]
            idx_invierno = tt[[x.dst().total_seconds() == 0 for x in tt]]
            df['P1'] = df['P2'] = False
            idx_12_22h = tt[tt.indexer_between_time('12:00', '22:00', **p_cierre_periodos)]
            idx_22_12h = tt[tt.indexer_between_time('22:00', '12:00', **p_cierre_periodos)]
            idx_23_13h = tt[tt.indexer_between_time('23:00', '13:00', **p_cierre_periodos)]
            if len(idx_verano) > 0:
                df.loc[idx_13_23h.intersection(idx_verano), 'P1'] = True
                df.loc[idx_23_13h.intersection(idx_verano), 'P2'] = True
            if len(idx_invierno) > 0:
                df.loc[idx_12_22h.intersection(idx_invierno), 'P1'] = True
                df.loc[idx_22_12h.intersection(idx_invierno), 'P2'] = True
            assert df[['P1', 'P2']].sum(axis=1).sum() == len(df)
        return True, df
    else:
        return False, series


class FacturaElec(object):
    """Cálculo de la facturación eléctrica en España para particulares."""

    def __init__(self, t0, tf, consumo=None,
                 tipo_peaje=TIPO_PEAJE_GEN,
                 potencia_contratada=DEFAULT_POTENCIA_CONTRATADA_KW,
                 con_bono_social=DEFAULT_BONO_SOCIAL,
                 zona_impuestos=ZONA_IMPUESTOS_PENIN_BALEARES,
                 alquiler_euros=None, alquiler_euros_dia=DEFAULT_ALQUILER_CONT_MES / 30,
                 impuesto_electrico=DEFAULT_IMPUESTO_ELECTRICO,
                 cups=DEFAULT_CUPS):
        # CUPS
        self._cups = cups

        # Intervalo
        self._t0 = pd.Timestamp(t0)
        self._tf = pd.Timestamp(tf)

        # Datos de facturación
        self._tipo_peaje = tipo_peaje
        self._potencia_contratada = potencia_contratada
        self._con_bono_social = con_bono_social
        self._zona_impuestos = zona_impuestos
        self._impuesto_electrico_general = impuesto_electrico
        self.alquiler_euros = alquiler_euros
        self.alquiler_euros_dia = alquiler_euros_dia

        # Datos de PVPC y perfiles de consumo
        self._pvpc_data = None
        self._pvpc_horario = None

        # Datos de cálculo
        self._consumo = consumo
        self._consumo_horario = None
        self._consumos_totales_por_periodo = None
        self._num_dias_factura = None
        self._periodos_fact = None
        self._termino_fijo = None
        self._termino_fijo_total = None
        self._coste_peaje_acceso_tea = None
        self._coste_ponderado_energia_tcu = None
        self._termino_variable_total = None
        self._descuento_bono_social = 0.
        self._termino_impuesto_electrico = None
        self._termino_equipo_medida = None
        self._terminos_iva = None
        self._termino_iva_total = None
        self._total_factura = None

        # PROCESADO DE FACTURA
        self._calcula_factura()

    def __repr__(self):
        """Representación en texto de la factura eléctrica."""
        def _append_total(str_line, total_value):
            return '{:70} {:.2f} €'.format(str_line, total_value)

        detalle_tfijo = '\n  '.join([MASK_T_FIJO.format(pot=self._potencia_contratada, dias=ndias, y=año,
                                                        dias_y=ndias_año, coste=coste, coef_t_fijo=coef_p)
                                     for (ndias, ndias_año, año), (coste, coef_p)
                                     in zip(self._periodos_fact, self._termino_fijo)])

        detalle_tvar = []
        con_2_años = len(self._periodos_fact) > 1
        zip_v = zip(self._coste_peaje_acceso_tea, self._coste_ponderado_energia_tcu, self._consumos_totales_por_periodo)
        for i, (tea, tcu, cons) in enumerate(zip_v):
            if con_2_años:
                if i == 0:
                    ts_ini, ts_fin = self._t0, self._t0.replace(day=31, month=12)
                else:
                    ts_ini, ts_fin = self._tf.replace(day=1, month=1), self._tf
                detalle_tvar.append(MASK_T_VAR_PERIOD_TRAMO.format(ind_tramo=i + 1, ts_ini=ts_ini, ts_fin=ts_fin))
                detalle_tvar += [MASK_T_VAR_PERIOD.format(ind_periodo=j + 1, consumo_periodo=cons_p,
                                                          valor_medio_periodo=(tcu_p + tea_p) / cons_p,
                                                          coste_periodo=tcu_p + tea_p,
                                                          valor_med_tcu=tcu_p / cons_p, coste_tcu=tcu_p,
                                                          valor_med_tea=tea_p / cons_p, coste_tea=tea_p)
                                 for j, (tea_p, tcu_p, cons_p) in enumerate(zip(tea, tcu, cons))]
            else:
                detalle_tvar.append(MASK_T_VAR_PERIOD.format(ind_periodo=i + 1, consumo_periodo=cons,
                                                             valor_medio_periodo=(tcu + tea) / cons,
                                                             coste_periodo=tcu + tea,
                                                             valor_med_tcu=tcu / cons, coste_tcu=tcu,
                                                             valor_med_tea=tea / cons, coste_tea=tea))

        detalle_impuesto = _append_total(MASK_T_IMP_ELEC.format(self._impuesto_electrico_general * 100.,
                                                                self.coste_termino_fijo, self.coste_termino_consumo),
                                         self.impuesto_electrico_general)

        _, _, impuesto_gen, impuesto_medida = DATOS_ZONAS_IMPUESTOS[self._zona_impuestos]
        subt_fijo_var = self._termino_fijo_total + self._termino_variable_total
        subt_fijo_var += self._termino_impuesto_electrico + self._descuento_bono_social

        if impuesto_gen != impuesto_medida:
            detalle_iva = MASK_T_IVA_M.format(impuesto_gen * 100, subt_fijo_var,
                                              impuesto_medida * 100, self._termino_equipo_medida)
        else:
            detalle_iva = MASK_T_IVA_U.format(impuesto_gen * 100, subt_fijo_var + self._termino_equipo_medida)

        detalle_descuento = ''
        if self._con_bono_social:
            detalle_descuento = _append_total('- DESCUENTO POR BONO SOCIAL:', self.descuento_bono_social)
        params = dict(ts_ini=self._t0, ts_fin=self._tf, cod_peaje=self._tipo_peaje, consumo_total=self.consumo_total,
                      desc_peaje=DATOS_TIPO_PEAJE[self._tipo_peaje][0], p_contrato=self._potencia_contratada,
                      con_bono='Sí' if self._con_bono_social else 'No', coste_medida=self.gasto_equipo_medida,
                      desc_impuesto=DATOS_ZONAS_IMPUESTOS[self._zona_impuestos][0], dias_fact=self.num_dias_factura,
                      detalle_descuento='\n{}\n'.format(detalle_descuento),
                      coste_impuesto_elec=self.impuesto_electrico_general,
                      total_termino_fijo=_append_total("     -> Término fijo", self.coste_termino_fijo),
                      total_termino_variable=_append_total("     -> Término de consumo", self.coste_termino_consumo),
                      total_equipo_medida=_append_total("- EQUIPO DE MEDIDA:", self.gasto_equipo_medida),
                      total_factura=_append_total("# TOTAL FACTURA", self.coste_total),
                      detalle_term_fijo=detalle_tfijo, detalle_iva=_append_total(detalle_iva, self.coste_iva),
                      detalle_term_variable='\n  '.join(detalle_tvar), detalle_term_impuesto_elec=detalle_impuesto)

        return TEMPLATE_FACTURA.format(**params)

    @staticmethod
    def _round(value, normal_round=True):
        # TODO refinar
        # print('debug_round: {:.4f} --> {:.4f}'.format(value, round(round(value, ROUND_PREC + 1), ROUND_PREC)))
        return round(value, ROUND_PREC)
        # if normal_round:
        #     return round(value, ROUND_PREC)
        # return round(round(value, ROUND_PREC + 1), ROUND_PREC)

    def _consumo_numerico(self):
        """
        Devuelve los datos de consumo y un booleano indicando si se trata de valores totales o es un pd.Series.
        :return: son_totales, consumo_kWh
        """
        if (type(self._consumo) is float) or (type(self._consumo) is int):
            return True, [float(self._consumo)]
        elif (type(self._consumo) is tuple) or (type(self._consumo) is list):
            # Establecidos consumos totales para cada periodo [P1, opc_P2, opc_P3]
            return True, self._consumo
        return False, self._consumo

    @staticmethod
    def _coste_tea_tcu(consumo, tcu, periodo_fac, tipo_peaje):
        """Devuelve TEA, TCU, CONSUMO como lista de tuplas por periodo de facturación.
        :return [(TEA_P1, TCU_P1, C_P1), (TEA_P2, TCU_P2, C_P2), ...]
        :rtype list
        """
        coefs_ener = TERM_ENER_PEAJE_ACCESO_EUR_KWH_TEA[periodo_fac][tipo_peaje]
        if len(coefs_ener) > 1:  # DISCRIMINACIÓN HORARIA
            name = consumo.name
            hay_discr, cons_discr = _asigna_periodos_discr_horaria(consumo, tipo_peaje)
            assert hay_discr
            assert tcu.index.equals(cons_discr.index)
            return [(cons_discr[cons_discr['P{}'.format(i + 1)]][name].sum() * coef,
                     (cons_discr[cons_discr['P{}'.format(i + 1)]][name] * tcu[cons_discr['P{}'.format(i + 1)]]).sum(),
                     cons_discr[cons_discr['P{}'.format(i + 1)]][name].sum())
                    for i, coef in enumerate(coefs_ener)]
        else:
            assert tcu.index.equals(consumo.index)
            return [(consumo.sum() * coefs_ener[0], (consumo * tcu).sum(), consumo.sum())]

    def _calcula_iva_y_total(self):
        """Añade el IVA y obtiene el total."""
        # Cálculo del IVA y TOTAL:
        subt_fijo_var = self._termino_fijo_total + self._termino_variable_total
        subt_fijo_var += self._termino_impuesto_electrico + self._descuento_bono_social
        _, _, impuesto_gen, impuesto_medida = DATOS_ZONAS_IMPUESTOS[self._zona_impuestos]
        # self._terminos_iva = (self._round(subt_fijo_var * impuesto_gen, normal_round=False),
        #                       self._round(self._termino_equipo_medida * impuesto_medida, normal_round=False))
        # self._termino_iva_total = self._terminos_iva[0] + self._terminos_iva[1]
        self._terminos_iva = (subt_fijo_var * impuesto_gen, self._termino_equipo_medida * impuesto_medida)
        self._termino_iva_total = self._round(self._terminos_iva[0] + self._terminos_iva[1])

        # TOTAL FACTURA:
        subt_fijo_var += self._termino_equipo_medida + self._termino_iva_total
        self._total_factura = subt_fijo_var

    def _calcula_factura(self):
        """Método para regenerar el cálculo de la factura eléctrica."""
        cod_tarifa = DATOS_TIPO_PEAJE[self._tipo_peaje][2]

        # Intervalos de facturación:
        year = self._t0.year
        year_f = self._tf.year
        self._num_dias_factura = (self._tf - self._t0).days  # t0 marca el siguiente inicio, por lo que no entra
        if year_f > year:
            # Cálculo de 2 tramos
            ts_limit = pd.Timestamp('{}-12-31'.format(year))
            days_1 = (ts_limit - self._t0).days
            days_2 = (self._tf - ts_limit).days
            n_days_y1 = (pd.Timestamp('{}-01-01'.format(year + 1)) - pd.Timestamp('{}-01-01'.format(year))).days
            n_days_y2 = (pd.Timestamp('{}-01-01'.format(year_f + 1)) - pd.Timestamp('{}-01-01'.format(year_f))).days
            self._periodos_fact = ((days_1, n_days_y1, year), (days_2, n_days_y2, year_f))
        else:
            n_days_y = (pd.Timestamp('{}-01-01'.format(year + 1)) - pd.Timestamp('{}-01-01'.format(year))).days
            self._periodos_fact = ((self._num_dias_factura, n_days_y, year),)

        # Aux: PVPC Data:
        if self._pvpc_data is None:
            pvpc_data = PVPC(update=True, verbose=False)
            self._pvpc_data = pvpc_calc_tcu_cp_feu_d(pvpc_data.data['data'], verbose=False, convert_kwh=True)
        cols_tarifa = list(filter(lambda x: cod_tarifa in x, self._pvpc_data.columns))
        pvpc_t_ini, pvpc_t_fin = self._t0 + pd.Timedelta('1D'), self._tf + pd.Timedelta('1D')
        self._pvpc_horario = self._pvpc_data[cols_tarifa].loc[pvpc_t_ini:pvpc_t_fin].iloc[:-1]

        # Cálculo del término fijo:
        self._termino_fijo, self._termino_fijo_total = [], 0
        for (days_fac, days_year, year) in self._periodos_fact:
            coef_potencia = MARGEN_COMERCIALIZACIÓN_EUR_KW_AÑO_MCF + TERM_POT_PEAJE_ACCESO_EUR_KW_AÑO_TPA[year]
            coste = self._potencia_contratada * days_fac * coef_potencia / days_year
            self._termino_fijo.append((coste, coef_potencia))
            self._termino_fijo_total += coste
        self._termino_fijo_total = self._round(self._termino_fijo_total)

        # Cálculo del término variable:
        if self._consumo is not None:
            son_totales, consumo_calc = self._consumo_numerico()
            if son_totales:
                # Estimación de consumo horario mediante aplicación de perfiles de consumo en el intervalo.
                c_coef = 'COF{}'.format(cod_tarifa)
                hay_discr, perfs_interv = _asigna_periodos_discr_horaria(self._pvpc_horario[c_coef], self._tipo_peaje)
                if not hay_discr:
                    self._consumo_horario = (perfs_interv * consumo_calc[0] / perfs_interv.sum()).rename('kWh')
                else:
                    consumos_horarios_periodos = []
                    for i, cons_periodo_i in enumerate(consumo_calc):
                        c = 'P{}'.format(i + 1)
                        idx = perfs_interv[perfs_interv[c]].index
                        consumos_horarios_periodos.append(perfs_interv.loc[idx, c_coef] * cons_periodo_i
                                                          / perfs_interv.loc[idx, c_coef].sum())
                    self._consumo_horario = pd.Series(pd.concat(consumos_horarios_periodos)).rename('kWh').sort_index()
            else:
                # Consumo horario real
                self._consumo_horario = consumo_calc

            col_tcu = 'TCU{}'.format(cod_tarifa)
            if len(self._periodos_fact) > 1:
                ts_limit = pd.Timestamp('{}-01-01'.format(self._tf.year)).tz_localize(self._consumo_horario.index.tz)
                consumo_1 = self._consumo_horario.loc[:ts_limit].iloc[:-1]
                consumo_2 = self._consumo_horario.loc[ts_limit:]
                pvpc_1 = self._pvpc_horario.loc[:ts_limit].iloc[:-1]
                pvpc_2 = self._pvpc_horario.loc[ts_limit:]
                tea_y1, tcu_y1, cons_tot_y1 = list(zip(*self._coste_tea_tcu(consumo_1, pvpc_1[col_tcu],
                                                                            self._t0.year, self._tipo_peaje)))
                tea_y2, tcu_y2, cons_tot_y2 = list(zip(*self._coste_tea_tcu(consumo_2, pvpc_2[col_tcu],
                                                                            self._tf.year, self._tipo_peaje)))
                self._coste_peaje_acceso_tea = (tea_y1, tea_y2)
                self._coste_ponderado_energia_tcu = (tcu_y1, tcu_y2)
                self._consumos_totales_por_periodo = (cons_tot_y1, cons_tot_y2)
                coste_variable_tot = (sum([sum(x) for x in self._coste_peaje_acceso_tea])
                                      + sum([sum(x) for x in self._coste_ponderado_energia_tcu]))
            else:
                tea, tcu, cons_tot = list(zip(*self._coste_tea_tcu(self._consumo_horario, self._pvpc_horario[col_tcu],
                                                                   self._t0.year, self._tipo_peaje)))
                self._coste_peaje_acceso_tea = tea
                self._coste_ponderado_energia_tcu = tcu
                self._consumos_totales_por_periodo = cons_tot
                coste_variable_tot = sum(self._coste_peaje_acceso_tea) + sum(self._coste_ponderado_energia_tcu)
        else:
            print_warn('No se ha definido ningún consumo energético')
            self._coste_peaje_acceso_tea = ((0.,),)
            self._coste_ponderado_energia_tcu = (0.,)
            coste_variable_tot = 0.
        self._termino_variable_total = self._round(coste_variable_tot)
        subt_fijo_var = self._termino_fijo_total + self._termino_variable_total

        # Cálculo de la bonificación (bono social):
        self._descuento_bono_social = 0.
        if self._con_bono_social:
            self._descuento_bono_social = self._round(-0.25 * subt_fijo_var)
            subt_fijo_var += self._descuento_bono_social

        # Cálculo del impuesto eléctrico:
        self._termino_impuesto_electrico = self._round(self._impuesto_electrico_general * subt_fijo_var,
                                                       normal_round=False)
        subt_fijo_var += self._termino_impuesto_electrico

        # Cálculo del equipo de medida:
        if self.alquiler_euros is not None:
            self._termino_equipo_medida = self._round(self.alquiler_euros)
        else:
            self._termino_equipo_medida = self._round(self._num_dias_factura * self.alquiler_euros_dia)

        # Cálculo del IVA o equivalente y del TOTAL:
        self._calcula_iva_y_total()

    @property
    def consumo_horario(self):
        """Devuelve los datos de consumo como time series horario. Si el consumo no tiene discriminación horaria,
        se aplican los perfiles de consumo para la tarifa seleccionada y el intervalo facturado,
        estimando los valores horarios."""
        return self._consumo_horario

    @property
    def pvpc_horas_periodo(self):
        """Devuelve el PVPC en el intervalo facturado.
        :return: pvpc €/kWh
        :rtype: pd.Series
        """
        # TODO revisar necesidad y si correcto
        return self._pvpc_horario

    @property
    def num_dias_factura(self):
        """Devuelve el # de días del periodo facturado."""
        return self._num_dias_factura

    @property
    def consumo_total(self):
        """Devuelve el consumo total del periodo facturado en kWh.
        :return consumo_kWh
        :rtype float

        """
        if self._consumo is not None:
            son_totales, consumo_calc = self._consumo_numerico()
            if son_totales:
                return sum(consumo_calc)
            return consumo_calc.sum()
        print_warn('No se ha definido ningún consumo energético')
        return 0.

    @consumo_total.setter
    def consumo_total(self, nuevo_consumo):
        """Establece el consumo energético del periodo de facturación en kWh.
        :param nuevo_consumo: Consumo en kWh, bien como float, bien como lista de 1, 2 o 3 elementos,
        bien como time series de datos horarios.
        """
        self._consumo = nuevo_consumo
        self._calcula_factura()

    @property
    def gasto_equipo_medida(self):
        """Devuelve el gasto relativo al alquiler de equipos de medida antes de impuestos, en €.
        :return gasto_alquiler
        :rtype float

        """
        return self._termino_equipo_medida

    @gasto_equipo_medida.setter
    def gasto_equipo_medida(self, nuevo_gasto):
        """Establece el gasto relativo al alquiler de equipos de medida antes de impuestos, en €, de forma absoluta.
        :param nuevo_gasto: Gasto en €
        """
        self.alquiler_euros = nuevo_gasto
        self._termino_equipo_medida = self._round(nuevo_gasto)
        # Re-Cálculo del IVA y TOTAL:
        self._calcula_iva_y_total()

    @property
    def coste_termino_fijo(self):
        """Calcula el coste del término de potencia antes de impuestos, en €.
        :return gasto_potencia
        :rtype float

        """
        return self._termino_fijo_total

    @property
    def coste_termino_consumo(self):
        """Calcula el coste asociado al consumo de energía en el periodo facturado, antes de impuestos, en €.
        :return gasto_energia
        :rtype float

        """
        return self._termino_variable_total

    @property
    def descuento_bono_social(self):
        """Calcula el importe del descuento por Bono Social, si lo hay, antes de impuestos, en €.
        :return descuento
        :rtype float

        """
        return self._descuento_bono_social

    @property
    def impuesto_electrico_general(self):
        """Calcula el importe del impuesto eléctrico, antes de IVA o equivalente, en €.
        :return impuesto
        :rtype float

        """
        return self._termino_impuesto_electrico

    @property
    def coste_iva(self):
        """Calcula el importe del IVA o equivalente, en €.
        :return impuesto
        :rtype float

        """
        return self._termino_iva_total

    @property
    def coste_total(self):
        """Calcula el importe total de la factura eléctrica, en €.
        :return coste
        :rtype float

        """
        return self._total_factura

    def generacion_csv_oficial_consumo_horario(self, save_pathdir=None):
        """
        Graba el consumo horario en CSV, con el formato utilizado por las distribuidoras (oficial de facto), para
        su importación en otras herramientas, como la existente en: https://facturaluz2.cnmc.es/facturaluz2.html

        El formato es el siguiente:
        ```
            CUPS;Fecha;Hora;Consumo_kWh;Metodo_obtencion
            ES00XXXXXXXXXXXXXXDB;06/09/2015;1;0,267;R
            ES00XXXXXXXXXXXXXXDB;06/09/2015;2;0,143;R
            ES00XXXXXXXXXXXXXXDB;06/09/2015;3;0,118;R
            ...
        ```
        :param save_pathdir: (OPC) path_str de destino para grabar el CSV.
        :return: dataframe de consumo con 'formato oficial'
        :rtype: pd.dataframe
        """
        serie_ch = pd.DataFrame(self._consumo_horario)

        columns = 'CUPS;Fecha;Hora;Consumo_kWh;Metodo_obtencion'.split(';')
        date_fmt = '{:%d/%m/%Y}'
        time_fmt = '{:%-H}'
        metodo_obt = 'R'
        serie_ch[columns[0]] = self._cups
        serie_ch[columns[1]] = [date_fmt.format(x) for x in serie_ch.index]
        serie_ch[columns[2]] = [int(time_fmt.format(x)) + 1 for x in serie_ch.index]
        serie_ch[columns[3]] = serie_ch[self._consumo_horario.name].round(3)
        serie_ch[columns[4]] = metodo_obt
        serie_ch.drop(self._consumo_horario.name, axis=1, inplace=True)

        if save_pathdir is not None:  # Export CSV to disk
            params_csv = dict(index=False, sep=';', decimal=',', float_format='%.3f')
            path_csv = os.path.join(os.path.expanduser(save_pathdir),
                                    'consumo_{:%Y_%m_%d}_to_{:%Y_%m_%d}.csv'.format(pd.Timestamp(self._t0), self._tf))
            serie_ch.to_csv(path_csv, **params_csv)
        return serie_ch


if __name__ == '__main__':
    def _check_results_factura(factura,
                               num_dias_factura, coste_termino_fijo, coste_termino_consumo, impuesto_electrico_general,
                               gasto_equipo_medida, coste_iva, coste_total):
        def _print_c(v1, v2):
            if v1 == v2:
                print_ok('{} == {}'.format(v1, v2))
            else:
                print_err('{} != {}'.format(v1, v2))

        repr_factura = str(factura)
        consumo_h = factura.consumo_horario
        factura.consumo_total = consumo_h
        print_warn(str(factura) == repr_factura)
        _print_c(round(factura.num_dias_factura, ROUND_PREC), num_dias_factura)
        _print_c(round(factura.coste_termino_fijo, ROUND_PREC), coste_termino_fijo)
        _print_c(round(factura.coste_termino_consumo, ROUND_PREC), coste_termino_consumo)
        _print_c(round(factura.impuesto_electrico_general, ROUND_PREC), impuesto_electrico_general)
        _print_c(round(factura.gasto_equipo_medida, ROUND_PREC), gasto_equipo_medida)
        _print_c(round(factura.coste_iva, ROUND_PREC), coste_iva)
        _print_c(round(factura.coste_total, ROUND_PREC), coste_total)
        assert all([round(factura.num_dias_factura, ROUND_PREC) == num_dias_factura,
                    round(factura.coste_termino_fijo, ROUND_PREC) == coste_termino_fijo,
                    round(factura.coste_termino_consumo, ROUND_PREC) == coste_termino_consumo,
                    round(factura.impuesto_electrico_general, ROUND_PREC) == impuesto_electrico_general,
                    round(factura.gasto_equipo_medida, ROUND_PREC) == gasto_equipo_medida,
                    round(factura.coste_iva, ROUND_PREC) == coste_iva,
                    round(factura.coste_total, ROUND_PREC) == coste_total])


    # t_0, t_f = '2016-11-01', '2017-01-05'
    # f1 = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_VHC, consumo=[219, 126, 154],
    #                  zona_impuestos=ZONA_IMPUESTOS_PENIN_BALEARES, alquiler_euros=1.62)
    # print_ok(f1)
    # _check_results_factura(f1, 65, 25.72, 53.31, 4.04, 1.62, 17.78, 102.47)
    #
    # f2 = FacturaElec(t_0, t_f, potencia_contratada=5, tipo_peaje=TIPO_PEAJE_GEN, consumo=[499], zona_impuestos=ZONA_IMPUESTOS_CANARIAS, con_bono_social=False, alquiler_euros=1.62)
    # print_yellow(f2)
    # _check_results_factura(f2, 65, 37.28, 63.68, 5.16, 1.62, 3.30, 111.04)
    #
    # f2_b = FacturaElec(t_0, t_f, potencia_contratada=5, tipo_peaje=TIPO_PEAJE_GEN, consumo=499, zona_impuestos=ZONA_IMPUESTOS_CANARIAS, con_bono_social=True, alquiler_euros=1.62)
    # _check_results_factura(f2_b, 65, 37.28, 63.68, 3.87, 1.62, 2.50, 83.71)
    # print_info(f2_b)

    t_0, t_f = '2016-11-01', '2016-12-09'

    # f3 = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_NOC, consumo=[219, 280], zona_impuestos=ZONA_IMPUESTOS_CEUTA_MELILLA, alquiler_euros=1.62)
    # print_info(f3)
    # _check_results_factura(f3, 38, 15.06, 51.89, 3.42, 1.62, 0.77, 72.76)
    # consumo_ofi = f3.generacion_csv_oficial_consumo_horario('~/Desktop')
    # print_info(consumo_ofi)

    f4 = FacturaElec(t_0, t_f, tipo_peaje=TIPO_PEAJE_VHC, consumo=[219, 126, 154], zona_impuestos=ZONA_IMPUESTOS_PENIN_BALEARES, alquiler_euros=1.62)
    print_warn(f4)
    _check_results_factura(f4, 38, 15.06, 51.76, 3.42, 1.62, 15.09, 86.95)

