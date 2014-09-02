# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Avanced Open Source Consulting
#    Copyright (C) 2011 - 2014 Avanzosc <http://www.avanzosc.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp.osv import orm, fields
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
import time
import datetime


class SimulationCost(orm.Model):
    _inherit = 'simulation.cost'

    def _end_date_ref(self, cr, uid, ids, name, args, context=None):
        res = {}
        for simulation_cost in self.browse(cr, uid, ids, context=context):
            if simulation_cost.start_date and simulation_cost.duration:
                if simulation_cost.duration > 0:
                    date = datetime.strptime(simulation_cost.start_date,
                                             '%Y-%m-%d')
                    new_date = (date +
                                relativedelta(months=simulation_cost.duration))
                    res[simulation_cost.id] = new_date.strftime('%Y-%m-%d')
        return res

    _columns = {
        # Fecha de inicio
        'start_date': fields.date('Start Date', required=True),
        # Duracion
        'duration': fields.integer('Duration'),
        # Fecha Fin
        'end_date': fields.function(_end_date_ref, method=True, type='date',
                                    string='End Date', store=True),
        # Previsiones
        'simulation_cost_prevision_ids':
            fields.one2many('simulation.cost.prevision', 'simulation_cost_id',
                            'Simulation Cost Previsions'),
        # Fecha Real de Firma
        'real_date_of_signature': fields.date('Real Date Of Signature'),
    }

    _defaults = {'start_date': lambda *a: time.strftime('%Y-%m-%d')
                 }

    def onchange_duration(self, cr, uid, ids, start_date, duration,
                          context=None):
        res = {}
        if start_date and duration:
            if duration > 0:
                date = datetime.strptime(start_date, '%Y-%m-%d')
                new_date = date + relativedelta(months=duration)
                res.update({'end_date': new_date.strftime('%Y-%m-%d')})
        return {'value': res}

    def button_load(self, cr, uid, ids, context=None):
        previsions_obj = self.pool['simulation.cost.prevision']
        cost_line_obj = self.pool['simulation.cost.line']
        # Leo el Objeto Simulación de coste
        simulation_cost = self.browse(cr, uid, ids[0], context)
        # Valido que haya introducido la fecha
        if not simulation_cost.start_date:
            raise orm.except_orm(_('Prevision Error'),
                                 _('Start Date No defined'))
        if not simulation_cost.duration:
            raise orm.except_orm(_('Prevision Error'),
                                 _('No defined month duration'))
        if simulation_cost.duration < 1:
            raise orm.except_orm(_('Prevision Error'),
                                 _('Months duration must be greater than 1'))
        # Borro las lines de prevision
        cond = [('simulation_cost_id', '=', simulation_cost.id)]
        previsions_ids = previsions_obj.search(cr, uid, cond, context)
        previsions_obj.unlink(cr, uid, previsions_ids)
        # Calculo los meses
        w_months = 0
        # Trato las lineas de otros
        for others_cost_lines_id in simulation_cost.others_cost_lines_ids:
            cost_line = cost_line_obj.browse(
                cr, uid, others_cost_lines_id.id, context)
            delay = (cost_line.month_start_cost + cost_line.month_duration +
                     cost_line.delay_cost - simulation_cost.duration)
            sale_delay = (cost_line.month_start_sale + cost_line.sale_duration
                          + cost_line.delay_sale - simulation_cost.duration)
            if delay > 0:
                if delay > w_months:
                    w_months = delay
            if sale_delay > 0:
                if sale_delay > w_months:
                    w_months = sale_delay
        simcost = simulation_cost
        for amortization_cost_lines_id in simcost.amortization_cost_lines_ids:
            cost_line = cost_line_obj.browse(
                cr, uid, amortization_cost_lines_id.id, context)
            delay = (cost_line.month_start_cost + cost_line.month_duration +
                     cost_line.delay_cost - simulation_cost.duration)
            sale_delay = (cost_line.month_start_sale + cost_line.sale_duration
                          + cost_line.delay_sale - simulation_cost.duration)
            if delay > 0:
                if delay > w_months:
                    w_months = delay
            if sale_delay > 0:
                if sale_delay > w_months:
                    w_months = sale_delay
        # Calculo los meses, y creo una tabla con ellos
        w_total_months = simulation_cost.duration + w_months
        # Creo una tabla con un elemento por cada mes
        month_datas = {}
        for numero in range(1, w_total_months + 1):
            date = (datetime.strptime(simulation_cost.start_date, '%Y-%m-%d') +
                    relativedelta(months=1))
            month_datas[(numero)] = {'month': numero,
                                     'period_date': date,
                                     'costs_amount_month': 0,
                                     'payment_prevision_month': 0,
                                     'sales_amount_month': 0,
                                     'charge_prevision_month': 0,
                                     }
        # Realizo los calculos para las lineas de otros
        for others_cost_lines_id in simulation_cost.others_cost_lines_ids:
            cost_line = cost_line_obj.browse(
                cr, uid, others_cost_lines_id.id, context)
            # Calculo el coste en el mes
            if cost_line.month_duration:
                w_months = cost_line.month_duration
                if w_months >= 1:
                    w_importe = ((cost_line.subtotal_purchase +
                                  cost_line.amortization_cost +
                                  cost_line.indirect_cost) / w_months)
                    w_mes = cost_line.month_start_cost
                    for numero in range(1, w_months+1):
                        for data in month_datas:
                            dat = month_datas[data]
                            month = dat['month']
                            if w_mes == month:
                                costs_amount_month = dat['costs_amount_month']
                                costs_amount_month = (costs_amount_month +
                                                      w_importe)
                                vals = {'costs_amount_month':
                                        costs_amount_month}
                                month_datas[data].update(vals)
                        w_mes = w_mes + 1
                    # Calculo la prevision de pago en el mes
                    # if cost_line.delay_cost:
                    w_mes = cost_line.month_start_cost + cost_line.delay_cost
                    for numero in range(1, w_months + 1):
                        for data in month_datas:
                            dat = month_datas[data]
                            month = dat['month']
                            if w_mes == month:
                                prev_month = dat['payment_prevision_month']
                                prev_month = prev_month + w_importe
                                vals = {'payment_prevision_month': prev_month}
                                month_datas[data].update(vals)
                        w_mes = w_mes + 1
            # Calculo las ventas en el mes
            if cost_line.sale_duration:
                w_months = cost_line.sale_duration
                if w_months >= 1:
                    w_importe = cost_line.subtotal_sale / w_months
                    w_mes = cost_line.month_start_sale
                    for numero in range(1, w_months+1):
                        for data in month_datas:
                            dat = month_datas[data]
                            month = dat['month']
                            if w_mes == month:
                                sales_amount_month = dat['sales_amount_month']
                                sales_amount_month = (sales_amount_month +
                                                      w_importe)
                                vals = {'sales_amount_month':
                                        sales_amount_month}
                                month_datas[data].update(vals)
                        w_mes = w_mes + 1
                    # Calculo la prevision de cobro en el mes
                    w_mes = cost_line.month_start_sale+cost_line.delay_sale
                    for numero in range(1, w_months+1):
                        for data in month_datas:
                            dat = month_datas[data]
                            month = dat['month']
                            if w_mes == month:
                                prevision_month = dat['charge_prevision_month']
                                prevision_month = (prevision_month +
                                                   w_importe)
                                vals = {'charge_prevision_month':
                                        prevision_month}
                                month_datas[data].update(vals)
                        w_mes = w_mes + 1

        simcos = simulation_cost
        for amortization_cost_lines_id in simcos.amortization_cost_lines_ids:
            cost_line = cost_line_obj.browse(
                cr, uid, amortization_cost_lines_id.id, context)
            # Calculo el coste en el mes
            if cost_line.month_duration:
                w_months = cost_line.month_duration
                if w_months >= 1:
                    w_importe = (cost_line.subtotal_purchase) / w_months
                    w_mes = cost_line.month_start_cost
                    for numero in range(1, w_months+1):
                        for data in month_datas:
                            dat = month_datas[data]
                            month = dat['month']
                            if w_mes == month:
                                costs_amount_month = dat['costs_amount_month']
                                costs_amount_month = (costs_amount_month +
                                                      w_importe)
                                vals = {'costs_amount_month':
                                        costs_amount_month}
                                month_datas[data].update(vals)
                        w_mes = w_mes + 1
                    # Calculo la prevision de pago en el mes
                    w_mes = cost_line.month_start_cost+cost_line.delay_cost
                    for numero in range(1, w_months+1):
                        for data in month_datas:
                            dat = month_datas[data]
                            month = dat['month']
                            if w_mes == month:
                                previsionm = dat['payment_prevision_month']
                                previsionm = previsionm + w_importe
                                vals = {'payment_prevision_month':
                                        previsionm}
                                month_datas[data].update(vals)
                        w_mes = w_mes + 1
            # Calculo las ventas en el mes
            if cost_line.sale_duration:
                w_months = cost_line.sale_duration
                if w_months >= 1:
                    w_importe = cost_line.subtotal_sale / w_months
                    w_mes = cost_line.month_start_sale
                    for numero in range(1, w_months+1):
                        for data in month_datas:
                            dat = month_datas[data]
                            month = dat['month']
                            if w_mes == month:
                                sales_amount_month = dat['sales_amount_month']
                                sales_amount_month = (sales_amount_month +
                                                      w_importe)
                                vals = {'sales_amount_month':
                                        sales_amount_month}
                                month_datas[data].update(vals)
                        w_mes = w_mes + 1
                    # Calculo la prevision de cobro en el mes
                    w_mes = cost_line.month_start_sale+cost_line.delay_sale
                    for numero in range(1, w_months+1):
                        for data in month_datas:
                            dat = month_datas[data]
                            month = dat['month']
                            if w_mes == month:
                                prevision_month = dat['charge_prevision_month']
                                prevision_month = prevision_month + w_importe
                                vals = {'charge_prevision_month':
                                        prevision_month}
                                month_datas[data].update(vals)
                        w_mes = w_mes + 1
        # Calculo totales de costes, y prevision de pago
        w_total_sales_amount_month = 0.0
        w_total_charge_prevision_month = 0.0
        for data in month_datas:
            dat = month_datas[data]
            month = dat['month']
            sales_amount_month = dat['sales_amount_month']
            charge_prevision_month = dat['charge_prevision_month']
            w_total_sales_amount_month = (w_total_sales_amount_month +
                                          sales_amount_month)
            w_total_charge_prevision_month = (w_total_charge_prevision_month +
                                              charge_prevision_month)
        # Doy de alta las previsiones
        for data in month_datas:
            dat = month_datas[data]
            month = dat['month']
            costs_amount_month = dat['costs_amount_month']
            payment_prevision_month = dat['payment_prevision_month']
            sales_amount_month = dat['sales_amount_month']
            charge_prevision_month = dat['charge_prevision_month']
            percentage_invoice = 0
            percentage_charge = 0
            if sales_amount_month > 0:
                percentage_invoice = ((sales_amount_month * 100) /
                                      w_total_sales_amount_month)
            if charge_prevision_month > 0:
                percentage_charge = ((charge_prevision_month * 100) /
                                     w_total_charge_prevision_month)
            date = (datetime.strptime(simulation_cost.start_date, '%Y-%m-%d') +
                    relativedelta(months=month-1))
            date_string = str(date.year) + '/' + str(date.month)
            line_vals = {'simulation_cost_id': simulation_cost.id,
                         'month': month,
                         'period_date': date_string,
                         'costs_amount_month': costs_amount_month,
                         'payment_prevision_month': payment_prevision_month,
                         'sales_amount_month': sales_amount_month,
                         'charge_prevision_month': charge_prevision_month,
                         'percentage_invoice': percentage_invoice,
                         'percentage_charge': percentage_charge,
                         }
            previsions_obj.create(cr, uid, line_vals, context)
        return True

    # BOTÓN COPIAR UNA SIMULACION DE COSTES
    def button_copy_cost_simulation(self, cr, uid, ids, context=None):
        cost_line_obj = self.pool['simulation.cost.line']
        prevision_obj = self.pool['simulation.cost.prevision']
        # Leo el Objeto Simulación de coste
        simulation_cost = self.browse(cr, uid, ids[0], context)
        # Creo la nueva simulacion de costes
        line_vals = {'name': simulation_cost.name,
                     'overhead_costs': simulation_cost.overhead_costs,
                     'start_date': simulation_cost.start_date,
                     'duration': simulation_cost.duration,
                     'end_date': simulation_cost.end_date,
                     'subtotal5t_purchase':
                     simulation_cost.subtotal5t_purchase,
                     'subtotal5t_sale': simulation_cost.subtotal5t_sale,
                     'benefit5t': simulation_cost.benefit5t,
                     'total_costs': simulation_cost.total_costs,
                     'total_sales': simulation_cost.total_sales,
                     'total_benefits': simulation_cost.total_benefits,
                     'total_amortizations':
                     simulation_cost.total_amortizations,
                     'total_indirects': simulation_cost.total_indirects,
                     'total_amort_indirects':
                     simulation_cost.total_amort_indirects,
                     'total_overhead_costs':
                     simulation_cost.total_overhead_costs,
                     'total': simulation_cost.total,
                     'net_cost': simulation_cost.net_cost,
                     'net_cost_percentage':
                     simulation_cost.net_cost_percentage,
                     'gross_margin': simulation_cost.gross_margin,
                     'gross_margin_percentage':
                     simulation_cost.gross_margin_percentage,
                     'contribution_margin':
                     simulation_cost.contribution_margin,
                     'contribution_margin_percentage':
                     simulation_cost.contribution_margin_percentage,
                     'net_margin': simulation_cost.net_margin,
                     'net_margin_percentage':
                     simulation_cost.net_margin_percentage,
                     'state': simulation_cost.state,
                     'department_id': simulation_cost.department_id.id,
                     'crm_case_resource_type_id':
                     simulation_cost.crm_case_resource_type_id.id,
                     'project_type_id': simulation_cost.project_type_id.id,
                     'subsector_id': simulation_cost.subsector_id.id,
                     'project_activity_id':
                     simulation_cost.project_activity_id.id,
                     'project_subactivity_id':
                     simulation_cost.project_subactivity_id.id,
                     'administration_id': simulation_cost.administration_id.id,
                     'type_program_id': simulation_cost.type_program_id.id,
                     'project_research_line_id':
                     simulation_cost.project_research_line_id.id,
                     'project_research_subline_id':
                     simulation_cost.project_research_subline_id.id,
                     'project_pyramid_test_id':
                     simulation_cost.project_pyramid_test_id.id,
                     'project_aeronautical_program_id':
                     simulation_cost.project_aeronautical_program_id.id,
                     'project_location_id':
                     simulation_cost.project_location_id.id,
                     'subsector_id': simulation_cost.subsector_id.id,
                     'sector_id': simulation_cost.sector_id.id,
                     'resume': simulation_cost.resume,
                     'project_id': simulation_cost.project_id,
                     'deductible_iva': simulation_cost.deductible_iva
                     }
        simulation_cost_id = self.create(cr, uid, line_vals, context)
        # Copio las lineas de otros
        for cost_line in cost_line_obj.browse(
                cr, uid, simulation_cost.others_cost_lines_ids, context):
            line_vals = {'simulation_cost_id': simulation_cost_id,
                         'product_id': cost_line.product_id.id,
                         'name': cost_line.name,
                         'description': cost_line.description,
                         'supplier_id': cost_line.supplier_id.id,
                         'purchase_price': cost_line.purchase_price,
                         'uom_id': cost_line.uom_id.id,
                         'amount': cost_line.amount,
                         'product_sale_id': cost_line.product_sale_id.id,
                         'sale_amount': cost_line.sale_amount,
                         'sale_price': cost_line.sale_price,
                         'estimated_margin': cost_line.estimated_margin,
                         'estimated_date_purchase_completion':
                         cost_line.estimated_date_purchase_completion,
                         'amortization_rate': cost_line.amortization_rate,
                         'amortization_cost': cost_line.amortization_cost,
                         'indirect_cost_rate': cost_line.indirect_cost_rate,
                         'indirect_cost': cost_line.indirect_cost,
                         'type_cost': cost_line.type_cost,
                         'type2': cost_line.type2,
                         'type3': cost_line.type3,
                         'template_id': cost_line.template_id.id,
                         'month_start_cost': cost_line.month_start_cost,
                         'month_end_cost': cost_line.month_end_cost,
                         'delay_cost': cost_line.delay_cost,
                         'month_start_sale': cost_line.month_start_sale,
                         'month_end_sale': cost_line.month_end_sale,
                         'delay_sale': cost_line.delay_sale,
                         'month_duration': cost_line.month_duration,
                         'sale_duration': cost_line.sale_duration,
                         'margin_percent': cost_line.margin_percent,
                         'stage': cost_line.stage,
                         }
            cost_line_obj.create(cr, uid, line_vals, context)

        for cost_line in cost_line_obj.browse(
                cr, uid, simulation_cost.amortization_cost_lines_ids, context):
            line_vals = {'simulation_cost_id': simulation_cost_id,
                         'product_id': cost_line.product_id.id,
                         'name': cost_line.name,
                         'description': cost_line.description,
                         'supplier_id': cost_line.supplier_id.id,
                         'purchase_price': cost_line.purchase_price,
                         'uom_id': cost_line.uom_id.id,
                         'amount': cost_line.amount,
                         'product_sale_id': cost_line.product_sale_id.id,
                         'sale_amount': cost_line.sale_amount,
                         'sale_price': cost_line.sale_price,
                         'estimated_margin': cost_line.estimated_margin,
                         'estimated_date_purchase_completion':
                         cost_line.estimated_date_purchase_completion,
                         'amortization_rate': cost_line.amortization_rate,
                         'amortization_cost': cost_line.amortization_cost,
                         'indirect_cost_rate': cost_line.indirect_cost_rate,
                         'indirect_cost': cost_line.indirect_cost,
                         'type_cost': cost_line.type_cost,
                         'type2': cost_line.type2,
                         'type3': cost_line.type3,
                         'template_id': cost_line.template_id.id,
                         'month_start_cost': cost_line.month_start_cost,
                         'month_end_cost': cost_line.month_end_cost,
                         'delay_cost': cost_line.delay_cost,
                         'month_start_sale': cost_line.month_start_sale,
                         'month_end_sale': cost_line.month_end_sale,
                         'delay_sale': cost_line.delay_sale,
                         'month_duration': cost_line.month_duration,
                         'sale_duration': cost_line.sale_duration,
                         'margin_percent': cost_line.margin_percent,
                         'stage': cost_line.stage,
                         }
            cost_line_obj.create(cr, uid, line_vals, context)
        # Copio las lineas de previsiones
        for prevision in prevision_obj.browse(
                cr, uid, simulation_cost.simulation_cost_prevision_ids,
                context):
            line_vals = {'simulation_cost_id': simulation_cost_id,
                         'month': prevision.month,
                         'period_date': prevision.period_date,
                         'costs_amount_month': prevision.costs_amount_month,
                         'payment_prevision_month':
                         prevision.payment_prevision_month,
                         'percentage_invoice': prevision.percentage_invoice,
                         'percentage_charge': prevision.percentage_charge,
                         'sales_amount_month': prevision.sales_amount_month,
                         'charge_prevision_month':
                         prevision.charge_prevision_month,
                         }
            prevision_obj.create(cr, uid, line_vals, context)
        value = {'view_type': 'form',
                 'view_mode': 'form,tree',
                 'res_model': 'simulation.cost',
                 'res_id': simulation_cost_id,
                 'context': context,
                 'type': 'ir.actions.act_window',
                 'nodestroy': True
                 }
        return value

    # BOTÓN PARA CARGAR FECHAS EN LINES DE SIMULACION DE COSTE
    def button_charge_dates(self, cr, uid, ids, context=None):
        # Leo el Objeto Simulación de coste
        simulation_cost = self.browse(cr, uid, ids[0], context)
        if simulation_cost.real_date_of_signature:
            self._charge_dates_in_simulation_cost_lines(
                cr, uid, simulation_cost,
                simulation_cost.real_date_of_signature, context)
        else:
            if simulation_cost.start_date:
                self._charge_dates_in_simulation_cost_lines(
                    cr, uid, simulation_cost, simulation_cost.start_date,
                    context)
        return True

    # Función para cambiar la fecha de la linea de simulacion de costes.
    def _charge_dates_in_simulation_cost_lines(self, cr, uid, simulation_cost,
                                               simulation_date, context=None):
        coste_line_obj = self.pool['simulation.cost.line']
        # Trato las lineas de OTHERS
        for coste_line_id in simulation_cost.others_cost_lines_ids:
            diff = coste_line_id.month_start_cost - 1
            date = (datetime.strptime(simulation_date, "%Y-%m-%d") +
                    relativedelta(months=diff))
            vals = {'estimated_date_purchase_completion': date}
            coste_line_obj.write(cr, uid, [coste_line_id.id], vals, context)
        # Trato las lineas de AMORTIZATIONS I+D
        for coste_line_id in simulation_cost.amortization_cost_lines_ids:
            diff = coste_line_id.month_start_cost - 1
            date = (datetime.strptime(simulation_date, "%Y-%m-%d") +
                    relativedelta(months=diff))
            vals = {'estimated_date_purchase_completion': date}
            coste_line_obj.write(cr, uid, [coste_line_id.id], vals, context)
        return True
