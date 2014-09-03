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
from openerp.addons import decimal_precision as dp
from openerp.tools.translate import _
from openerp import workflow
import time


class SimulationCost(orm.Model):
    _inherit = 'simulation.cost'

    _columns = {
        # Campo para saber a que proyecto pertenece la simulación
        'project_id': fields.many2one('project.project', 'Project',
                                      readonly=True),
        # Campo para relacionar la Simulación de Costes con departamentos
        'department_id': fields.many2one('hr.department', 'Department',
                                         select=1),
        # Campo para relacionar la Simulación de Costes con campañas
        'crm_case_resource_type_id': fields.many2one('crm.tracking.campaign',
                                                     'Campaign', select=1),
        # Campo para relacionar la Simulación de Costes con tipos de proyectos
        'project_type_id': fields.many2one('project.type', 'Project Type',
                                           select=1, required=True),
        # Campo para relacionar la Simulación de Costes con tipos de proyectos
        'subsector_id': fields.many2one('subsector', 'Subsector', select=1),
        # Campo para relacionar la Simulación de Costes con Oportunidades
        'crm_opportunity_id': fields.many2one('crm.lead', 'Opportunity'),
        # Campo para saber el proyecto con que actividad esta relacionado
        'project_activity_id': fields.many2one('project.activity', 'Activity',
                                               select=1),
        # Campo para saber el proyecto con que subactividad esta relacionado
        'project_subactivity_id': fields.many2one('project.subactivity',
                                                  'Subactivity', select=1),
        # Campo para saber el proyecto con que administracion esta relacionado
        'administration_id': fields.many2one('administration',
                                             'Administration', select=1),
        # Campo para saber el proyecto con que tipo de programa esta
        # relacionado
        'type_program_id': fields.many2one('type.program', 'Call', select=1),
        # Campo para saber el proyecto con que línea de investigación esta
        # relacionado
        'project_research_line_id': fields.many2one('project.research.line',
                                                    'Line', select=1),
        # Campo para saber el proyecto con que sublínea de investigación esta
        # relacionado
        'project_research_subline_id':
            fields.many2one('project.research.subline', 'Subline', select=1),
        # Campo para saber el proyecto con que pirámide de ensayo esta
        # relacionado
        'project_pyramid_test_id': fields.many2one('project.pyramid.test',
                                                   'Pyramid Test', select=1),
        # Campo para saber el proyecto con que cliente final esta relacionado
        'final_partner_id': fields.many2one('res.partner', 'Final Customer'),
        # Campo para saber el proyecto con que programa aeronautico esta
        # relacionado
        'project_aeronautical_program_id':
            fields.many2one('project.aeronautical.program',
                            'Aeronautical Program', select=1),
        # Campo para saber la ubicación del proyecto
        'project_location_id': fields.many2one('project.location',
                                               'Location', select=1),
        'resume': fields.text('Resume'),
        'sector_id': fields.many2one('sector', 'Sector', select=1),
        'amortization_cost_lines_ids':
            fields.one2many('simulation.cost.line', 'simulation_cost_id',
                            'Amortization I+D Lines',
                            domain=[('type_cost', '=', 'Amortization')],
                            attrs={'readonly': [('historical_ok', '=',
                                                 True)]}),
        'subtotal6_purchase':
            fields.float('Total Purchase', readonly=True,
                         digits_compute=dp.get_precision('Purchase Price')),
        'subtotal6_sale':
            fields.float('Total Sale', readonly=True,
                         digits_compute=dp.get_precision('Purchase Price')),
        'benefit6':
            fields.float('Total Benefit', readonly=True,
                         digits_compute=dp.get_precision('Purchase Price')),
        'subtotal6t_purchase':
            fields.float('Amortizations R&D', readonly=True,
                         digits_compute=dp.get_precision('Purchase Price')),
        'subtotal6t_sale':
            fields.float('Total Amortizations R&D', readonly=True,
                         digits_compute=dp.get_precision('Purchase Price')),
        'benefit6t':
            fields.float('Amortizations R&D Benefit', readonly=True,
                         digits_compute=dp.get_precision('Purchase Price')),
        # WORKFLOW DE LA SIMULACION DEL COSTE
        'state': fields.selection([('draft', 'Draft'),
                                   ('financing', 'Financing'),
                                   ('open', 'Open'),
                                   ('inmodif_budgetary',
                                    'In Budgetary Modification'),
                                   ('closed', 'Closed'),
                                   ('accepted', 'Accepted'),
                                   ('canceled', 'Canceled'),
                                   ], 'State', readonly=True),
        # IVA DEDUCIBLE
        'deductible_iva': fields.boolean('Deductible IVA'),
        # Financiacion Proyectos
        'financing_source_ids':
            fields.one2many('project.financing', 'simulation_cost_id',
                            'Financing Sources'),
        # Lineas de Simulacion que tienen un fondo financiador propio
        'project_financing_lines_ids':
            fields.one2many('simulation.cost.line', 'simulation_cost_id',
                            'Lines with Financing Source',
                            domain=[('project_financing_id', '!=', False)],
                            readonly=True),
        # Categorias asociadas a la simulacion de coste
        'expense_area_ids':
            fields.many2many('expense.area', 'simucost_expensearea_rel',
                             'simulation_cost_id', 'expense_area_id',
                             'Expense Areas'),
        # Campo para saber si hay que generar estructura analitica por lineas
        'generate_by_lines': fields.boolean('Generate By Lines'),
        # Categorias Permitidas/Excluidas en la simulacion
        'simulation_category_ids':
            fields.one2many('simulation.category', 'simulation_cost_id',
                            'Categories',
                            attrs={'readonly': [('historical_ok', '=',
                                                 True)]}),
        # Usar Proyecto
        'use_project_id': fields.many2one('project.project', 'Use Project'),
        # Proyecto Padre
        'parent_project_id':
            fields.many2one('project.project', 'Parent Project'),
    }

    def default_get(self, cr, uid, fields, context=None):
        sequence_obj = self.pool['ir.sequence']
        sequence = sequence_obj.get(cr, uid, 'cost.serial')
        serial = sequence[0]
        res = super(SimulationCost, self).default_get(cr, uid, fields,
                                                      context=context)
        res.update({'simulation_number': serial})
        return res

    def unlink(self, cr, uid, ids, context=None):
        project_financing_obj = self.pool['project.financing']
        project_obj = self.pool['project.project']
        account_analytic_account_obj = self.pool['account.analytic.account']
        analytic_line_obj = self.pool['account.analytic.line']
        for cost in self.browse(cr, uid, ids, context):
            if cost.sale_order_ids:
                raise orm.except_orm(_('Invalid action !'),
                                     _('This Simulation Costs Have Associated '
                                       'Sales Orders'))
            # Borro los fondos financiadores asociados a las lineas de
            # simulacion
            for line in cost.others_cost_lines_ids:
                if line.project_financing_id:
                    project_financing_obj.unlink(
                        cr, uid, line.project_financing_id.id, context=context)
            for line in cost.amortization_cost_lines_ids:
                if line.project_financing_id:
                    project_financing_obj.unlink(
                        cr, uid, line.project_financing_id.id, context=context)
            # Borro el proyecto, cuenta analitica, y apuntes contables
            # Borro Proyecto y Cuenta Analítica  SOLO SI NO HAY use_project
            if cost.project_id:
                if not cost.use_project_id:
                    account_id = cost.project_id.analytic_account_id.id
                    project_obj.unlink(cr, uid, [cost.project_id.id],
                                       context=context)
                    account_analytic_account_obj.unlink(cr, uid, [account_id],
                                                        context=context)
                else:
                    # Borro las líneas de analitica para esta simulacion
                    cond = [('simulation_cost_id', '=', cost.id)]
                    analytic_line_ids = analytic_line_obj.search(
                        cr, uid, cond, context=context)
                    if analytic_line_ids:
                        analytic_line_obj.unlink(
                            cr, uid, analytic_line_ids, context=context)
        return super(SimulationCost, self).unlink(cr, uid, ids,
                                                  context=context)

    def button_copy_cost_simulation(self, cr, uid, ids, context=None):
        simuline_obj = self.pool['simulation.cost.line']
        # Leo el Objeto Simulación de coste
        simu = self.browse(cr, uid, ids[0])
        # Creo la nueva simulacion de costes
        margin_percentage = simu.contribution_margin_percentage
        resource_type_id = simu.crm_case_resource_type_id.id
        research_line_id = simu.project_research_line_id.id
        research_subline_id = simu.project_research_subline_id.id
        pyramid_test_id = simu.project_pyramid_test_id.id
        aeroprogram_id = simu.project_aeronautical_program_id.id
        line_vals = {'name': simu.name,
                     'overhead_costs': simu.overhead_costs,
                     'subtotal5_purchase': simu.subtotal5_purchase,
                     'subtotal5_sale': simu.subtotal5_sale,
                     'benefit5': simu.benefit5,
                     'subtotal5t_purchase': simu.subtotal5t_purchase,
                     'subtotal5t_sale': simu.subtotal5t_sale,
                     'benefit5t': simu.benefit5t,
                     'total_costs': simu.total_costs,
                     'total_sales': simu.total_sales,
                     'total_benefits': simu.total_benefits,
                     'total_amortizations': simu.total_amortizations,
                     'total_indirects': simu.total_indirects,
                     'total_amort_indirects': simu.total_amort_indirects,
                     'total_overhead_costs': simu.total_overhead_costs,
                     'total': simu.total,
                     'net_cost': simu.net_cost,
                     'net_cost_percentage': simu.net_cost_percentage,
                     'gross_margin': simu.gross_margin,
                     'gross_margin_percentage': simu.gross_margin_percentage,
                     'contribution_margin': simu.contribution_margin,
                     'contribution_margin_percentage': margin_percentage,
                     'net_margin': simu.net_margin,
                     'net_margin_percentage': simu.net_margin_percentage,
                     'state': simu.state,
                     'department_id': simu.department_id.id,
                     'crm_case_resource_type_id': resource_type_id,
                     'project_type_id': simu.project_type_id.id,
                     'subsector_id': simu.subsector_id.id,
                     'project_activity_id': simu.project_activity_id.id,
                     'project_subactivity_id': simu.project_subactivity_id.id,
                     'administration_id': simu.administration_id.id,
                     'type_program_id': simu.type_program_id.id,
                     'project_research_line_id': research_line_id,
                     'project_research_subline_id': research_subline_id,
                     'project_pyramid_test_id': pyramid_test_id,
                     'project_aeronautical_program_id': aeroprogram_id,
                     'project_location_id': simu.project_location_id.id,
                     'subsector_id': simu.subsector_id,
                     'sector_id': simu.sector_id,
                     'resume': simu.resume,
                     'project_id': simu.project_id.id,
                     'deductible_iva': simu.deductible_iva
                     }
        simu_id = self.create(cr, uid, line_vals, context=context)
        # Copio las lineas de otros
        for cost_line in simuline_obj.browse(
                cr, uid, simu.others_cost_lines_ids, context):
            date = cost_line.estimated_date_purchase_completion
            line_vals = {'simu_id': simu_id,
                         'product_id': cost_line.product_id.id,
                         'name': cost_line.name,
                         'description': cost_line.description,
                         'supplier_id': cost_line.supplier_id.id,
                         'purchase_price': cost_line.purchase_price,
                         'uom_id': cost_line.uom_id.id,
                         'amount': cost_line.amount,
                         'product_sale_id': cost_line.product_sale_id.id,
                         'sale_price': cost_line.sale_price,
                         'estimated_margin': cost_line.estimated_margin,
                         'estimated_date_purchase_completion': date,
                         'amortization_rate': cost_line.amortization_rate,
                         'amortization_cost': cost_line.amortization_cost,
                         'indirect_cost_rate': cost_line.indirect_cost_rate,
                         'indirect_cost': cost_line.indirect_cost,
                         'type_cost': cost_line.type_cost,
                         'type2': cost_line.type2,
                         'type3': cost_line.type3,
                         'template_id': cost_line.template_id.id,
                         'month_duration': cost_line.month_duration,
                         'sale_duration': cost_line.sale_duration,
                         'margin_percent': cost_line.margin_percent,
                         'stage': cost_line.stage,
                         }
            simuline_obj.create(cr, uid, line_vals, context)
        # Copio las lineas de Amortizaciones I+D
        for cost_line in simuline_obj.browse(
                cr, uid, simu.amortization_cost_lines_ids, context):
            date = cost_line.estimated_date_purchase_completion
            line_vals = {'simu_id': simu_id,
                         'product_id': cost_line.product_id.id,
                         'name': cost_line.name,
                         'description': cost_line.description,
                         'supplier_id': cost_line.supplier_id.id,
                         'purchase_price': cost_line.purchase_price,
                         'uom_id': cost_line.uom_id.id,
                         'amount': cost_line.amount,
                         'product_sale_id': cost_line.product_sale_id.id,
                         'sale_price': cost_line.sale_price,
                         'estimated_margin': cost_line.estimated_margin,
                         'estimated_date_purchase_completion': date,
                         'amortization_rate': cost_line.amortization_rate,
                         'amortization_cost': cost_line.amortization_cost,
                         'indirect_cost_rate': cost_line.indirect_cost_rate,
                         'indirect_cost': cost_line.indirect_cost,
                         'type_cost': cost_line.type_cost,
                         'type2': cost_line.type2,
                         'type3': cost_line.type3,
                         'template_id': cost_line.template_id.id,
                         'month_duration': cost_line.month_duration,
                         'sale_duration': cost_line.sale_duration,
                         'margin_percent': cost_line.margin_percent,
                         'stage': cost_line.stage,
                         }
            simuline_obj.create(cr, uid, line_vals, context)
        value = {'view_type': 'form',
                 'view_mode': 'form,tree',
                 'res_model': 'simulation.cost',
                 'res_id': simu_id,
                 'context': context,
                 'type': 'ir.actions.act_window',
                 'nodestroy': True
                 }
        return value

    def button_recalculation(self, cr, uid, ids, *args):
        simuline_obj = self.pool['simulation.cost.line']
        # Leo el Objeto Coste
        simulation_cost = self.browse(cr, uid, ids[0])
        # valido que no esté historificado ya
        if simulation_cost.historical_ok:
            raise orm.except_orm(_('This cost simulation have Historical'))
        subtotal_others_costs = 0.0
        subtotal_others_sales = 0.0
        subtotal_others_benefit = 0.0
        subtotal_amortization_costs = 0.0
        subtotal_amortization_sales = 0.0
        subtotal_amortization_benefit = 0.0
        total_costs = 0.0
        total_sales = 0.0
        total_benefit = 0.0
        total_amortizations = 0.0
        total_indirects = 0.0
        total_amort_indirects = 0.0
        subtotal_net_cost = 0.0
        subtotal_gross_margin = 0.0
        subtotal_contribution_margin = 0.0
        subtotal_net_margin = 0.0
        total_net_cost = 0.0
        total_gross_margin = 0.0
        total_contribution_margin = 0.0
        total_net_margin = 0.0
        net_cost_percentage = 0.0
        gross_margin_percentage = 0.0
        contribution_margin_percentage = 0.0
        net_margin_percentage = 0.0
        total_overhead_costs = 0.0
        total = 0.0
        # trato todas las líneas de tipo "OTHERS"
        total_other_amortizations = 0
        total_other_indirects = 0
        for cost_line in simuline_obj.browse(
                cr, uid, simulation_cost.others_cost_lines_ids):
            # Calculo el total de compras y el total de ventas
            subtotal_others_costs = (subtotal_others_costs +
                                     cost_line.subtotal_purchase)
            subtotal_others_sales = (subtotal_others_sales +
                                     cost_line.subtotal_sale)
            # Sumo los costes de amortización, y los costes indirectos
            total_amortizations = (total_amortizations +
                                   cost_line.amortization_cost)
            total_indirects = total_indirects + cost_line.indirect_cost
            total_other_amortizations = (total_other_amortizations +
                                         cost_line.amortization_cost)
            total_other_indirects = (total_other_indirects +
                                     cost_line.indirect_cost)
            # Sumo importes para Precio Neto, Margen Bruto, Margen de
            # Contribución, Margen Neto
            if cost_line.type2:
                if cost_line.type2 == 'variable':
                    if cost_line.type3:
                        if (cost_line.type3 == 'marketing' or
                                cost_line.type3 == 'sale'):
                            subtotal_net_cost = (subtotal_net_cost +
                                                 cost_line.subtotal_purchase)
                        else:
                            if cost_line.type3 == 'production':
                                subpurchase = cost_line.subtotal_purchase
                                subtotal_gross_margin = (subtotal_gross_margin
                                                         + subpurchase)
                else:
                    if cost_line.type2 == 'fixed':
                        if cost_line.type3:
                            subpurchase = cost_line.subtotal_purchase
                            if cost_line.type3 in ('sale', 'marketing',
                                                   'structureexpenses',
                                                   'generalexpenses',
                                                   'amortizationexpenses'):
                                subtotal_net_margin = (subtotal_net_margin +
                                                       subpurchase)
                            if cost_line.type3 == 'production':
                                submargin = subtotal_contribution_margin
                                subtotal_contribution_margin = (submargin +
                                                                subpurchase)

        subtotal_others_benefit = (subtotal_others_sales -
                                   subtotal_others_costs -
                                   total_other_amortizations -
                                   total_other_indirects)

        for cost_line in simuline_obj.browse(
                cr, uid, simulation_cost.amortization_cost_lines_ids):
            # Calculo el total de compras y el total de ventas
            subtotal_amortization_costs = (subtotal_amortization_costs +
                                           cost_line.subtotal_purchase)
            subtotal_amortization_sales = (subtotal_amortization_sales +
                                           cost_line.subtotal_sale)
            # Sumo importes para Precio Neto, Margen Bruto, Margen de
            # Contribución, Margen Neto
            if cost_line.type2:
                if cost_line.type2 == 'variable':
                    if cost_line.type3:
                        subpurchase = cost_line.subtotal_purchase
                        if (cost_line.type3 == 'marketing' or
                                cost_line.type3 == 'sale'):
                            subtotal_net_cost = (subtotal_net_cost +
                                                 subpurchase)
                        if cost_line.type3 == 'production':
                            subtotal_gross_margin = (subtotal_gross_margin +
                                                     subpurchase)
                else:
                    if cost_line.type2 == 'fixed':
                        if cost_line.type3:
                            subpurchase = cost_line.subtotal_purchase
                            if cost_line.type3 in ('sale', 'marketing',
                                                   'structureexpenses',
                                                   'generalexpenses',
                                                   'amortizationexpenses'):
                                subtotal_net_margin = (subtotal_net_margin +
                                                       subpurchase)
                            if cost_line.type3 == 'production':
                                submargin = subtotal_contribution_margin
                                subtotal_contribution_margin = (submargin +
                                                                subpurchase)

        subtotal_amortization_benefit = (subtotal_amortization_sales -
                                         subtotal_amortization_costs)
        # Calculo totales generales
        total_costs = subtotal_others_costs
        total_sales = subtotal_others_sales + subtotal_amortization_sales
        # Calculo el total de amortizaciones + costes indirectos
        total_amort_indirects = (total_amortizations + total_indirects +
                                 subtotal_amortization_costs)
        # Calculo Precio Neto, Margen Bruto, Margen de Contribución, Margen
        # Neto
        total_net_cost = total_sales - subtotal_net_cost
        total_gross_margin = total_net_cost - subtotal_gross_margin
        total_contribution_margin = (total_gross_margin -
                                     subtotal_contribution_margin -
                                     total_indirects)
        # Calculo los porcentajes de los importes anteriores
        if total_net_cost > 0 and total_sales > 0:
            net_cost_percentage = (total_net_cost * 100) / total_sales
        if total_gross_margin > 0 and total_sales > 0:
            gross_margin_percentage = (total_gross_margin * 100) / total_sales
        if total_contribution_margin > 0 and total_sales > 0:
            contribution_margin_percentage = ((total_contribution_margin * 100)
                                              / total_sales)
        if simulation_cost.overhead_costs:
            if simulation_cost.overhead_costs > 0:
                if total_amort_indirects > 0 or total_costs > 0:
                    total_overhead_costs = (simulation_cost.overhead_costs *
                                            (total_amort_indirects +
                                             total_costs)) / 100
        total = total_amort_indirects + total_costs + total_overhead_costs
        total_benefit = (subtotal_others_benefit +
                         subtotal_amortization_benefit - total_overhead_costs)
        total_net_margin = (total_contribution_margin - subtotal_net_margin -
                            total_amortizations - total_overhead_costs)
        if total_net_margin > 0 and total_sales > 0:
            net_margin_percentage = (total_net_margin * 100) / total_sales
        # Modifico el Objeto con los totales
        percentage = contribution_margin_percentage
        vals = {'subtotal5_purchase': subtotal_others_costs,
                'subtotal5_sale': subtotal_others_sales,
                'benefit5': subtotal_others_benefit,
                'subtotal5t_purchase': subtotal_others_costs,
                'subtotal5t_sale': subtotal_others_sales,
                'subtotal6_purchase': subtotal_amortization_costs,
                'subtotal6_sale': subtotal_amortization_sales,
                'benefit6': subtotal_amortization_benefit,
                'subtotal6t_purchase': subtotal_amortization_costs,
                'subtotal6t_sale': subtotal_amortization_sales,
                'benefit6t': subtotal_amortization_benefit,
                'benefit5t': subtotal_others_benefit,
                'total_costs': total_costs,
                'total_sales': total_sales,
                'total_benefits': total_benefit,
                'total_amortizations': total_amortizations,
                'total_indirects': total_indirects,
                'total_amort_indirects': total_amort_indirects,
                'total_overhead_costs': total_overhead_costs,
                'total': total,
                'net_cost': total_net_cost,
                'net_cost_percentage': net_cost_percentage,
                'gross_margin': total_gross_margin,
                'gross_margin_percentage': gross_margin_percentage,
                'contribution_margin': total_contribution_margin,
                'contribution_margin_percentage': percentage,
                'net_margin': total_net_margin,
                'net_margin_percentage': net_margin_percentage
                }
        self.write(cr, uid, simulation_cost.id, vals)
        return True

    # BOTÓN para crear un pedido de venta
    def button_create_sale_order(self, cr, uid, ids, *args):
        account_journal_obj = self.pool['account.analytic.journal']
        account_account_obj = self.pool['account.account']
        project_obj = self.pool['project.project']
        sale_order_obj = self.pool['sale.order']
        project_financing_obj = self.pool['project.financing']
        # Leo el Objeto Coste
        simulation_cost = self.browse(cr, uid, ids[0])
        # valido que no esté historificado ya
        if simulation_cost.historical_ok:
            raise orm.except_orm(_('Sale Order Creation Error'),
                                 _('You can not generate one Sale Order from '
                                   'one Historical'))
        if not simulation_cost.project_id:
            raise orm.except_orm(_('Sale Order Creation Error'),
                                 _('Simulation WITHOUT PROJECT'))
        project = project_obj.browse(cr, uid, simulation_cost.project_id.id)
        w_cuenta_analitica = project.analytic_account_id.id
        # Cojo el diario analítico
        cond = [('name', 'like', 'Presupuestarias')]
        account_journal_ids = account_journal_obj.search(
            cr, uid, cond)
        if not account_journal_ids:
            raise orm.except_orm(_('Sale Order Creation Error'),
                                 _('Journal with Presupuestarias literal NOT '
                                   'FOUND'))
        # Cojo la cuenta general
        cond = [('name', 'like', 'Your Company')]
        account_account_ids = account_account_obj.search(cr, uid, cond)
        if not account_account_ids:
            raise orm.except_orm(_('Sale Order Creation Error'),
                                 _('General Account YOUR COMPANY not found'))
        # TRATAMIENTO PARA FONDOS FINANCIADORES DEFINIDOS EN LA PROPIA LINEA
        # DE SIMULACION
        # Trato lineas de tipo OTHERS de la simulacion de costes, y doy de
        # alta el apunte MODIF. FINANCIERA
        if (simulation_cost.others_cost_lines_ids and
                simulation_cost.state == 'financing'):
            for line in simulation_cost.others_cost_lines_ids:
                if line.project_financing_id and line.financied_line:
                    self._create_sale_order_case1(
                        cr, uid, simulation_cost, line, w_cuenta_analitica,
                        account_journal_ids[0],
                        account_account_ids[0])
        # Trato lineas de tipo AMORTIZATION de la simulacion de costes, y doy
        # de alta el apunte MODIF. FINANCIERA
        if (simulation_cost.amortization_cost_lines_ids and
                simulation_cost.state == 'financing'):
            for line in simulation_cost.amortization_cost_lines_ids:
                if line.project_financing_id and line.financied_line:
                    self._create_sale_order_case1(
                        cr, uid, simulation_cost, line, w_cuenta_analitica,
                        account_journal_ids[0],
                        account_account_ids[0])
        # TRATAMIENTO PARA FONDOS FINANCIADORES NO DEFINIDOS EN LA PROPIA
        # LINEA DE SIMULACION
        # Trato lineas de tipo OTHERS de la simulacion de costes, y doy de
        # alta el apunte MODIF. FINANCIERA
        if (simulation_cost.others_cost_lines_ids and
                simulation_cost.state == 'financing'):
            for line in simulation_cost.others_cost_lines_ids:
                if not line.project_financing_id and line.financied_line:
                    self._create_sale_order_case2(
                        cr, uid, simulation_cost, line, w_cuenta_analitica,
                        account_journal_ids[0],
                        account_account_ids[0])
        # Trato lineas de tipo AMORTIZATION de la simulacion de costes, y doy
        # de alta el apunte MODIF. FINANCIERA
        if (simulation_cost.amortization_cost_lines_ids and
                simulation_cost.state == 'financing'):
            for line in simulation_cost.amortization_cost_lines_ids:
                if not line.project_financing_id and line.financied_line:
                    self._create_sale_order_case2(
                        cr, uid, simulation_cost, line, w_cuenta_analitica,
                        account_journal_ids[0],
                        account_account_ids[0])
        # Trato lineas de tipo OTHERS de la simulacion de costes PARA
        # MODIFICACIONES FINANCIERAS
        if (simulation_cost.others_cost_lines_ids and
                simulation_cost.state == 'inmodif_budgetary'):
            for line in simulation_cost.others_cost_lines_ids:
                if not line.financied_line:
                    if not line.project_financing_id:
                        self._create_sale_order_case3(
                            cr, uid, simulation_cost, line, w_cuenta_analitica,
                            account_journal_ids[0],
                            account_account_ids[0])
                    else:
                        self._create_sale_order_case4(
                            cr, uid, simulation_cost, line, w_cuenta_analitica,
                            account_journal_ids[0],
                            account_account_ids[0])
        # Trato lineas de tipo AMORTIZATION de la simulacion de costes PARA
        # MODIFICACIONES FINANCIERAS
        if (simulation_cost.amortization_cost_lines_ids and
                simulation_cost.state == 'inmodif_budgetary'):
            for line in simulation_cost.amortization_cost_lines_ids:
                if not line.financied_line:
                    if not line.project_financing_id:
                        self._create_sale_order_case3(
                            cr, uid, simulation_cost, line, w_cuenta_analitica,
                            account_journal_ids[0],
                            account_account_ids[0])
        # Tratamiento para Fuentes de financiación que se hayan definido en el
        # estado de la simulacion in_modif_budgetary
        if (simulation_cost.others_cost_lines_ids and
                simulation_cost.state == 'inmodif_budgetary' and
                simulation_cost.financing_source_ids):
            for financing in simulation_cost.financing_source_ids:
                if not financing.treaty:
                    for line in simulation_cost.others_cost_lines_ids:
                        if not line.project_financing_id:
                            if line.financied_line:
                                if not financing.expense_area_id:
                                    self._create_sale_order_case5(
                                        cr, uid, financing, simulation_cost,
                                        line, w_cuenta_analitica,
                                        account_journal_ids[0],
                                        account_account_ids[0])
                                else:
                                    if (financing.expense_area_id ==
                                            line.expense_area_id):
                                        self._create_sale_order_case6(
                                            cr, uid, financing,
                                            simulation_cost, line,
                                            w_cuenta_analitica,
                                            account_journal_ids[0],
                                            account_account_ids[0])
        cond = [('project2_id', '=', simulation_cost.project_id.id),
                ('state', '=', 'draft')]
        sale_order_ids = sale_order_obj.search(cr, uid, cond)
        if sale_order_ids:
            for sale_order_id in sale_order_ids:
                # Confirmo el pedido de venta
                workflow.trg_validate(uid, 'sale.order', sale_order_id,
                                      'order_confirm', cr)
        if simulation_cost.financing_source_ids:
            for financing in simulation_cost.financing_source_ids:
                project_financing_obj.write(
                    cr, uid, [financing.id], {'treaty': True})
        return True

    def _create_sale_order_case1(self, cr, uid, simulation_cost, line,
                                 w_cuenta_analitica, w_journal_id,
                                 w_account_id):
        analytic_line_obj = self.pool['account.analytic.line']
        sale_order_obj = self.pool['sale.order']
        pedido_linea_obj = self.pool['sale.order.line']
        product_obj = self.pool['product.product']
        simuline_obj = self.pool['simulation.cost.line']
        project_financing_obj = self.pool['project.financing']
        account_simuline_obj = self.pool['account.analytic.simulation.line']
        sequence_obj = self.pool['ir.sequence']
        partner_obj = self.pool['res.partner']
        fiscalpos_obj = self.pool['account.fiscal.position']
        # Valido que halla introducido un producto de venta
        if not line.product_sale_id:
            raise orm.except_orm(_('Process Error'),
                                 _('Purchase product %s, without product '
                                   'sales') % line.product_id.name)
        cond = [('simulation_cost_id', '=', simulation_cost.id),
                ('simulation_cost_line_id', '=', line.id),
                ('expense_area_id', '=', line.expense_area_id.id),
                ('project_financing_id', '=', line.project_financing_id.id)]
        # Busco el apunte analítico
        analytic_simuline_ids = account_simuline_obj.search(
            cr, uid, cond)
        if analytic_simuline_ids:
            # Busco si ya existe el pedido de venta
            financing_source = line.project_financing_id.financing_source_id
            cond = [('partner_id', '=', financing_source.res_partner_id.id),
                    ('project2_id', '=', simulation_cost.project_id.id),
                    ('financing_source_id', '=', financing_source.id),
                    ('sale_type', '=', 'initial'),
                    ('state', '=', 'draft')]
            sale_order_ids = sale_order_obj.search(cr, uid, cond)
            # Cojo los datos del cliente
            addr = partner_obj.address_get(
                cr, uid, [financing_source.res_partner_id.id],
                ['delivery', 'invoice', 'contact'])
            part = partner_obj.browse(cr, uid,
                                      financing_source.res_partner_id.id)
            pricelist = (part.property_product_pricelist and
                         part.property_product_pricelist.id or False)
            payment_term = (part.property_payment_term and
                            part.property_payment_term.id or False)
            fiscal_position = (part.property_account_position and
                               part.property_account_position.id or False)
            dedicated_salesman = part.user_id and part.user_id.id or uid
            if sale_order_ids:
                sale_order_id = sale_order_ids[0]
            else:
                type = simulation_cost.project_type_id.project_type_sequence_id
                simulation_number = sequence_obj.get_id(cr, uid, type.id)
                partner = financing_source.res_partner_id.id.res_partner_id
                val = {'name': simulation_number,
                       'partner_id': partner.id,
                       'partner_invoice_id': addr['invoice'],
                       'partner_order_id': addr['contact'],
                       'partner_shipping_id': addr['delivery'],
                       'payment_term': payment_term,
                       'fiscal_position': fiscal_position,
                       'user_id': dedicated_salesman,
                       'simulation_cost_ids': [(6, 0, [simulation_cost.id])],
                       'project2_id': simulation_cost.project_id.id,
                       'financing_source_id': financing_source.id,
                       'sale_type': 'initial'
                       }
                if pricelist:
                    val['pricelist_id'] = pricelist
                sale_order_id = sale_order_obj.create(cr, uid, val)
            # Creo la linea del pedido de venta
            product = product_obj.browse(cr, uid, line.product_sale_id.id)
            fpos = (fiscal_position and
                    fiscalpos_obj.browse(cr, uid, fiscal_position) or False)
            tax_id = fiscalpos_obj.map_tax(cr, uid, fpos, product.taxes_id)
            # Busco el apunte de la fuente de financiacion
            if simulation_cost.generate_by_lines:
                cond = [('name', 'like', ('Budgetary - ' +
                                          line.product_id.name)),
                        ('type', '=', 'budgetary'),
                        ('expense_area_id', '=', line.expense_area_id.id),
                        ('account_id', '=', w_cuenta_analitica),
                        ('journal_id', '=', w_journal_id),
                        ('general_account_id', '=', w_account_id),
                        ('simulation_cost_line_id', '=', line.id),
                        ('product_id', '=', line.product_id.id),
                        ('simulation_cost_id', '=', simulation_cost.id)]
            else:
                cond = [('name', 'like', ('Budgetary - ' +
                                          line.expense_area_id.name)),
                        ('type', '=', 'budgetary'),
                        ('expense_area_id', '=', line.expense_area_id.id),
                        ('account_id', '=', w_cuenta_analitica),
                        ('journal_id', '=', w_journal_id),
                        ('general_account_id', '=', w_account_id),
                        ('simulation_cost_line_id', '=', False),
                        ('simulation_cost_id', '=', simulation_cost.id)]
            analine_ids = analytic_line_obj.search(cr, uid, cond)
            if not analine_ids:
                if not simulation_cost.generate_by_lines:
                    raise orm.except_orm(_('Sale Order Creation Error'),
                                         _('Budgetary analytic line not found'
                                           ' for product: %s') %
                                         line.product_id.name)
                else:
                    raise orm.except_orm(_('Process Error'),
                                         _('Budgetary analytic line not found'
                                           ' for %s expense area') %
                                         line.expense_area_id.name)
        if not line.product_sale_id:
            financing_id = line.project_financing_id.id
            aline_id = analine_ids[0]
            financsource = line.project_financing_id.financing_source_id
            if not simulation_cost.generate_by_lines:
                cond = [('name', '=', (line.project_financing_id.name + ' - '
                                       + line.product_id.name)),
                        ('type', '=', 'financing_source'),
                        ('expense_area_id', '=', line.expense_area_id.id),
                        ('project_financing_id', '=', financing_id),
                        ('account_analytic_line_budgetary_id', '=', aline_id),
                        ('partner_id', '=', financsource.res_partner_id.id),
                        ('account_id', '=', w_cuenta_analitica),
                        ('journal_id', '=', w_journal_id),
                        ('general_account_id', '=', w_account_id),
                        ('simulation_cost_line_id', '=', line.id),
                        ('product_id', '=', line.product_id.id),
                        ('simulation_cost_id', '=', simulation_cost.id)]
            else:
                cond = [('name', '=', (line.project_financing_id.name + ' - ' +
                                       line.expense_area_id.name)),
                        ('type', '=', 'financing_source'),
                        ('expense_area_id', '=', line.expense_area_id.id),
                        ('project_financing_id', '=', financing_id.i),
                        ('account_analytic_line_budgetary_id', '=', aline_id),
                        ('partner_id', '=', financsource.res_partner_id.id),
                        ('account_id', '=', w_cuenta_analitica),
                        ('journal_id', '=', w_journal_id),
                        ('general_account_id', '=', w_account_id),
                        ('simulation_cost_line_id', '=', False),
                        ('simulation_cost_id', '=', simulation_cost.id)]
            analytic_line_ids = analytic_line_obj.search(cr, uid, cond)
            if not analytic_line_ids:
                if simulation_cost.generate_by_lines:
                    raise orm.except_orm(_('Sale Order Creation Error'),
                                         _('Financing Source analytic line not'
                                           ' found for product: %s') %
                                         line.product_id.name)
                else:
                    raise orm.except_orm(_('Sale Order Creation Error'),
                                         _('Financing Source analytic line not'
                                           ' found for %s expense area') %
                                         line.expense_area_id.name)
            # Busco el apunte analitico en la tabla que relaciona apuntes
            # analiticos y lineas de simulacion
            analytic_simuline = account_simuline_obj.browse(
                cr, uid, analytic_simuline_ids[0])
            aline_id = analine_ids[0]
            amount = analytic_simuline.amount
            percentage = analytic_simuline.financing_percentage
            values_line = {'product_id': line.product_sale_id.id,
                           'type': 'make_to_order',
                           'order_id': sale_order_id,
                           'name': line.product_sale_id.name,
                           'product_uom': product.uom_id.id,
                           'product_uom_qty': line.sale_amount,
                           'price_unit': line.sale_price,
                           'tax_id': [(6, 0, tax_id)],
                           'simulation_cost_line_id': line.id,
                           'account_analytic_id': w_cuenta_analitica,
                           'financial_source_line_id': analytic_line_ids[0],
                           'analytic_budgetary_line_id': aline_id,
                           'financied_amount': amount,
                           'financing_percentage': percentage
                           }
            sale_order_line_id = pedido_linea_obj.create(cr, uid, values_line)
            # Actualizo la linea de simulacion con la linea del pedido de venta
            vals = {'sale_order_line_id': sale_order_line_id}
            simuline_obj.write(cr, uid, [line.id], vals)
            # Actualizo el fondo financiador con el codigo del pedido de venta
            vals = {'sale_order_id': sale_order_id}
            project_financing_obj.write(cr, uid,
                                        [line.project_financing_id.id], vals)
        return True

    def _create_sale_order_case2(self, cr, uid, simulation_cost, line,
                                 w_cuenta_analitica, w_journal_id,
                                 w_account_id):
        analytic_line_obj = self.pool['account.analytic.line']
        sale_order_obj = self.pool['sale.order']
        pedido_linea_obj = self.pool['sale.order.line']
        product_obj = self.pool['product.product']
        simuline_obj = self.pool['simulation.cost.line']
        project_financing_obj = self.pool['project.financing']
        account_simuline_obj = self.pool['account.analytic.simulation.line']
        sequence_obj = self.pool['ir.sequence']
        partner_obj = self.pool['res.partner']
        fiscal_position_obj = self.pool['account.fiscal.position']
        # Valido que halla introducido un producto de venta
        if not line.product_sale_id:
            raise orm.except_orm(_('Sale Order Creation Error'),
                                 _('Purchase product %s, without product'
                                   ' sales') % line.product_id.name)
        # BUSCO FONDOS FINANCIADORES QUE FINANCIEN EL AREA DE GASTO DE LA
        # LINEA DE SIMULACION
        with_area = True
        cond = [('simulation_cost_id', '=', simulation_cost.id),
                ('expense_area_id', '=', line.expense_area_id.id)]
        project_financing_ids = project_financing_obj.search(cr, uid, cond)
        if not project_financing_ids:
            with_area = False
            # BUSCO FONDOS FINANCIADORES QUE FINANCIEN TODAS LAS AREAS DE GASTO
            cond = [('simulation_cost_id', '=', simulation_cost.id),
                    ('expense_area_id', '=', False)]
            project_financing_ids = project_financing_obj.search(cr, uid, cond)
        # TRATO LOS FONDOS FINANCIADORES
        if project_financing_ids:
            for project_financing in project_financing_obj.browse(
                    cr, uid, project_financing_ids):
                # Busco el apunte analítico
                cond = [('simulation_cost_id', '=', simulation_cost.id),
                        ('simulation_cost_line_id', '=', line.id),
                        ('expense_area_id', '=', line.expense_area_id.id),
                        ('project_financing_id', '=', project_financing.id)]
                analytic_simuline_ids = account_simuline_obj.search(cr, uid,
                                                                    cond)
                partner = project_financing.financing_source_id.res_partner_id
                fsource = project_financing.financing_source_id
                sproject = simulation_cost.project_id
                if analytic_simuline_ids:
                    cond = [('partner_id', '=', partner.id),
                            ('project2_id', '=', sproject.id),
                            ('financing_source_id', '=', fsource.id),
                            ('sale_type', '=', 'initial'),
                            ('state', '=', 'draft')]
                    sale_order_ids = sale_order_obj.search(cr, uid, cond)
                    # Cojo los datos del cliente
                    addr = partner_obj.address_get(
                        cr, uid, [partner.id], ['delivery', 'invoice',
                                                'contact'])
                    part = partner_obj.browse(cr, uid, partner.id)
                    pricelist = (part.property_product_pricelist and
                                 part.property_product_pricelist.id or False)
                    payment_term = (part.property_payment_term and
                                    part.property_payment_term.id or False)
                    fiscal_position = (part.property_account_position and
                                       part.property_account_position.id or
                                       False)
                    dedicated_salesman = (part.user_id and part.user_id.id or
                                          uid)
                    if sale_order_ids:
                        sale_order_id = sale_order_ids[0]
                    else:
                        projtype = simulation_cost.project_type_id
                        simulation_number = sequence_obj.get_id(
                            cr, uid, projtype.project_type_sequence_id.id)
                        simu_id = simulation_cost.id
                        fsource = project_financing.financing_source_id
                        val = {'name': simulation_number,
                               'partner_id': partner.id,
                               'partner_invoice_id': addr['invoice'],
                               'partner_order_id': addr['contact'],
                               'partner_shipping_id': addr['delivery'],
                               'payment_term': payment_term,
                               'fiscal_position': fiscal_position,
                               'user_id': dedicated_salesman,
                               'simulation_cost_ids':  [(6, 0, [simu_id])],
                               'project2_id': simulation_cost.project_id.id,
                               'financing_source_id': fsource.id,
                               'sale_type': 'initial'
                               }
                        if pricelist:
                            val['pricelist_id'] = pricelist
                        # Grabo SALE.ORDER
                        sale_order_id = sale_order_obj.create(cr, uid, val)
                    # Creo la linea del pedido de venta
                    product = product_obj.browse(cr, uid,
                                                 line.product_sale_id.id)
                    fpos = (fiscal_position and
                            fiscal_position_obj.browse(cr, uid,
                                                       fiscal_position) or
                            False)
                    tax_id = fiscal_position_obj.map_tax(
                        cr, uid, fpos, product.taxes_id)
                    # Busco el apunte de la fuente de financiacion
                    expense_area_id = line.expense_area_id.id
                    simu_id = simulation_cost.id
                    if simulation_cost.generate_by_lines:
                        cond = [('name', 'like', ('Budgetary - ' +
                                                  line.product_id.name)),
                                ('type', '=', 'budgetary'),
                                ('expense_area_id', '=', expense_area_id),
                                ('account_id', '=', w_cuenta_analitica),
                                ('journal_id', '=', w_journal_id),
                                ('general_account_id', '=', w_account_id),
                                ('simulation_cost_line_id', '=', line.id),
                                ('product_id', '=', line.product_id.id),
                                ('simulation_cost_id', '=', simu_id)]
                    else:
                        cond = [('name', 'like', ('Budgetary - ' +
                                                  line.expense_area_id.name)),
                                ('type', '=', 'budgetary'),
                                ('expense_area_id', '=', expense_area_id),
                                ('account_id', '=', w_cuenta_analitica),
                                ('journal_id', '=', w_journal_id),
                                ('general_account_id', '=', w_account_id),
                                ('simulation_cost_line_id', '=', False),
                                ('simulation_cost_id', '=', simu_id)]
                    analine_ids = analytic_line_obj.search(
                        cr, uid, cond)
                    if not analine_ids:
                        if simulation_cost.generate_by_lines:
                            raise orm.except_orm(_('Sale Order Creation '
                                                   'Error'),
                                                 _('Budgetary analytic line '
                                                   'not found for product: %s')
                                                 % line.product_id.name)
                        else:
                            raise orm.except_orm(_('Sale Order Creation '
                                                   'Error'),
                                                 _('Budgetary analytic line '
                                                   'not found for %s expense '
                                                   'area') %
                                                 line.expense_area_id.name)
                    expense_area_id = line.expense_area_id.id
                    pfinan_id = project_financing.id
                    fsource = project_financing.financing_source_id
                    simu_id = simulation_cost.id
                    if not with_area:
                        if simulation_cost.generate_by_lines:
                            cond = [('name', '=', project_financing.name),
                                    ('type', '=', 'financing_source'),
                                    ('expense_area_id', '=', expense_area_id),
                                    ('project_financing_id', '=', pfinan_id),
                                    ('account_analytic_line_budgetary_id', '=',
                                     analine_ids[0]),
                                    ('partner_id', '=',
                                     fsource.res_partner_id.id),
                                    ('account_id', '=', w_cuenta_analitica),
                                    ('journal_id', '=', w_journal_id),
                                    ('general_account_id', '=', w_account_id),
                                    ('simulation_cost_line_id', '=', line.id),
                                    ('product_id', '=', line.product_id.id),
                                    ('simulation_cost_id', '=', simu_id)]
                        else:
                            cond = [('name', '=', project_financing.name),
                                    ('type', '=', 'financing_source'),
                                    ('expense_area_id', '=', expense_area_id),
                                    ('project_financing_id', '=', pfinan_id),
                                    ('account_analytic_line_budgetary_id', '=',
                                     analine_ids[0]),
                                    ('partner_id', '=',
                                     fsource.res_partner_id.id),
                                    ('account_id', '=', w_cuenta_analitica),
                                    ('journal_id', '=', w_journal_id),
                                    ('general_account_id', '=', w_account_id),
                                    ('simulation_cost_line_id', '=', False),
                                    ('simulation_cost_id', '=', simu_id)]
                        analytic_line_ids = analytic_line_obj.search(
                            cr, uid, cond)
                    else:
                        if simulation_cost.generate_by_lines:
                            cond = [('name', '=', (project_financing.name +
                                                   ' - ' + line.product_id.name
                                                   + ' - ' +
                                                   line.expense_area_id.name)),
                                    ('type', '=', 'financing_source'),
                                    ('expense_area_id', '=', expense_area_id),
                                    ('project_financing_id', '=', pfinan_id),
                                    ('account_analytic_line_budgetary_id', '=',
                                     analine_ids[0]),
                                    ('partner_id', '=',
                                     fsource.res_partner_id.id),
                                    ('account_id', '=', w_cuenta_analitica),
                                    ('journal_id', '=', w_journal_id),
                                    ('general_account_id', '=', w_account_id),
                                    ('simulation_cost_line_id', '=', line.id),
                                    ('product_id', '=', line.product_id.id),
                                    ('simulation_cost_id', '=', simu_id)]
                        else:
                            cond = [('name', '=', (project_financing.name +
                                                   ' - ' +
                                                   line.expense_area_id.name)),
                                    ('type', '=', 'financing_source'),
                                    ('expense_area_id', '=', expense_area_id),
                                    ('project_financing_id', '=', pfinan_id),
                                    ('account_analytic_line_budgetary_id', '=',
                                     analine_ids[0]),
                                    ('partner_id', '=',
                                     fsource.res_partner_id.id),
                                    ('account_id', '=', w_cuenta_analitica),
                                    ('journal_id', '=', w_journal_id),
                                    ('general_account_id', '=', w_account_id),
                                    ('simulation_cost_line_id', '=', False),
                                    ('simulation_cost_id', '=', simu_id)]
                    analytic_line_ids = analytic_line_obj.search(cr, uid, cond)
                    if not analytic_line_ids:
                        if not simulation_cost.generate_by_lines:
                            raise orm.except_orm(_('Sale Order Creation '
                                                   'Error'),
                                                 _('Financing Source analytic '
                                                   'line not found for %s '
                                                   'expense area') %
                                                 line.expense_area_id.name)
                        else:
                            raise orm.except_orm(_('Sale Order Creation '
                                                   'Error'),
                                                 _('Financing Source analytic '
                                                   'line not found for '
                                                   'product: %s') %
                                                 line.product_id.name)
                    # Busco el apunte analitico en la tabla que relaciona
                    # apuntes analiticos y lineas de simulacion
                    analytic_simuline = account_simuline_obj.browse(
                        cr, uid, analytic_simuline_ids[0])
                    w_price_unit = ((line.sale_price *
                                    analytic_simuline.financing_percentage) /
                                    100)
                    values_line = {'product_id': line.product_sale_id.id,
                                   'type': 'make_to_order',
                                   'order_id': sale_order_id,
                                   'name': line.product_sale_id.name,
                                   'product_uom': product.uom_id.id,
                                   'product_uom_qty': line.sale_amount,
                                   'price_unit': w_price_unit,
                                   'tax_id': [(6, 0, tax_id)],
                                   'simulation_cost_line_id': line.id,
                                   'account_analytic_id': w_cuenta_analitica,
                                   'financial_source_line_id':
                                   analytic_line_ids[0],
                                   'analytic_budgetary_line_id':
                                   analine_ids[0],
                                   'financied_amount':
                                   analytic_simuline.amount,
                                   'financing_percentage':
                                   analytic_simuline.financing_percentage
                                   }
                    sale_order_line_id = pedido_linea_obj.create(
                        cr, uid, values_line)
                    # Actualizo la linea de simulacion con la linea del pedido
                    # de venta
                    vals = {'sale_order_line_id': sale_order_line_id}
                    simuline_obj.write(cr, uid, [line.id], vals)
                    # Actualizo el fondo financiador con el codigo del pedido
                    # de venta
                    vals = {'sale_order_id': sale_order_id}
                    project_financing_obj.write(cr, uid,
                                                [project_financing.id], vals)
        return True

    def _create_sale_order_case3(self, cr, uid, simulation_cost, line,
                                 w_cuenta_analitica, w_journal_id,
                                 w_account_id):
        analytic_line_obj = self.pool['account.analytic.line']
        sale_order_obj = self.pool['sale.order']
        pedido_linea_obj = self.pool['sale.order.line']
        product_obj = self.pool['product.product']
        simuline_obj = self.pool['simulation.cost.line']
        project_financing_obj = self.pool['project.financing']
        sequence_obj = self.pool['ir.sequence']
        partner_obj = self.pool['res.partner']
        fposition_obj = self.pool['account.fiscal.position']
        # Valido que halla introducido un producto de venta
        if not line.product_sale_id:
            raise orm.except_orm(_('Sale Order Creation Error'),
                                 _('Purchase product %s, without product '
                                   'sales') % line.product_id.name)
        # BUSCO FONDOS FINANCIADORES QUE FINANCIEN EL AREA DE GASTO DE LA
        # LINEA DE SIMULACION
        with_area = True
        cond = [('simulation_cost_id', '=', simulation_cost.id),
                ('expense_area_id', '=', line.expense_area_id.id)]
        project_financing_ids = project_financing_obj.search(cr, uid, cond)
        if not project_financing_ids:
            with_area = False
            # BUSCO FONDOS FINANCIADORES QUE FINANCIEN TODAS LAS AREAS DE GASTO
            cond = [('simulation_cost_id', '=', simulation_cost.id),
                    ('expense_area_id', '=', False)]
            project_financing_ids = project_financing_obj.search(cr, uid, cond)
        # TRATO LOS FONDOS FINANCIADORES
        if project_financing_ids:
            for project_financing in project_financing_obj.browse(
                    cr, uid, project_financing_ids):
                fsource = project_financing.financing_source_id
                cond = [('partner_id', '=', fsource.res_partner_id.id),
                        ('project2_id', '=', simulation_cost.project_id.id),
                        ('financing_source_id', '=',
                         project_financing.financing_source_id.id),
                        ('sale_type', '=', 'modification'),
                        ('state', '=', 'draft')]
                sale_order_ids = sale_order_obj.search(cr, uid, cond)
                # Cojo los datos del cliente
                addr = partner_obj.address_get(
                    cr, uid, [fsource.res_partner_id.id],
                    ['delivery', 'invoice', 'contact'])
                part = partner_obj.browse(cr, uid, fsource.res_partner_id.id)
                pricelist = (part.property_product_pricelist and
                             part.property_product_pricelist.id or False)
                payment_term = (part.property_payment_term and
                                part.property_payment_term.id or False)
                fiscal_position = (part.property_account_position and
                                   part.property_account_position.id or False)
                dedicated_salesman = part.user_id and part.user_id.id or uid
                if sale_order_ids:
                    sale_order_id = sale_order_ids[0]
                else:
                    projtype = simulation_cost.project_type_id
                    simulation_number = sequence_obj.get_id(
                        cr, uid, projtype.project_type_sequence_id.id)
                    fsource = project_financing.financing_source_id
                    val = {'name': simulation_number,
                           'partner_id': fsource.res_partner_id.id,
                           'partner_invoice_id': addr['invoice'],
                           'partner_order_id': addr['contact'],
                           'partner_shipping_id': addr['delivery'],
                           'payment_term': payment_term,
                           'fiscal_position': fiscal_position,
                           'user_id': dedicated_salesman,
                           'simulation_cost_ids':  [(6, 0,
                                                     [simulation_cost.id])],
                           'project_financing_id': project_financing.id,
                           'financing_source_id': fsource.id,
                           'project2_id': simulation_cost.project_id.id,
                           'sale_type': 'modification'
                           }
                    if pricelist:
                        val['pricelist_id'] = pricelist
                    # Grabo SALE.ORDER
                    sale_order_id = sale_order_obj.create(cr, uid, val)
                # Creo la linea del pedido de venta
                product = product_obj.browse(cr, uid,
                                             line.product_sale_id.id)
                fpos = (fiscal_position and
                        fposition_obj.browse(cr, uid, fiscal_position) or
                        False)
                tax_id = fposition_obj.map_tax(cr, uid, fpos, product.taxes_id)
                # Busco el apunte de la fuente de financiacion
                if not simulation_cost.generate_by_lines:
                    cond = [('name', 'like', ('Budgetary - ' +
                                              line.expense_area_id.name)),
                            ('type', '=', 'budgetary'),
                            ('expense_area_id', '=', line.expense_area_id.id),
                            ('account_id', '=', w_cuenta_analitica),
                            ('journal_id', '=', w_journal_id),
                            ('general_account_id', '=', w_account_id),
                            ('simulation_cost_line_id', '=', False),
                            ('simulation_cost_id', '=', simulation_cost.id)]
                    analine_ids = analytic_line_obj.search(
                        cr, uid, cond)
                else:
                    cond = [('name', 'like', ('Budgetary - ' +
                                              line.product_id.name)),
                            ('type', '=', 'budgetary'),
                            ('expense_area_id', '=', line.expense_area_id.id),
                            ('account_id', '=', w_cuenta_analitica),
                            ('journal_id', '=', w_journal_id),
                            ('general_account_id', '=', w_account_id),
                            ('simulation_cost_line_id', '=', line.id),
                            ('product_id', '=', line.product_id.id),
                            ('simulation_cost_id', '=', simulation_cost.id)]
                    analine_ids = analytic_line_obj.search(
                        cr, uid, cond)
                    if not analine_ids:
                        line_vals = {'name': ('Budgetary - ' +
                                              line.product_id.name),
                                     'type': 'budgetary',
                                     'expense_area_id':
                                     line.expense_area_id.id,
                                     'account_id': w_cuenta_analitica,
                                     'journal_id': w_journal_id,
                                     'general_account_id': w_account_id,
                                     'simulation_cost_line_id': line.id,
                                     'product_id': line.product_id.id,
                                     'simulation_cost_id': simulation_cost.id
                                     }
                        account_analytic_line_id = analytic_line_obj.create(
                            cr, uid, line_vals)
                        analine_ids = [account_analytic_line_id]
                if not analine_ids:
                    if not simulation_cost.generate_by_lines:
                        raise orm.except_orm(_('Sale Order Creation Error'),
                                             _('Budgetary analytic line not '
                                               'found for %s expense area') %
                                             line.expense_area_id.name)
                    else:
                        raise orm.except_orm(_('Sale Order Creation Error'),
                                             _('Budgetary analytic line not '
                                               'found for product %s') %
                                             line.product_id.name)
                if not with_area:
                    fsource = project_financing.financing_source_id
                    simu_id = simulation_cost.id
                    if not simulation_cost.generate_by_lines:
                        cond = [('name', '=', project_financing.name),
                                ('type', '=', 'financing_source'),
                                ('expense_area_id', '=',
                                 line.expense_area_id.id),
                                ('project_financing_id', '=',
                                 project_financing.id),
                                ('account_analytic_line_budgetary_id', '=',
                                 analine_ids[0]),
                                ('partner_id', '=', fsource.res_partner_id.id),
                                ('account_id', '=', w_cuenta_analitica),
                                ('journal_id', '=', w_journal_id),
                                ('general_account_id', '=', w_account_id),
                                ('simulation_cost_line_id', '=', False),
                                ('simulation_cost_id', '=', simu_id)]
                        analytic_line_ids = analytic_line_obj.search(
                            cr, uid, cond)
                    else:
                        line_vals = {'name': project_financing.name,
                                     'type': 'financing_source',
                                     'expense_area_id':
                                     line.expense_area_id.id,
                                     'project_financing_id':
                                     project_financing.id,
                                     'account_analytic_line_budgetary_id':
                                     analine_ids[0],
                                     'partner_id': fsource.res_partner_id.id,
                                     'account_id': w_cuenta_analitica,
                                     'journal_id': w_journal_id,
                                     'general_account_id': w_account_id,
                                     'simulation_cost_line_id': line.id,
                                     'financing_percentage':
                                     project_financing.project_percent,
                                     'product_id': line.product_id.id,
                                     'simulation_cost_id': simulation_cost.id
                                     }
                        analytic_line_id = analytic_line_obj.create(cr, uid,
                                                                    line_vals)
                        analytic_line_ids = [analytic_line_id]
                else:
                    fsource = project_financing.financing_source_id
                    simu_id = simulation_cost.id
                    if not simulation_cost.generate_by_lines:
                        cond = [('name', '=', (project_financing.name + ' - ' +
                                               line.expense_area_id.name)),
                                ('type', '=', 'financing_source'),
                                ('expense_area_id', '=',
                                 line.expense_area_id.id),
                                ('project_financing_id', '=',
                                 project_financing.id),
                                ('account_analytic_line_budgetary_id', '=',
                                 analine_ids[0]),
                                ('partner_id', '=', fsource.res_partner_id.id),
                                ('account_id', '=', w_cuenta_analitica),
                                ('journal_id', '=', w_journal_id),
                                ('general_account_id', '=', w_account_id),
                                ('simulation_cost_line_id', '=', False),
                                ('simulation_cost_id', '=', simu_id)]
                        analytic_line_ids = analytic_line_obj.search(cr, uid,
                                                                     cond)
                    else:
                        line_vals = {'name': (project_financing.name + ' - ' +
                                              line.product_id.name + ' - ' +
                                              line.expense_area_id.name),
                                     'type': 'financing_source',
                                     'expense_area_id':
                                     line.expense_area_id.id,
                                     'project_financing_id':
                                     project_financing.id,
                                     'account_analytic_line_budgetary_id':
                                     analine_ids[0],
                                     'partner_id': fsource.res_partner_id.id,
                                     'account_id': w_cuenta_analitica,
                                     'journal_id': w_journal_id,
                                     'general_account_id': w_account_id,
                                     'simulation_cost_line_id': line.id,
                                     'financing_percentage':
                                     project_financing.project_percent,
                                     'product_id': line.product_id.id,
                                     'simulation_cost_id': simu_id
                                     }
                        analytic_line_id = analytic_line_obj.create(cr, uid,
                                                                    line_vals)
                        analytic_line_ids = [analytic_line_id]
                if not analytic_line_ids:
                    if not simulation_cost.generate_by_lines:
                        raise orm.except_orm(_('Sale Order Creation Error'),
                                             _('Financing Source analytic line'
                                               ' not found for %s expense '
                                               'area') %
                                             line.expense_area_id.name)
                    else:
                        raise orm.except_orm(_('Sale Order Creation Error'),
                                             _('Financing Source analytic line'
                                               ' not found for product %s') %
                                             line.product_id.name)
                # Doy de alta la linea del pedido de venta
                w_imp = ((line.subtotal_purchase *
                          project_financing.project_percent) / 100)
                w_price_unit = ((line.sale_price *
                                 project_financing.project_percent) / 100)
                values_line = {'product_id': line.product_sale_id.id,
                               'type': 'make_to_order',
                               'order_id': sale_order_id,
                               'name': line.product_sale_id.name,
                               'product_uom': product.uom_id.id,
                               'product_uom_qty': line.sale_amount,
                               'price_unit': w_price_unit,
                               'tax_id': [(6, 0, tax_id)],
                               'simulation_cost_line_id': line.id,
                               'account_analytic_id': w_cuenta_analitica,
                               'financial_source_line_id':
                               analytic_line_ids[0],
                               'analytic_budgetary_line_id':
                               analine_ids[0],
                               'financied_amount': w_imp,
                               'financing_percentage':
                               project_financing.project_percent
                               }
                sale_order_line_id = pedido_linea_obj.create(cr, uid,
                                                             values_line)
                # Actualizo la linea de simulacion con la linea del pedido
                # de venta
                vals = {'sale_order_line_id': sale_order_line_id,
                        'financied_line': True}
                simuline_obj.write(cr, uid, [line.id], vals)
                # Actualizo el fondo financiador con el codigo del pedido de
                # venta, el imorte que financia
                w_imp2 = project_financing.amount_awarded + w_imp
                vals = {'sale_order_id': sale_order_id,
                        'amount_awarded': w_imp2,
                        'grant': w_imp2}
                project_financing_obj.write(cr, uid, [project_financing.id],
                                            vals)
        return True

    def _create_sale_order_case4(self, cr, uid, simulation_cost, line,
                                 w_cuenta_analitica, w_journal_id,
                                 w_account_id):
        analytic_line_obj = self.pool['account.analytic.line']
        sale_order_obj = self.pool['sale.order']
        pedido_linea_obj = self.pool['sale.order.line']
        product_obj = self.pool['product.product']
        simuline_obj = self.pool['simulation.cost.line']
        project_financing_obj = self.pool['project.financing']
        sequence_obj = self.pool['ir.sequence']
        partner_obj = self.pool['res.partner']
        fposition_obj = self.pool['account.fiscal.position']
        # Valido que halla introducido un producto de venta
        if not line.product_sale_id:
            raise orm.except_orm(_('Sale Order Creation Error'),
                                 _('Purchase product %s, without product '
                                   'sales') % line.product_id.name)
        fsource = line.project_financing_id.financing_source_id
        cond = [('partner_id', '=', fsource.res_partner_id.id),
                ('project2_id', '=', simulation_cost.project_id.id),
                ('financing_source_id', '=', fsource.id),
                ('sale_type', '=', 'modification'),
                ('state', '=', 'draft')]
        sale_order_ids = sale_order_obj.search(cr, uid, cond)
        # Cojo los datos del cliente
        addr = partner_obj.address_get(
            cr, uid, [fsource.res_partner_id.id], ['delivery', 'invoice',
                                                   'contact'])
        part = partner_obj.browse(cr, uid, fsource.res_partner_id.id)
        pricelist = (part.property_product_pricelist and
                     part.property_product_pricelist.id or False)
        payment_term = (part.property_payment_term and
                        part.property_payment_term.id or False)
        fiscal_position = (part.property_account_position and
                           part.property_account_position.id or False)
        dedicated_salesman = part.user_id and part.user_id.id or uid
        if sale_order_ids:
            sale_order_id = sale_order_ids[0]
        else:
            projtype = simulation_cost.project_type_id
            simulation_number = sequence_obj.get_id(
                cr, uid, projtype.project_type_sequence_id.id)
            val = {'name': simulation_number,
                   'partner_id': fsource.res_partner_id.id,
                   'partner_invoice_id': addr['invoice'],
                   'partner_order_id': addr['contact'],
                   'partner_shipping_id': addr['delivery'],
                   'payment_term': payment_term,
                   'fiscal_position': fiscal_position,
                   'user_id': dedicated_salesman,
                   'simulation_cost_ids':  [(6, 0, [simulation_cost.id])],
                   'project2_id': simulation_cost.project_id.id,
                   'financing_source_id': fsource.id,
                   'sale_type': 'modification'
                   }
            if pricelist:
                val['pricelist_id'] = pricelist
            # Grabo SALE.ORDER
            sale_order_id = sale_order_obj.create(cr, uid, val)
        # Creo la linea del pedido de venta
        product = product_obj.browse(cr, uid, line.product_sale_id.id)
        fpos = (fiscal_position and
                fposition_obj.browse(cr, uid, fiscal_position) or False)
        tax_id = fposition_obj.map_tax(cr, uid, fpos, product.taxes_id)
        # Busco el apunte de la fuente de financiacion
        if not simulation_cost.generate_by_lines:
            cond = [('name', 'like', ('Budgetary - ' +
                                      line.expense_area_id.name)),
                    ('type', '=', 'budgetary'),
                    ('expense_area_id', '=', line.expense_area_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', False),
                    ('simulation_cost_id', '=', simulation_cost.id)]
            analine_ids = analytic_line_obj.search(cr, uid, cond)
            if not analine_ids:
                line_vals = {'name': 'Budgetary - ' + line.product_id.name,
                             'type': 'budgetary',
                             'expense_area_id': line.expense_area_id.id,
                             'account_id': w_cuenta_analitica,
                             'journal_id': w_journal_id,
                             'general_account_id': w_account_id,
                             'simulation_cost_line_id': False,
                             'simulation_cost_id': simulation_cost.id
                             }
                account_analytic_line_id = analytic_line_obj.create(cr, uid,
                                                                    line_vals)
                analine_ids = [account_analytic_line_id]
        else:
            cond = [('name', 'like', 'Budgetary - ' + line.product_id.name),
                    ('type', '=', 'budgetary'),
                    ('expense_area_id', '=', line.expense_area_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', line.id),
                    ('product_id', '=', line.product_id.id),
                    ('simulation_cost_id', '=', simulation_cost.id)]
            analine_ids = analytic_line_obj.search(cr, uid, cond)
            if not analine_ids:
                line_vals = {'name': 'Budgetary - ' + line.product_id.name,
                             'type': 'budgetary',
                             'expense_area_id': line.expense_area_id.id,
                             'account_id': w_cuenta_analitica,
                             'journal_id': w_journal_id,
                             'general_account_id': w_account_id,
                             'simulation_cost_line_id': line.id,
                             'product_id': line.product_id.id,
                             'simulation_cost_id': simulation_cost.id
                             }
                account_analytic_line_id = analytic_line_obj.create(cr, uid,
                                                                    line_vals)
                analine_ids = [account_analytic_line_id]
        if not analine_ids:
            if not simulation_cost.generate_by_lines:
                raise orm.except_orm(_('Sale Order Creation Error'),
                                     _('Budgetary analytic line not found for '
                                       '%s expense area') %
                                     line.expense_area_id.name)
            else:
                raise orm.except_orm(_('Sale Order Creation Error'),
                                     _('Budgetary analytic line not found for '
                                       'product: %s') % line.product_id.name)
        fsource = line.project_financing_id.financing_source_id
        if not simulation_cost.generate_by_lines:
            cond = [('name', '=', (line.project_financing_id.name + ' - ' +
                                   line.expense_area_id.name)),
                    ('type', '=', 'financing_source'),
                    ('expense_area_id', '=', line.expense_area_id.id),
                    ('project_financing_id', '=',
                     line.project_financing_id.id),
                    ('account_analytic_line_budgetary_id', '=',
                     analine_ids[0]),
                    ('partner_id', '=', fsource.res_partner_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', False),
                    ('simulation_cost_id', '=', simulation_cost.id)]
            analytic_line_ids = analytic_line_obj.search(cr, uid, cond)
            if not analytic_line_ids:
                line_vals = {'name': (line.project_financing_id.name + ' - ' +
                                      line.expense_area_id.name),
                             'type': 'financing_source',
                             'expense_area_id':
                             line.expense_area_id.id,
                             'project_financing_id':
                             line.project_financing_id.id,
                             'account_analytic_line_budgetary_id':
                             analine_ids[0],
                             'partner_id': fsource.res_partner_id.id,
                             'account_id': w_cuenta_analitica,
                             'journal_id': w_journal_id,
                             'general_account_id': w_account_id,
                             'financing_percentage': 100,
                             'simulation_cost_id': simulation_cost.id
                             }
                analytic_line_id = analytic_line_obj.create(cr, uid, line_vals)
                analytic_line_ids = [analytic_line_id]
        else:
            cond = [('name', '=', (line.project_financing_id.name + ' - ' +
                                   line.product_id.name)),
                    ('type', '=', 'financing_source'),
                    ('expense_area_id', '=', line.expense_area_id.id),
                    ('project_financing_id', '=',
                     line.project_financing_id.id),
                    ('account_analytic_line_budgetary_id', '=',
                     analine_ids[0]),
                    ('partner_id', '=', fsource.res_partner_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', line.id),
                    ('product_id', '=', line.product_id.id),
                    ('simulation_cost_id', '=', simulation_cost.id)]
            analytic_line_ids = analytic_line_obj.search(cr, uid, cond)
            if not analytic_line_ids:
                line_vals = {'name': (line.project_financing_id.name + ' - ' +
                                      line.expense_area_id.name),
                             'type': 'financing_source',
                             'expense_area_id':
                             line.expense_area_id.id,
                             'project_financing_id':
                             line.project_financing_id.id,
                             'account_analytic_line_budgetary_id':
                             analine_ids[0],
                             'partner_id': fsource.res_partner_id.id,
                             'account_id': w_cuenta_analitica,
                             'journal_id': w_journal_id,
                             'general_account_id': w_account_id,
                             'simulation_cost_line_id': line.id,
                             'product_id': line.product_id.id,
                             'financing_percentage': 100,
                             'simulation_cost_id': simulation_cost.id
                             }
                analytic_line_id = analytic_line_obj.create(cr, uid, line_vals)
                analytic_line_ids = [analytic_line_id]
        if not analytic_line_ids:
            if not simulation_cost.generate_by_lines:
                raise orm.except_orm(_('Sale Order Creation Error'),
                                     _('Financing Source analytic line not '
                                       'found for %s expense area') %
                                     line.expense_area_id.name)
            else:
                raise orm.except_orm(_('Sale Order Creation Error'),
                                     _('Financing Source analytic line not '
                                       'found for product %s') %
                                     line.product_id.name)
        # Doy de alta la linea del pedido de venta
        w_imp = line.subtotal_purchase
        w_price_unit = line.sale_price
        values_line = {'product_id': line.product_sale_id.id,
                       'type': 'make_to_order',
                       'order_id': sale_order_id,
                       'name': line.product_sale_id.name,
                       'product_uom': product.uom_id.id,
                       'product_uom_qty': line.sale_amount,
                       'price_unit': w_price_unit,
                       'tax_id': [(6, 0, tax_id)],
                       'simulation_cost_line_id': line.id,
                       'account_analytic_id': w_cuenta_analitica,
                       'financial_source_line_id': analytic_line_ids[0],
                       'analytic_budgetary_line_id': analine_ids[0],
                       'financied_amount': w_imp,
                       'financing_percentage': 100
                       }
        sale_order_line_id = pedido_linea_obj.create(cr, uid, values_line)
        # Actualizo la linea de simulacion con la linea del pedido de venta
        vals = {'sale_order_line_id': sale_order_line_id,
                'financied_line': True}
        simuline_obj.write(cr, uid, [line.id], vals)
        # Actualizo el fondo financiador con el codigo del pedido de venta, el
        # imorte que financia
        w_imp2 = line.project_financing_id.amount_awarded + w_imp
        vals = {'sale_order_id': sale_order_id,
                'amount_awarded': w_imp2,
                'grant': w_imp2}
        project_financing_obj.write(cr, uid, [line.project_financing_id.id],
                                    vals)
        return True

    def _create_sale_order_case5(self, cr, uid, project_financing,
                                 simulation_cost, line, w_cuenta_analitica,
                                 w_journal_id, w_account_id):
        analytic_line_obj = self.pool['account.analytic.line']
        sale_order_obj = self.pool['sale.order']
        pedido_linea_obj = self.pool['sale.order.line']
        product_obj = self.pool['product.product']
        simuline_obj = self.pool['simulation.cost.line']
        project_financing_obj = self.pool['project.financing']
        partner_obj = self.pool['res.partner']
        sequence_obj = self.pool['ir.sequence']
        fposition_obj = self.pool['account.fiscal.position']
        # Valido que halla introducido un producto de venta
        if not line.product_sale_id:
            raise orm.except_orm(_('Sale Order Creation Error'),
                                 _('Purchase product %s, without product '
                                   'sales') % line.product_id.name)
        # BUSCO FONDOS FINANCIADORES QUE FINANCIEN EL AREA DE GASTO DE LA
        # LINEA DE SIMULACION
        fsource = project_financing.financing_source_id
        cond = [('partner_id', '=', fsource.res_partner_id.id),
                ('project2_id', '=', simulation_cost.project_id.id),
                ('financing_source_id', '=', fsource.id),
                ('sale_type', '=', 'modification'),
                ('state', '=', 'draft')]
        sale_order_ids = sale_order_obj.search(cr, uid, cond)
        # Cojo los datos del cliente
        addr = partner_obj.address_get(
            cr, uid, [fsource.res_partner_id.id], ['delivery', 'invoice',
                                                   'contact'])
        part = partner_obj.browse(cr, uid, fsource.res_partner_id.id)
        pricelist = (part.property_product_pricelist and
                     part.property_product_pricelist.id or False)
        payment_term = (part.property_payment_term and
                        part.property_payment_term.id or False)
        fiscal_position = (part.property_account_position and
                           part.property_account_position.id or False)
        dedicated_salesman = part.user_id and part.user_id.id or uid
        if sale_order_ids:
            sale_order_id = sale_order_ids[0]
        else:
            projtype = simulation_cost.project_type_id
            simulation_number = sequence_obj.get_id(
                cr, uid, projtype.project_type_sequence_id.id)
            val = {'name': simulation_number,
                   'partner_id': fsource.res_partner_id.id,
                   'partner_invoice_id': addr['invoice'],
                   'partner_order_id': addr['contact'],
                   'partner_shipping_id': addr['delivery'],
                   'payment_term': payment_term,
                   'fiscal_position': fiscal_position,
                   'user_id': dedicated_salesman,
                   'simulation_cost_ids': [(6, 0, [simulation_cost.id])],
                   'project_financing_id': project_financing.id,
                   'financing_source_id': fsource.id,
                   'project2_id': simulation_cost.project_id.id,
                   'sale_type': 'modification'
                   }
            if pricelist:
                val['pricelist_id'] = pricelist
            # Grabo SALE.ORDER
            sale_order_id = sale_order_obj.create(cr, uid, val)
        # Creo la linea del pedido de venta
        product = product_obj.browse(cr, uid, line.product_sale_id.id)
        fpos = (fiscal_position and
                fposition_obj.browse(cr, uid, fiscal_position) or False)
        tax_id = fposition_obj.map_tax(cr, uid, fpos, product.taxes_id)
        # Busco el apunte de la fuente de financiacion
        if not simulation_cost.generate_by_lines:
            cond = [('name', 'like', ('Budgetary - ' +
                                      line.expense_area_id.name)),
                    ('type', '=', 'budgetary'),
                    ('expense_area_id', '=', line.expense_area_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', False),
                    ('simulation_cost_id', '=', simulation_cost.id)]
            analine_ids = analytic_line_obj.search(cr, uid, cond)
        else:
            cond = [('name', 'like', 'Budgetary - ' + line.product_id.name),
                    ('type', '=', 'budgetary'),
                    ('expense_area_id', '=', line.expense_area_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', line.id),
                    ('product_id', '=', line.product_id.id),
                    ('simulation_cost_id', '=', simulation_cost.id)]
            analine_ids = analytic_line_obj.search(cr, uid, cond)
            if not analine_ids:
                line_vals = {'name': 'Budgetary - ' + line.product_id.name,
                             'type': 'budgetary',
                             'expense_area_id': line.expense_area_id.id,
                             'account_id': w_cuenta_analitica,
                             'journal_id': w_journal_id,
                             'general_account_id': w_account_id,
                             'simulation_cost_line_id': line.id,
                             'product_id': line.product_id.id,
                             'simulation_cost_id': simulation_cost.id
                             }
                account_analytic_line_id = analytic_line_obj.create(cr, uid,
                                                                    line_vals)
                analine_ids = [account_analytic_line_id]
        if not analine_ids:
            if not simulation_cost.generate_by_lines:
                raise orm.except_orm(_('Sale Order Creation Error'),
                                     _('Budgetary analytic line not found for'
                                       ' %s expense area') %
                                     line.expense_area_id.name)
            else:
                raise orm.except_orm(_('Sale Order Creation Error'),
                                     _('Budgetary analytic line not found for'
                                       ' product: %s') % line.product_id.name)
        if not simulation_cost.generate_by_lines:
            cond = [('name', '=', project_financing.name),
                    ('type', '=', 'financing_source'),
                    ('expense_area_id', '=', line.expense_area_id.id),
                    ('project_financing_id', '=', project_financing.id),
                    ('account_analytic_line_budgetary_id', '=',
                     analine_ids[0]),
                    ('partner_id', '=', fsource.res_partner_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', False),
                    ('simulation_cost_id', '=', simulation_cost.id)]
            analytic_line_ids = analytic_line_obj.search(cr, uid, cond)
        else:
            line_vals = {'name': project_financing.name,
                         'type': 'financing_source',
                         'expense_area_id': line.expense_area_id.id,
                         'project_financing_id': project_financing.id,
                         'account_analytic_line_budgetary_id':
                         analine_ids[0],
                         'partner_id': fsource.res_partner_id.id,
                         'account_id': w_cuenta_analitica,
                         'journal_id': w_journal_id,
                         'general_account_id': w_account_id,
                         'simulation_cost_line_id': line.id,
                         'financing_percentage':
                         project_financing.project_percent,
                         'product_id': line.product_id.id,
                         'simulation_cost_id': simulation_cost.id
                         }
            analytic_line_id = analytic_line_obj.create(cr, uid, line_vals)
            analytic_line_ids = [analytic_line_id]
        if not analytic_line_ids:
            if not simulation_cost.generate_by_lines:
                raise orm.except_orm(_('Sale Order Creation Error'),
                                     _('Financing Source analytic line not '
                                       'found for %s expense area') %
                                     line.expense_area_id.name)
            else:
                raise orm.except_orm(_('Sale Order Creation Error'),
                                     _('Financing Source analytic line not '
                                       'found for product %s') %
                                     line.product_id.name)
        # Doy de alta la linea del pedido de venta
        w_imp = ((line.subtotal_purchase *
                  project_financing.project_percent) / 100)
        w_price_unit = ((line.sale_price *
                         project_financing.project_percent) / 100)
        values_line = {'product_id': line.product_sale_id.id,
                       'type': 'make_to_order',
                       'order_id': sale_order_id,
                       'name': line.product_sale_id.name,
                       'product_uom': product.uom_id.id,
                       'product_uom_qty': line.sale_amount,
                       'price_unit': w_price_unit,
                       'tax_id': [(6, 0, tax_id)],
                       'simulation_cost_line_id': line.id,
                       'account_analytic_id': w_cuenta_analitica,
                       'financial_source_line_id': analytic_line_ids[0],
                       'analytic_budgetary_line_id':
                       analine_ids[0],
                       'financied_amount': w_imp,
                       'financing_percentage':
                       project_financing.project_percent
                       }
        sale_order_line_id = pedido_linea_obj.create(cr, uid, values_line)
        # Actualizo la linea de simulacion con la linea del pedido de venta
        vals = {'sale_order_line_id': sale_order_line_id,
                'financied_line': True}
        simuline_obj.write(cr, uid, [line.id], vals)
        # Actualizo el fondo financiador con el codigo del pedido de venta, el
        # imorte que financia
        w_imp2 = project_financing.amount_awarded + w_imp
        vals = {'sale_order_id': sale_order_id,
                'amount_awarded': w_imp2,
                'grant': w_imp2}
        project_financing_obj.write(cr, uid, [project_financing.id], vals)
        return True

    def _create_sale_order_case6(self, cr, uid, project_financing,
                                 simulation_cost, line, w_cuenta_analitica,
                                 w_journal_id, w_account_id):
        analytic_line_obj = self.pool['account.analytic.line']
        sale_order_obj = self.pool['sale.order']
        pedido_linea_obj = self.pool['sale.order.line']
        product_obj = self.pool['product.product']
        simuline_obj = self.pool['simulation.cost.line']
        project_financing_obj = self.pool['project.financing']
        sequence_obj = self.pool['ir.sequence']
        partner_obj = self.pool['res.parnter']
        fposition_obj = self.pool['account.fiscal.position']
        # Valido que halla introducido un producto de venta
        if not line.product_sale_id:
            raise orm.except_orm(_('Sale Order Creation Error'),
                                 _('Purchase product %s, without product '
                                   'sales') % line.product_id.name)
        fsource = project_financing.financing_source_id
        cond = [('partner_id', '=', fsource.res_partner_id.id),
                ('project2_id', '=', simulation_cost.project_id.id),
                ('financing_source_id', '=', fsource.id),
                ('sale_type', '=', 'modification'),
                ('state', '=', 'draft')]
        sale_order_ids = sale_order_obj.search(cr, uid, cond)
        # Cojo los datos del cliente
        addr = partner_obj.address_get(
            cr, uid, [fsource.res_partner_id.id], ['delivery', 'invoice',
                                                   'contact'])
        part = partner_obj.browse(cr, uid, fsource.res_partner_id.id)
        pricelist = (part.property_product_pricelist and
                     part.property_product_pricelist.id or False)
        payment_term = (part.property_payment_term and
                        part.property_payment_term.id or False)
        fiscal_position = (part.property_account_position and
                           part.property_account_position.id or False)
        dedicated_salesman = part.user_id and part.user_id.id or uid
        if sale_order_ids:
            sale_order_id = sale_order_ids[0]
        else:
            projtype = simulation_cost.project_type_id
            simulation_number = sequence_obj.get_id(
                cr, uid, projtype.project_type_sequence_id.id)
            val = {'name': simulation_number,
                   'partner_id': fsource.res_partner_id.id,
                   'partner_invoice_id': addr['invoice'],
                   'partner_order_id': addr['contact'],
                   'partner_shipping_id': addr['delivery'],
                   'payment_term': payment_term,
                   'fiscal_position': fiscal_position,
                   'user_id': dedicated_salesman,
                   'simulation_cost_ids': [(6, 0, [simulation_cost.id])],
                   'project_financing_id': project_financing.id,
                   'financing_source_id': fsource.id,
                   'project2_id': simulation_cost.project_id.id,
                   'sale_type': 'modification'
                   }
            if pricelist:
                val['pricelist_id'] = pricelist
            # Grabo SALE.ORDER
            sale_order_id = sale_order_obj.create(cr, uid, val)
        # Creo la linea del pedido de venta
        product = product_obj.browse(cr, uid, line.product_sale_id.id)
        fpos = (fiscal_position and
                fposition_obj.browse(cr, uid, fiscal_position) or False)
        tax_id = fposition_obj.map_tax(cr, uid, fpos, product.taxes_id)
        # Busco el apunte de la fuente de financiacion
        if not simulation_cost.generate_by_lines:
            cond = [('name', 'like', ('Budgetary - ' +
                                      line.expense_area_id.name)),
                    ('type', '=', 'budgetary'),
                    ('expense_area_id', '=', line.expense_area_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', False),
                    ('simulation_cost_id', '=', simulation_cost.id)]
            analine_ids = analytic_line_obj.search(cr, uid, cond)
        else:
            cond = [('name', 'like', 'Budgetary - ' + line.product_id.name),
                    ('type', '=', 'budgetary'),
                    ('expense_area_id', '=', line.expense_area_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', line.id),
                    ('product_id', '=', line.product_id.id),
                    ('simulation_cost_id', '=', simulation_cost.id)]
            analine_ids = analytic_line_obj.search(cr, uid, cond)
            if not analine_ids:
                line_vals = {'name': 'Budgetary - ' + line.product_id.name,
                             'type': 'budgetary',
                             'expense_area_id': line.expense_area_id.id,
                             'account_id': w_cuenta_analitica,
                             'journal_id': w_journal_id,
                             'general_account_id': w_account_id,
                             'simulation_cost_line_id': line.id,
                             'product_id': line.product_id.id,
                             'simulation_cost_id': simulation_cost.id
                             }
                account_analytic_line_id = analytic_line_obj.create(cr, uid,
                                                                    line_vals)
                analine_ids = [account_analytic_line_id]
        if not analine_ids:
            if not simulation_cost.generate_by_lines:
                raise orm.except_orm(_('Sale Order Creation Error'),
                                     _('Budgetary analytic line not found for'
                                       ' %s expense area') %
                                     line.expense_area_id.name)
            else:
                raise orm.except_orm(_('Sale Order Creation Error'),
                                     _('Budgetary analytic line not found for'
                                       ' product: %s') % line.product_id.name)
        if not simulation_cost.generate_by_lines:
            cond = [('name', '=', (project_financing.name + ' - ' +
                                   line.expense_area_id.name)),
                    ('type', '=', 'financing_source'),
                    ('expense_area_id', '=', line.expense_area_id.id),
                    ('project_financing_id', '=', project_financing.id),
                    ('account_analytic_line_budgetary_id', '=',
                     analine_ids[0]),
                    ('partner_id', '=', fsource.res_partner_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', False),
                    ('simulation_cost_id', '=', simulation_cost.id)]
            analytic_line_ids = analytic_line_obj.search(cr, uid, cond)
        else:
            line_vals = {'name': (project_financing.name + ' - ' +
                                  line.product_id.name + ' - ' +
                                  line.expense_area_id.name),
                         'type': 'financing_source',
                         'expense_area_id': line.expense_area_id.id,
                         'project_financing_id': project_financing.id,
                         'account_analytic_line_budgetary_id':
                         analine_ids[0],
                         'partner_id': fsource.res_partner_id.id,
                         'account_id': w_cuenta_analitica,
                         'journal_id': w_journal_id,
                         'general_account_id': w_account_id,
                         'simulation_cost_line_id': line.id,
                         'financing_percentage':
                         project_financing.project_percent,
                         'product_id': line.product_id.id,
                         'simulation_cost_id': simulation_cost.id
                         }
            analytic_line_id = analytic_line_obj.create(cr, uid, line_vals)
            analytic_line_ids = [analytic_line_id]
        if not analytic_line_ids:
            if not simulation_cost.generate_by_lines:
                raise orm.except_orm(_('Sale Order Creation Error'),
                                     _('Financing Source analytic line not '
                                       'found for %s expense area') %
                                     line.expense_area_id.name)
            else:
                raise orm.except_orm(_('Sale Order Creation Error'),
                                     _('Financing Source analytic line not '
                                       'found for product %s') %
                                     line.product_id.name)
        # Doy de alta la linea del pedido de venta
        w_imp = ((line.subtotal_purchase *
                  project_financing.project_percent) / 100)
        w_price_unit = ((line.sale_price *
                         project_financing.project_percent) / 100)
        values_line = {'product_id': line.product_sale_id.id,
                       'type': 'make_to_order',
                       'order_id': sale_order_id,
                       'name': line.product_sale_id.name,
                       'product_uom': product.uom_id.id,
                       'product_uom_qty': line.sale_amount,
                       'price_unit': w_price_unit,
                       'tax_id': [(6, 0, tax_id)],
                       'simulation_cost_line_id': line.id,
                       'account_analytic_id': w_cuenta_analitica,
                       'financial_source_line_id': analytic_line_ids[0],
                       'analytic_budgetary_line_id':
                       analine_ids[0],
                       'financied_amount': w_imp,
                       'financing_percentage':
                       project_financing.project_percent
                       }
        sale_order_line_id = pedido_linea_obj.create(cr, uid, values_line)
        # Actualizo la linea de simulacion con la linea del pedido de venta
        vals = {'sale_order_line_id': sale_order_line_id,
                'financied_line': True}
        simuline_obj.write(cr, uid, [line.id], vals)
        # Actualizo el fondo financiador con el codigo del pedido de venta,
        # el imorte que financia
        w_imp2 = project_financing.amount_awarded + w_imp
        vals = {'sale_order_id': sale_order_id,
                'amount_awarded': w_imp2,
                'grant': w_imp2}
        project_financing_obj.write(cr, uid, [project_financing.id], vals)
        return True

    def action_financing(self, cr, uid, ids):
        project_obj = self.pool['project.project']
        account_journal_obj = self.pool['account.analytic.journal']
        account_account_obj = self.pool['account.account']
        analytic_line_obj = self.pool['account.analytic.line']
        simuline_obj = self.pool['simulation.cost.line']
        picking_obj = self.pool['stock.picking']
        move_obj = self.pool['stock.move']
        sale_line_obj = self.pool['sale.order.line']
        account_analytic_account_obj = self.pool['account.analytic.account']
        sale_obj = self.pool['sale.order']
        # Cojo el diario analítico
        cond = [('name', 'like', 'Presupuestarias')]
        account_journal_ids = account_journal_obj.search(cr, uid, cond)
        if not account_journal_ids:
            raise orm.except_orm(_('Financing Error'),
                                 _('Journal with Presupuestarias literal NOT '
                                   'FOUND'))
        # Cojo la cuenta general
        cond = [('name', 'like', 'Your Company')]
        account_account_ids = account_account_obj.search(cr, uid, cond)
        if not account_account_ids:
            raise orm.except_orm(_('Financing Error'),
                                 _('General Account YOUR COMPANY not found'))
        if ids:
            for simulation_cost_id in ids:
                simulation_cost = self.browse(cr, uid, simulation_cost_id)
                # Si la simulación estaba abierta, y se pasa a open
                if simulation_cost.state == 'open':
                    if simulation_cost.project_id.sum_expense_request > 0:
                        raise orm.except_orm(_('Error'),
                                             _('Project with imputations'))
                    # Borro los pedidos de venta
                    if simulation_cost.sale_order_ids:
                        for sale_order in simulation_cost.sale_order_ids:
                            if sale_order.picking_ids:
                                for picking in sale_order.picking_ids:
                                    if picking.move_lines:
                                        for move_line in picking.move_lines:
                                            move_obj.action_cancel(
                                                cr, uid, [move_line.id])
                                            vals = {'state': 'draft'}
                                            move_obj.write(
                                                cr, uid, [move_line.id], vals)
                                            move_obj.unlink(
                                                cr, uid, [move_line.id])
                                    vals = {'state': 'draft'}
                                    picking_obj.write(
                                        cr, uid, [picking.id], vals)
                                    picking_obj.unlink(
                                        cr, uid, [picking.id])
                            if sale_order.order_line:
                                for order_line in sale_order.order_line:
                                    sale_line_obj.button_cancel(
                                        cr, uid, [order_line.id])
                                    sale_line_obj.unlink(
                                        cr, uid, [order_line.id])
                            workflow.trg_validate(uid, 'sale.order',
                                                  sale_order.id, 'cancel', cr)
                            sale_obj.unlink(cr, uid, [sale_order.id])
                    # Borro Lineas de Analitica
                    if not simulation_cost.use_project_id:
                        proj = simulation_cost.project_id
                        cond = [('account_id', '=',
                                 proj.analytic_account_id.id),
                                ('type', '!=', 'budgetary')]
                        account_line_ids = analytic_line_obj.search(cr, uid,
                                                                    cond)
                        if account_line_ids:
                            analytic_line_obj.unlink(cr, uid, account_line_ids)
                    else:
                        # Borro las líneas de analitica para esta simulacion
                        cond = [('simulation_cost_id', '=',
                                 simulation_cost.id),
                                ('type', '!=', 'budgetary')]
                        analytic_line_ids = analytic_line_obj.search(cr, uid,
                                                                     cond)
                        if analytic_line_ids:
                            analytic_line_obj.unlink(cr, uid,
                                                     analytic_line_ids)
                    # Marco las lineas de la simulacion como no tratadas
                    cond = [('simulation_cost_id', '=', simulation_cost.id)]
                    simulation_line_ids = simuline_obj.search(cr, uid, cond)
                    if simulation_line_ids:
                        vals = {'financied_line': False,
                                'sale_order_line_id': False}
                        simuline_obj.write(cr, uid, simulation_line_ids, vals)
                else:
                    # Si no existe el proyecto lo creo
                    if not simulation_cost.project_id:
                        if not simulation_cost.use_project_id:
                            # DOY DE ALTA EL PROYECTO
                            my_year = int(str(time.strftime('%Y')))
                            if not simulation_cost.project_type_id:
                                raise orm.except_orm(_('Project Creation '
                                                       'Error'),
                                                     _('Simulation Cost '
                                                       'WITHOUT PROJECT TYPE'))
                            else:
                                projtype = simulation_cost.project_type_id
                                if not projtype.project_type_sequence_id:
                                    raise orm.except_orm(_('Project Creation '
                                                           'Error'),
                                                         _('Project Type WITHO'
                                                           'UT SEQUENCE'))
                            simu = simulation_cost
                            line = {'project_code': simu.simulation_number,
                                    'name': simulation_cost.name,
                                    'date_start': time.strftime('%Y-%m-%d'),
                                    'final_partner_id':
                                    simu.final_partner_id.id,
                                    'department_id': simu.department_id.id,
                                    'crm_case_resource_type_id':
                                    simu.crm_case_resource_type_id.id,
                                    'project_type_id': simu.project_type_id.id,
                                    'project_activity_id':
                                    simu.project_activity_id.id,
                                    'project_subactivity_id':
                                    simu.project_subactivity_id.id,
                                    'administration_id':
                                    simu.administration_id.id,
                                    'type_program_id': simu.type_program_id.id,
                                    'project_research_line_id':
                                    simu.project_research_line_id.id,
                                    'project_research_subline_id':
                                    simu.project_research_subline_id.id,
                                    'project_pyramid_test_id':
                                    simu.project_pyramid_test_id.id,
                                    'project_aeronautical_program_id':
                                    simu.project_aeronautical_program_id.id,
                                    'project_location_id':
                                    simu.project_location_id.id,
                                    'sector_id': simulation_cost.sector_id.id,
                                    'subsector_id':
                                    simu.subsector_id.id,
                                    'resume': simulation_cost.resume,
                                    'project_year': my_year,
                                    'deductible_iva': simu.deductible_iva,
                                    'simulation_cost_id': simulation_cost.id
                                    }
                            if simulation_cost.parent_project_id:
                                parent = simu.parent_project_id
                                line.update({'parent_id':
                                             parent.analytic_account_id.id,
                                             'parent_project_id': parent.id})
                            project_project_id = project_obj.create(cr, uid,
                                                                    line)
                            # Actualizo la cuenta analitica que se ha dado de
                            # alta automaticamente al crear el proyecto
                            proj = project_obj.browse(cr, uid,
                                                      project_project_id)
                            w_cuenta_analitica = proj.analytic_account_id.id
                            if not simulation_cost.parent_project_id:
                                simu = simulation_cost
                                vals = {'name': simulation_cost.name,
                                        'code': simu.simulation_number,
                                        'state': 'open',
                                        'estimated_balance': 0,
                                        'estimated_cost': 0,
                                        'estimated_sale': 0,
                                        }
                                account_analytic_account_obj.write(
                                    cr, uid, [w_cuenta_analitica], vals)
                            else:
                                parent = simulation_cost.parent_project_id
                                vals = {'name': simulation_cost.name,
                                        'code':
                                        simulation_cost.simulation_number,
                                        'parent_id':
                                        parent.analytic_account_id.id,
                                        'state': 'open',
                                        'estimated_balance': 0,
                                        'estimated_cost': 0,
                                        'estimated_sale': 0,
                                        }
                                account_analytic_account_obj.write(
                                    cr, uid, [w_cuenta_analitica], vals)
                        else:
                            if simulation_cost.use_project_id:
                                simproj = simulation_cost.use_project_id
                                aaccoun = simproj.analytic_account_id
                                project_project_id = simproj.id
                                w_cuenta_analitica = aaccoun.id
                        # Actualizo la simulacion de costes con el proyecto
                        # creado
                        vals = {'project_id': project_project_id}
                        self.write(cr, uid, [simulation_cost.id], vals)
                        # Por cada pestaña del simulador que tenga lineas de
                        # simulación, creo una partida presupuestaria
                        if simulation_cost.others_cost_lines_ids:
                            for line in simulation_cost.others_cost_lines_ids:
                                self._create_budgetary(
                                    cr, uid, simulation_cost.generate_by_lines,
                                    line.expense_area_id.name,
                                    line.expense_area_id.id,
                                    w_cuenta_analitica,
                                    account_journal_ids[0],
                                    account_account_ids[0],
                                    line.product_id.name, line.id,
                                    simulation_cost.id)
                        if simulation_cost.amortization_cost_lines_ids:
                            simu = simulation_cost
                            for line in simu.amortization_cost_lines_ids:
                                self._create_budgetary(
                                    cr, uid, simulation_cost.generate_by_lines,
                                    line.expense_area_id.name,
                                    line.expense_area_id.id,
                                    w_cuenta_analitica,
                                    account_journal_ids[0],
                                    account_account_ids[0],
                                    line.product_id.name, line.id,
                                    simulation_cost.id)
        self.write(cr, uid, ids, {'state': 'financing'})
        return True

    def _create_budgetary(self, cr, uid, w_generate_by_lines, w_area_name,
                          w_area_id, w_cuenta_analitica, w_journal_id,
                          w_account_id, w_product_name, w_line_id,
                          w_simulation_cost_id):
        simulation_line_obj = self.pool['simulation.cost.line']
        analytic_line_obj = self.pool['account.analytic.line']
        if not w_generate_by_lines:
            cond = [('name', 'like', 'Budgetary - ' + w_area_name),
                    ('type', '=', 'budgetary'),
                    ('expense_area_id', '=', w_area_id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', False),
                    ('simulation_cost_id', '=', w_simulation_cost_id)]
            analine_ids = analytic_line_obj.search(cr, uid, cond)
            if not analine_ids:
                line_vals = {'name': 'Budgetary - ' + w_area_name,
                             'type': 'budgetary',
                             'expense_area_id': w_area_id,
                             'account_id': w_cuenta_analitica,
                             'journal_id': w_journal_id,
                             'general_account_id': w_account_id,
                             'simulation_cost_line_id': False,
                             'simulation_cost_id': w_simulation_cost_id
                             }
                analytic_line_obj.create(cr, uid, line_vals)
        else:
            line = simulation_line_obj.browse(cr, uid, w_line_id)
            line_vals = {'name': 'Budgetary - ' + w_product_name,
                         'type': 'budgetary',
                         'expense_area_id': w_area_id,
                         'account_id': w_cuenta_analitica,
                         'journal_id': w_journal_id,
                         'general_account_id': w_account_id,
                         'simulation_cost_line_id': w_line_id,
                         'product_id': line.product_id.id,
                         'simulation_cost_id': w_simulation_cost_id
                         }
            analytic_line_obj.create(cr, uid, line_vals)
        return True

    def action_open(self, cr, uid, ids):
        project_project_obj = self.pool['project.project']
        account_journal_obj = self.pool['account.analytic.journal']
        account_account_obj = self.pool['account.account']
        projfinancing_obj = self.pool['project.financing']
        financing_source_obj = self.pool['financing.source']
        # Cojo el diario analítico
        cond = [('name', 'like', 'Presupuestarias')]
        account_analytic_journal_ids = account_journal_obj.search(cr, uid,
                                                                  cond)
        if not account_analytic_journal_ids:
            raise orm.except_orm(_('Process Error'),
                                 _('Journal with Presupuestarias literal NOT '
                                   'FOUND'))
        # Cojo la cuenta general
        cond = [('name', 'like', 'Your Company')]
        account_account_ids = account_account_obj.search(cr, uid, cond)
        if not account_account_ids:
            raise orm.except_orm(_('Proces Error'),
                                 _('General Account YOUR COMPANY not found'))
        if ids:
            for simulation_cost_id in ids:
                simulation_cost = self.browse(cr, uid, simulation_cost_id)
                # Control de Fuentes de Financiación, para ver si pueden
                # financiar importes de compra.
                if simulation_cost.others_cost_lines_ids:
                    # Si se ha definido una nueva fuente de financiación, que
                    # no estaba definida desde un principio, doy de alta un
                    # apunte analitico de tipo FINANCIAL_SOURCE
                    if simulation_cost.state == 'inmodif_budgetary':
                        self._action_open_inmodif_budgetary(
                            cr, uid, simulation_cost,
                            account_analytic_journal_ids, account_account_ids)
                    if (simulation_cost.state == 'inmodif_budgetary' and
                            simulation_cost.financing_source_ids):
                        self._action_open_inmodif_budgetary_fsource(
                            cr, uid, simulation_cost,
                            account_analytic_journal_ids, account_account_ids)
                    # Trato líneas de simulación
                    datas = {}
                    for line in simulation_cost.others_cost_lines_ids:
                        if (line.project_financing_id and not
                                line.financied_line):
                            percen = line.project_financing_id.project_percent
                            w_imp = (line.subtotal_purchase * percen) / 100
                            w_found = 0
                            for data in datas:
                                datarray = datas[data]
                                fsource_id = datarray['financing_source_id']
                                amount = datarray['amount']
                                projfinac = line.project_financing_id
                                fsource2_id = projfinac.financing_source_id.id
                                if fsource_id == fsource2_id:
                                    w_found = 1
                                    amount = amount + w_imp
                                    datas[data].update({'amount': amount})
                            if w_found == 0:
                                vals = {'financing_source_id': fsource2_id,
                                        'amount': w_imp}
                                datas[(fsource2_id)] = vals
                        else:
                            if (not line.project_financing_id and not
                                    line.financied_line):
                                with_area = True
                                # BUSCO FONDOS FINANCIADORES QUE FINANCIEN EL
                                # AREA DE GASTO DE LA LINEA DE SIMULACION
                                cond = [('simulation_cost_id', '=',
                                         simulation_cost.id),
                                        ('expense_area_id', '=',
                                         line.expense_area_id.id)]
                                pfinancing_ids = projfinancing_obj.search(
                                    cr, uid, cond)
                                if not pfinancing_ids:
                                    with_area = False
                                    # BUSCO FONDOS FINANCIADORES QUE FINANCIEN
                                    # TODAS LAS AREAS DE GASTO
                                    cond = [('simulation_cost_id', '=',
                                             simulation_cost.id),
                                            ('expense_area_id', '=',
                                             False)]
                                    pfinancing_ids = projfinancing_obj.search(
                                        cr, uid, cond)
                                # TRATO LOS FONDOS FINANCIADORES
                                if pfinancing_ids:
                                    for pfinancing in projfinancing_obj.browse(
                                            cr, uid, pfinancing_ids):
                                        w_imp = ((line.subtotal_purchase *
                                                  pfinancing.project_percent) /
                                                 100)
                                        w_found = 0
                                        f2 = pfinancing.financing_source_id
                                        for data in datas:
                                            datarray = datas[data]
                                            f = datarray['financing_source_id']
                                            amount = datarray['amount']
                                            if f == f2.id:
                                                w_found = 1
                                                amount = amount + w_imp
                                                vals = {'amount': amount}
                                                datas[data].update(vals)
                                        if w_found == 0:
                                            vals = {'financing_source_id':
                                                    f2.id,
                                                    'amount': w_imp}
                                            datas[(f2.id)] = vals
                    if datas:
                        for data in datas:
                            datarray = datas[data]
                            fs_id = datarray['financing_source_id']
                            amount = datarray['amount']
                            financing_source = financing_source_obj.browse(
                                cr, uid, fs_id)
                            if financing_source.availability_fund == 'granted':
                                if amount > financing_source.grant:
                                    name1 = financing_source.name
                                    grant = financing_source.grant
                                    raise orm.except_orm(_('Financing Source '
                                                           'ERROR'),
                                                         _("The Financing Sour"
                                                           "ce '%s', only have"
                                                           " an amount availab"
                                                           "le for %s euros an"
                                                           "d can not finance"
                                                           " %s euros") %
                                                         (name1, grant,
                                                          amount,))
                            if (financing_source.availability_fund ==
                                    'accepted'):
                                if (amount >
                                    (financing_source.total_recognized +
                                     financing_source.transfered)):
                                    name1 = financing_source.name
                                    sum = (financing_source.total_recognized +
                                           financing_source.transfered)
                                    raise orm.except_orm(_('Financing Source '
                                                           'ERROR'),
                                                         _("The Financing Sour"
                                                           "ce '%s', only have"
                                                           " an amount availab"
                                                           "le for %s euros an"
                                                           "d can not finance "
                                                           "%s euros") %
                                                         (name1, sum, amount,))
                            if financing_source.availability_fund == 'charged':
                                if (amount >
                                    (financing_source.total_invoices_billed +
                                     financing_source.transfered)):
                                    name1 = financing_source.name
                                    fs = financing_source
                                    sum = (fs.total_invoices_billed +
                                           fs.transfered)
                                    raise orm.except_orm(_('Financing Source '
                                                           'ERROR'),
                                                         _("The Financing Sour"
                                                           "ce '%s', only have"
                                                           " an amount availab"
                                                           "le for %s euros an"
                                                           "d can not finance "
                                                           "%s euros") %
                                                         (name1, sum, amount,))
                if simulation_cost.state == 'financing':
                    project = project_project_obj.browse(
                        cr, uid, simulation_cost.project_id.id)
                    w_cuenta_analitica = project.analytic_account_id.id
                    # TRATAMIENTO PARA FONDOS FINANCIADORES DEFINIDOS EN LA
                    # PROPIA LINEA DE SIMULACION
                    # Trato lineas de tipo OTHERS de la simulacion de costes
                    # , y doy de alta el apunte MODIF. FINANCIERA
                    if simulation_cost.others_cost_lines_ids:
                        for line in simulation_cost.others_cost_lines_ids:
                            if (line.project_financing_id and not
                                    line.financied_line):
                                self._create_financial_source(
                                    cr, uid, simulation_cost, line,
                                    w_cuenta_analitica,
                                    account_analytic_journal_ids[0],
                                    account_account_ids[0])
                    # Trato lineas de tipo AMORTIZATION de la simulacion de
                    # costes, y doy de alta el apunte MODIF. FINANCIERA
                    if simulation_cost.amortization_cost_lines_ids:
                        simu = simulation_cost
                        for line in simu.amortization_cost_lines_ids:
                            if (line.project_financing_id and not
                                    line.financied_line):
                                self._create_financial_source(
                                    cr, uid, simulation_cost, line,
                                    w_cuenta_analitica,
                                    account_analytic_journal_ids[0],
                                    account_account_ids[0])
                    # TRATAMIENTO PARA FONDOS FINANCIADORES NO DEFINIDOS EN LA
                    # PROPIA LINEA DE SIMULACION
                    # Trato lineas de tipo OTHERS de la simulacion de costes,
                    # y doy de alta el apunte MODIF. FINANCIERA
                    if simulation_cost.others_cost_lines_ids:
                        for line in simulation_cost.others_cost_lines_ids:
                            if (not line.project_financing_id and not
                                    line.financied_line):
                                with_area = True
                                # BUSCO FONDOS FINANCIADORES QUE FINANCIEN EL
                                # AREA DE GASTO DE LA LINEA DE SIMULACION
                                c = [('simulation_cost_id', '=',
                                      simulation_cost.id),
                                     ('expense_area_id', '=',
                                      line.expense_area_id.id)]
                                projfinanc_ids = projfinancing_obj.search(
                                    cr, uid, c)
                                if not projfinanc_ids:
                                    with_area = False
                                    # BUSCO FONDOS FINANCIADORES QUE FINANCIEN
                                    # TODAS LAS AREAS DE GASTO
                                    c = [('simulation_cost_id', '=',
                                          simulation_cost.id),
                                         ('expense_area_id', '=', False)]
                                    projfinanc_ids = projfinancing_obj.search(
                                        cr, uid, c)
                                # TRATO LOS FONDOS FINANCIADORES
                                if projfinanc_ids:
                                    for pfinancing in projfinancing_obj.browse(
                                            cr, uid, projfinanc_ids):
                                        self._create_financial_source2(
                                            cr, uid, with_area, pfinancing,
                                            simulation_cost, line,
                                            w_cuenta_analitica,
                                            account_analytic_journal_ids[0],
                                            account_account_ids[0])
                    # Trato lineas de tipo AMORTIZATIONS de la simulacion de
                    # costes, y doy de alta el apunte MODIF. FINANCIERA
                    if simulation_cost.amortization_cost_lines_ids:
                        simu = simulation_cost
                        for line in simu.amortization_cost_lines_ids:
                            if (not line.project_financing_id and not
                                    line.financied_line):
                                with_area = True
                                # BUSCO FONDOS FINANCIADORES QUE FINANCIEN EL
                                # AREA DE GASTO DE LA LINEA DE SIMULACION
                                c = [('simulation_cost_id', '=',
                                      simulation_cost.id),
                                     ('expense_area_id', '=',
                                      line.expense_area_id.id)]
                                projfinanc_ids = projfinancing_obj.search(
                                    cr, uid, c)
                                if not projfinanc_ids:
                                    with_area = False
                                    # BUSCO FONDOS FINANCIADORES QUE FINANCIEN
                                    # TODAS LAS AREAS DE GASTO
                                    c = [('simulation_cost_id', '=',
                                          simulation_cost.id),
                                         ('expense_area_id', '=', False)]
                                    projfinanc_ids = projfinancing_obj.search(
                                        cr, uid, c)
                                # TRATO LOS FONDOS FINANCIADORES
                                if projfinanc_ids:
                                    for pfinancing in projfinancing_obj.browse(
                                            cr, uid, projfinanc_ids):
                                        self._create_financial_source2(
                                            cr, uid, with_area, pfinancing,
                                            simulation_cost, line,
                                            w_cuenta_analitica,
                                            account_analytic_journal_ids[0],
                                            account_account_ids[0])
        # Creo el pedido de venta
        self.button_create_sale_order(cr, uid, ids)
        # Pongo la simulación en estado OPEN
        self.write(cr, uid, ids, {'state': 'open'})
        return True

    def _action_open_inmodif_budgetary(self, cr, uid, simulation_cost,
                                       account_analytic_journal_ids,
                                       account_account_ids):
        project_project_obj = self.pool['project.project']
        account_line_obj = self.pool['account.analytic.line']
        for line in simulation_cost.others_cost_lines_ids:
            if line.project_financing_id and not line.financied_line:
                project = project_project_obj.browse(
                    cr, uid, simulation_cost.project_id.id)
                w_cuenta_analitica = project.analytic_account_id.id
                w_journal_id = account_analytic_journal_ids[0]
                w_account_id = account_account_ids[0]
                if not simulation_cost.generate_by_lines:
                    cond = [('name', 'like', ('Budgetary - ' +
                                              line.expense_area_id.name)),
                            ('type', '=', 'budgetary'),
                            ('expense_area_id', '=', line.expense_area_id.id),
                            ('account_id', '=', w_cuenta_analitica),
                            ('journal_id', '=', w_journal_id),
                            ('general_account_id', '=', w_account_id),
                            ('simulation_cost_line_id', '=', False),
                            ('simulation_cost_id', '=', simulation_cost.id)]
                else:
                    cond = [('name', 'like', ('Budgetary - ' +
                                              line.product_id.name)),
                            ('type', '=', 'budgetary'),
                            ('expense_area_id', '=', line.expense_area_id.id),
                            ('account_id', '=', w_cuenta_analitica),
                            ('journal_id', '=', w_journal_id),
                            ('general_account_id', '=', w_account_id),
                            ('simulation_cost_line_id', '=', line.id),
                            ('product_id', '=', line.product_id.id),
                            ('simulation_cost_id', '=', simulation_cost.id)]
                account_analytic_line_ids = account_line_obj.search(cr, uid,
                                                                    cond)
                if not account_analytic_line_ids:
                    if not simulation_cost.generate_by_lines:
                        raise orm.except_orm(_('Process Error'),
                                             _('Budgetary analytic line not '
                                               'found for %s expense area') %
                                             line.expense_area_id.name)
                    else:
                        raise orm.except_orm(_('Process Error'),
                                             _('Budgetary analytic line not '
                                               'found for product: %s') %
                                             line.product_id.name)
                fsource = line.project_financing_id.financing_source_id
                if not simulation_cost.generate_by_lines:
                    cond = [('name', '=', (line.project_financing_id.name +
                                           ' - ' + line.expense_area_id.name)),
                            ('type', '=', 'financing_source'),
                            ('expense_area_id', '=', line.expense_area_id.id),
                            ('project_financing_id', '=',
                             line.project_financing_id.id),
                            ('account_analytic_line_budgetary_id', '=',
                             account_analytic_line_ids[0]),
                            ('partner_id', '=', fsource.res_partner_id.id),
                            ('account_id', '=', w_cuenta_analitica),
                            ('journal_id', '=', w_journal_id),
                            ('general_account_id', '=', w_account_id),
                            ('simulation_cost_line_id', '=', False),
                            ('simulation_cost_id', '=', simulation_cost.id),
                            ('financing_source_id', '=', fsource.id)]
                else:
                    cond = [('name', '=', (line.project_financing_id.name +
                                           ' - ' + line.product_id.name)),
                            ('type', '=', 'financing_source'),
                            ('expense_area_id', '=', line.expense_area_id.id),
                            ('project_financing_id', '=',
                             line.project_financing_id.id),
                            ('account_analytic_line_budgetary_id', '=',
                             account_analytic_line_ids[0]),
                            ('partner_id', '=', fsource.res_partner_id.id),
                            ('account_id', '=', w_cuenta_analitica),
                            ('journal_id', '=', w_journal_id),
                            ('general_account_id', '=', w_account_id),
                            ('simulation_cost_line_id', '=', line.id),
                            ('product_id', '=', line.product_id.id),
                            ('simulation_cost_id', '=', simulation_cost.id),
                            ('financing_source_id', '=', fsource.id)]
                analytic_line_ids = account_line_obj.search(cr, uid, cond)
                if not analytic_line_ids:
                    if not simulation_cost.generate_by_lines:
                        line_vals = {'name': (line.project_financing_id.name +
                                              ' - ' +
                                              line.expense_area_id.name),
                                     'type': 'financing_source',
                                     'expense_area_id':
                                     line.expense_area_id.id,
                                     'project_financing_id':
                                     line.project_financing_id.id,
                                     'account_analytic_line_budgetary_id':
                                     account_analytic_line_ids[0],
                                     'partner_id': fsource.res_partner_id.id,
                                     'account_id': w_cuenta_analitica,
                                     'journal_id': w_journal_id,
                                     'general_account_id': w_account_id,
                                     'simulation_cost_line_id': False,
                                     'financing_percentage': 100,
                                     'simulation_cost_id': simulation_cost.id,
                                     'financing_source_id': fsource.id
                                     }
                    else:
                        line_vals = {'name': (line.project_financing_id.name +
                                              ' - ' + line.product_id.name),
                                     'type': 'financing_source',
                                     'expense_area_id':
                                     line.expense_area_id.id,
                                     'project_financing_id':
                                     line.project_financing_id.id,
                                     'account_analytic_line_budgetary_id':
                                     account_analytic_line_ids[0],
                                     'partner_id': fsource.res_partner_id.id,
                                     'account_id': w_cuenta_analitica,
                                     'journal_id': w_journal_id,
                                     'general_account_id': w_account_id,
                                     'simulation_cost_line_id': line.id,
                                     'financing_percentage': 100,
                                     'product_id': line.product_id.id,
                                     'simulation_cost_id': simulation_cost.id,
                                     'financing_source_id': fsource.id
                                     }
                    account_line_obj.create(cr, uid, line_vals)
        return True

    def _action_open_inmodif_budgetary_fsource(self, cr, uid, simulation_cost,
                                               account_analytic_journal_ids,
                                               account_account_ids):
        project_project_obj = self.pool['project.project']
        acc_line_obj = self.pool['account.analytic.line']
        for financing in simulation_cost.financing_source_ids:
            if not financing.treaty:
                for line in simulation_cost.others_cost_lines_ids:
                    project = project_project_obj.browse(
                        cr, uid, simulation_cost.project_id.id)
                    w_cuenta_analitica = project.analytic_account_id.id
                    w_journal_id = account_analytic_journal_ids[0]
                    w_account_id = account_account_ids[0]
                    if not line.project_financing_id:
                        w_found = 0
                        if not financing.expense_area_id:
                            w_found = 1
                        else:
                            if (financing.expense_area_id ==
                                    line.expense_area_id.id):
                                w_found = 1
                        if w_found == 1:
                            if not simulation_cost.generate_by_lines:
                                area_name = line.expense_area_id.name
                                cond = [('name', 'like', ('Budgetary - ' +
                                                          area_name)),
                                        ('type', '=', 'budgetary'),
                                        ('expense_area_id', '=',
                                         line.expense_area_id.id),
                                        ('account_id', '=',
                                         w_cuenta_analitica),
                                        ('journal_id', '=',
                                         w_journal_id),
                                        ('general_account_id', '=',
                                         w_account_id),
                                        ('simulation_cost_line_id', '=',
                                         False),
                                        ('simulation_cost_id', '=',
                                         simulation_cost.id)]
                            else:
                                product_name = line.product_id.name
                                cond = [('name', 'like', ('Budgetary - ' +
                                                          product_name)),
                                        ('type', '=', 'budgetary'),
                                        ('expense_area_id', '=',
                                         line.expense_area_id.id),
                                        ('account_id', '=',
                                         w_cuenta_analitica),
                                        ('journal_id', '=',
                                         w_journal_id),
                                        ('general_account_id', '=',
                                         w_account_id),
                                        ('simulation_cost_line_id', '=',
                                         line.id),
                                        ('product_id', '=',
                                         line.product_id.id),
                                        ('simulation_cost_id', '=',
                                         simulation_cost.id)]
                            aanalytic_line_ids = acc_line_obj.search(
                                cr, uid, cond)
                            if not aanalytic_line_ids:
                                if not simulation_cost.generate_by_lines:
                                    lit = _('Budgetary analytic line not found'
                                            ' for %s expense area')
                                    raise orm.except_orm(_('Process Error'),
                                                         lit % area_name)
                                else:
                                    lit = _('Budgetary analytic line not found'
                                            ' for product: %s')
                                    raise orm.except_orm(_('Process Error'),
                                                         lit % product_name)
                            if not financing.expense_area_id:
                                fsource = financing.financing_source_id
                                if not simulation_cost.generate_by_lines:
                                    cond = [('name', '=', financing.name),
                                            ('type', '=', 'financing_source'),
                                            ('expense_area_id', '=',
                                             line.expense_area_id.id),
                                            ('project_financing_id', '=',
                                             financing.id),
                                            ('account_analytic_line_budgetary'
                                             '_id', '=',
                                             aanalytic_line_ids[0]),
                                            ('partner_id', '=',
                                             fsource.res_partner_id.id),
                                            ('account_id', '=',
                                             w_cuenta_analitica),
                                            ('journal_id', '=',
                                             w_journal_id),
                                            ('general_account_id', '=',
                                             w_account_id),
                                            ('simulation_cost_line_id', '=',
                                             False),
                                            ('simulation_cost_id', '=',
                                             simulation_cost.id),
                                            ('financing_source_id', '=',
                                             fsource.id)]
                                else:
                                    cond = [('name', '=', financing.name),
                                            ('type', '=', 'financing_source'),
                                            ('expense_area_id', '=',
                                             line.expense_area_id.id),
                                            ('project_financing_id', '=',
                                             financing.id),
                                            ('account_analytic_line_budgetary_'
                                             'id', '=', aanalytic_line_ids[0]),
                                            ('partner_id', '=',
                                             fsource.res_partner_id.id),
                                            ('account_id', '=',
                                             w_cuenta_analitica),
                                            ('journal_id', '=',
                                             w_journal_id),
                                            ('general_account_id', '=',
                                             w_account_id),
                                            ('simulation_cost_line_id', '=',
                                             line.id),
                                            ('product_id', '=',
                                             line.product_id.id),
                                            ('simulation_cost_id', '=',
                                             simulation_cost.id),
                                            ('financing_source_id', '=',
                                             fsource.id)]
                                analytic_line_ids = acc_line_obj.search(
                                    cr, uid, cond)
                                if not analytic_line_ids:
                                    if not simulation_cost.generate_by_lines:
                                        line_vals = {'name': financing.name,
                                                     'type':
                                                     'financing_source',
                                                     'expense_area_id':
                                                     line.expense_area_id.id,
                                                     'project_financing_id':
                                                     financing.id,
                                                     'account_analytic_line_bu'
                                                     'dgetary_id':
                                                     aanalytic_line_ids[0],
                                                     'partner_id':
                                                     fsource.res_partner_id.id,
                                                     'account_id':
                                                     w_cuenta_analitica,
                                                     'journal_id':
                                                     w_journal_id,
                                                     'general_account_id':
                                                     w_account_id,
                                                     'simulation_cost_line_id':
                                                     False,
                                                     'financing_percentage':
                                                     financing.project_percent,
                                                     'simulation_cost_id':
                                                     simulation_cost.id,
                                                     'financing_source_id':
                                                     fsource.id
                                                     }
                                    else:
                                        line_vals = {'name': financing.name,
                                                     'type':
                                                     'financing_source',
                                                     'expense_area_id':
                                                     line.expense_area_id.id,
                                                     'project_financing_id':
                                                     financing.id,
                                                     'account_analytic_line_bu'
                                                     'dgetary_id':
                                                     aanalytic_line_ids[0],
                                                     'partner_id':
                                                     fsource.res_partner_id.id,
                                                     'account_id':
                                                     w_cuenta_analitica,
                                                     'journal_id':
                                                     w_journal_id,
                                                     'general_account_id':
                                                     w_account_id,
                                                     'simulation_cost_line_id':
                                                     line.id,
                                                     'financing_percentage':
                                                     financing.project_percent,
                                                     'product_id':
                                                     line.product_id.id,
                                                     'simulation_cost_id':
                                                     simulation_cost.id,
                                                     'financing_source_id':
                                                     fsource.id
                                                     }
                                    acc_line_obj.create(cr, uid, line_vals)
                            else:
                                fs = financing.financing_source_id
                                if not simulation_cost.generate_by_lines:
                                    area_name = line.expense_area_id.name
                                    c = [('name', '=', (financing.name + ' - '
                                                        + area_name)),
                                         ('type', '=', 'financing_source'),
                                         ('expense_area_id', '=',
                                          line.expense_area_id.id),
                                         ('project_financing_id', '=',
                                          financing.id),
                                         ('account_analytic_line_budgetary_id',
                                          '=', aanalytic_line_ids[0]),
                                         ('partner_id', '=',
                                          fs.res_partner_id.id),
                                         ('account_id', '=',
                                          w_cuenta_analitica),
                                         ('journal_id', '=',
                                          w_journal_id),
                                         ('general_account_id', '=',
                                          w_account_id),
                                         ('simulation_cost_line_id', '=',
                                          False),
                                         ('simulation_cost_id', '=',
                                          simulation_cost.id),
                                         ('financing_source_id', '=', fs.id)]
                                else:
                                    prod_name = line.product_id.name
                                    area_name = line.expense_area_id.name
                                    c = [('name', '=', (financing.name + ' - '
                                                        + prod_name + ' - ' +
                                                        area_name)),
                                         ('type', '=', 'financing_source'),
                                         ('expense_area_id', '=',
                                          line.expense_area_id.id),
                                         ('project_financing_id', '=',
                                          financing.id),
                                         ('account_analytic_line_budgetary_id',
                                          '=', aanalytic_line_ids[0]),
                                         ('partner_id', '=',
                                          fs.res_partner_id.id),
                                         ('account_id', '=',
                                          w_cuenta_analitica),
                                         ('journal_id', '=',
                                          w_journal_id),
                                         ('general_account_id', '=',
                                          w_account_id),
                                         ('simulation_cost_line_id', '=',
                                          line.id),
                                         ('product_id', '=',
                                          line.product_id.id),
                                         ('simulation_cost_id', '=',
                                          simulation_cost.id),
                                         ('financing_source_id', '=',
                                          fs.id)]
                                analytic_line_ids = acc_line_obj.search(
                                    cr, uid, c)
                                if not analytic_line_ids:
                                    if not simulation_cost.generate_by_lines:
                                        line_vals = {'name': (financing.name +
                                                              ' - ' +
                                                              area_name),
                                                     'type':
                                                     'financing_source',
                                                     'expense_area_id':
                                                     line.expense_area_id.id,
                                                     'project_financing_id':
                                                     financing.id,
                                                     'account_analytic_line'
                                                     '_budgetary_id':
                                                     aanalytic_line_ids[0],
                                                     'partner_id':
                                                     fs.res_partner_id.id,
                                                     'account_id':
                                                     w_cuenta_analitica,
                                                     'journal_id':
                                                     w_journal_id,
                                                     'general_account_id':
                                                     w_account_id,
                                                     'simulation_cost_line_id':
                                                     False,
                                                     'financing_percentage':
                                                     financing.project_percent,
                                                     'simulation_cost_id':
                                                     simulation_cost.id,
                                                     'financing_source_id':
                                                     fs.id
                                                     }
                                    else:
                                        line_vals = {'name': (financing.name +
                                                              ' - ' +
                                                              product_name +
                                                              ' - ' +
                                                              area_name),
                                                     'type':
                                                     'financing_source',
                                                     'expense_area_id':
                                                     line.expense_area_id.id,
                                                     'project_financing_id':
                                                     financing.id,
                                                     'account_analytic_line'
                                                     '_budgetary_id':
                                                     aanalytic_line_ids[0],
                                                     'partner_id':
                                                     fs.res_partner_id.id,
                                                     'account_id':
                                                     w_cuenta_analitica,
                                                     'journal_id':
                                                     w_journal_id,
                                                     'general_account_id':
                                                     w_account_id,
                                                     'simulation_cost_line_id':
                                                     line.id,
                                                     'financing_percentage':
                                                     financing.project_percent,
                                                     'product_id':
                                                     line.product_id.id,
                                                     'simulation_cost_id':
                                                     simulation_cost.id,
                                                     'financing_source_id':
                                                     fs.id
                                                     }
                                    acc_line_obj.create(cr, uid, line_vals)
        return True

    def _create_financial_source(self, cr, uid, simulation_cost, line,
                                 w_cuenta_analitica, w_journal_id,
                                 w_account_id):
        analytic_line_obj = self.pool['account.analytic.line']
        project_financing_obj = self.pool['project.financing']
        account_simuline_obj = self.pool['account.analytic.simulation.line']
        simuline_obj = self.pool['simulation.cost.line']
        if not simulation_cost.generate_by_lines:
            cond = [('name', 'like', ('Budgetary - ' +
                                      line.expense_area_id.name)),
                    ('type', '=', 'budgetary'),
                    ('expense_area_id', '=',  line.expense_area_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', False),
                    ('simulation_cost_id', '=', simulation_cost.id)]
        else:
            cond = [('name', 'like', 'Budgetary - ' + line.product_id.name),
                    ('type', '=', 'budgetary'),
                    ('expense_area_id', '=', line.expense_area_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', line.id),
                    ('product_id', '=', line.product_id.id),
                    ('simulation_cost_id', '=', simulation_cost.id)]
        analine_ids = analytic_line_obj.search(cr, uid, cond)
        if not analine_ids:
            if not simulation_cost.generate_by_lines:
                raise orm.except_orm(_('Process Error'),
                                     _('Budgetary analytic line not found for '
                                       '%s expense area') %
                                     line.expense_area_id.name)
            else:
                raise orm.except_orm(_('Process Error'),
                                     _('Budgetary analytic line not found for '
                                       'product: %s') % line.product_id.name)
        fsource = line.project_financing_id.financing_source_id
        if not simulation_cost.generate_by_lines:
            cond = [('name', '=', (line.project_financing_id.name + ' - ' +
                                   line.expense_area_id.name)),
                    ('type', '=', 'financing_source'),
                    ('expense_area_id', '=', line.expense_area_id.id),
                    ('project_financing_id', '=',
                     line.project_financing_id.id),
                    ('account_analytic_line_budgetary_id', '=',
                     analine_ids[0]),
                    ('partner_id', '=', fsource.res_partner_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', False),
                    ('simulation_cost_id', '=', simulation_cost.id),
                    ('financing_source_id', '=', fsource.id)]
        else:
            cond = [('name', '=', (line.project_financing_id.name + ' - ' +
                                   line.product_id.name)),
                    ('type', '=', 'financing_source'),
                    ('expense_area_id', '=', line.expense_area_id.id),
                    ('project_financing_id', '=',
                     line.project_financing_id.id),
                    ('account_analytic_line_budgetary_id', '=',
                     analine_ids[0]),
                    ('partner_id', '=', fsource.res_partner_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', line.id),
                    ('product_id', '=', line.product_id.id),
                    ('simulation_cost_id', '=', simulation_cost.id),
                    ('financing_source_id', '=', fsource.id)]
        analytic_line_ids = analytic_line_obj.search(cr, uid, cond)
        if not analytic_line_ids:
            if not simulation_cost.generate_by_lines:
                line_vals = {'name': (line.project_financing_id.name + ' - ' +
                                      line.expense_area_id.name),
                             'type': 'financing_source',
                             'expense_area_id': line.expense_area_id.id,
                             'project_financing_id':
                             line.project_financing_id.id,
                             'account_analytic_line_budgetary_id':
                             analine_ids[0],
                             'partner_id': fsource.res_partner_id.id,
                             'account_id': w_cuenta_analitica,
                             'journal_id': w_journal_id,
                             'general_account_id': w_account_id,
                             'simulation_cost_line_id': False,
                             'financing_percentage': 100,
                             'simulation_cost_id': simulation_cost.id,
                             'financing_source_id': fsource.id
                             }
            else:
                line_vals = {'name': (line.project_financing_id.name + ' - ' +
                                      line.product_id.name),
                             'type': 'financing_source',
                             'expense_area_id': line.expense_area_id.id,
                             'project_financing_id':
                             line.project_financing_id.id,
                             'account_analytic_line_budgetary_id':
                             analine_ids[0],
                             'partner_id': fsource.res_partner_id.id,
                             'account_id': w_cuenta_analitica,
                             'journal_id': w_journal_id,
                             'general_account_id': w_account_id,
                             'simulation_cost_line_id': line.id,
                             'financing_percentage': 100,
                             'product_id': line.product_id.id,
                             'simulation_cost_id': simulation_cost.id,
                             'financing_source_id': fsource.id
                             }
            account_analytic_line_id = analytic_line_obj.create(cr, uid,
                                                                line_vals)
        else:
            account_analytic_line_id = analytic_line_ids[0]
        # Cálculo del importe a financiar
        w_imp = ((line.subtotal_purchase *
                  line.project_financing_id.project_percent) / 100)
        if not simulation_cost.generate_by_lines:
            line_vals = {'name': (line.project_financing_id.name + ' - ' +
                                  line.expense_area_id.name + ' - ' +
                                  line.product_id.name),
                         'type': 'initial_financial_source',
                         'expense_area_id': line.expense_area_id.id,
                         'project_financing_id': line.project_financing_id.id,
                         'account_analytic_line_financing_source_id':
                         account_analytic_line_id,
                         'partner_id': fsource.res_partner_id.id,
                         'account_id': w_cuenta_analitica,
                         'journal_id': w_journal_id,
                         'general_account_id': w_account_id,
                         'product_id': line.product_id.id,
                         'assigned': w_imp,
                         'simulation_cost_line_id': False,
                         'simulation_cost_id': simulation_cost.id
                         }
        else:
            line_vals = {'name': (line.project_financing_id.name + ' - ' +
                                  line.product_id.name + ' - ' +
                                  line.expense_area_id.name),
                         'type': 'initial_financial_source',
                         'expense_area_id': line.expense_area_id.id,
                         'project_financing_id': line.project_financing_id.id,
                         'account_analytic_line_financing_source_id':
                         account_analytic_line_id,
                         'partner_id': fsource.res_partner_id.id,
                         'account_id': w_cuenta_analitica,
                         'journal_id': w_journal_id,
                         'general_account_id': w_account_id,
                         'product_id': line.product_id.id,
                         'assigned': w_imp,
                         'simulation_cost_line_id': line.id,
                         'simulation_cost_id': simulation_cost.id
                         }
        account_analytic_line_id = analytic_line_obj.create(cr, uid, line_vals)
        # Actualizo el Fondo Financiador (project_financing) con el importe que
        # financia
        project_financing = project_financing_obj.browse(
            cr, uid, line.project_financing_id.id)
        w_imp2 = project_financing.amount_awarded + w_imp
        vals = {'amount_awarded': w_imp2,
                'grant': w_imp2}
        project_financing_obj.write(
            cr, uid, [line.project_financing_id.id], vals)
        # Actualizo la linea de simulación como financiada
        simuline_obj.write(cr, uid, line.id, {'financied_line': True})
        # Doy de alta una fila en la tabla que relaciona partidas y
        # simulaciones
        line_vals = {'account_analytic_line_id': account_analytic_line_id,
                     'simulation_cost_id': simulation_cost.id,
                     'simulation_cost_line_id': line.id,
                     'expense_area_id': line.expense_area_id.id,
                     'project_financing_id': line.project_financing_id.id,
                     'amount': w_imp,
                     'financing_percentage': 100
                     }
        account_simuline_obj.create(cr, uid, line_vals)
        return True

    def _create_financial_source2(self, cr, uid, with_area, project_financing,
                                  simulation_cost, line, w_cuenta_analitica,
                                  w_journal_id, w_account_id):
        analytic_line_obj = self.pool['account.analytic.line']
        project_financing_obj = self.pool['project.financing']
        account_simuline_obj = self.pool['account.analytic.simulation.line']
        simuline_obj = self.pool['simulation.cost.line']
        if not simulation_cost.generate_by_lines:
            cond = [('name', 'like', ('Budgetary - ' +
                                      line.expense_area_id.name)),
                    ('type', '=', 'budgetary'),
                    ('expense_area_id', '=', line.expense_area_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', False),
                    ('simulation_cost_id', '=', simulation_cost.id)]
        else:
            cond = [('name', 'like', 'Budgetary - ' + line.product_id.name),
                    ('type', '=', 'budgetary'),
                    ('expense_area_id', '=', line.expense_area_id.id),
                    ('account_id', '=', w_cuenta_analitica),
                    ('journal_id', '=', w_journal_id),
                    ('general_account_id', '=', w_account_id),
                    ('simulation_cost_line_id', '=', line.id),
                    ('product_id', '=', line.product_id.id),
                    ('simulation_cost_id', '=', simulation_cost.id)]
        analine_ids = analytic_line_obj.search(cr, uid, cond)
        if not analine_ids:
            if not simulation_cost.generate_by_lines:
                raise orm.except_orm(_('Process Error'),
                                     _('Budgetary analytic line not found for '
                                       '%s expense area') %
                                     line.expense_area_id.name)
            else:
                raise orm.except_orm(_('Process Error'),
                                     _('Budgetary analytic line not found for '
                                       'product: %s') % line.product_id.name)
        fsource = project_financing.financing_source_id
        if not with_area:
            if not simulation_cost.generate_by_lines:
                cond = [('name', '=', project_financing.name),
                        ('type', '=', 'financing_source'),
                        ('expense_area_id', '=', line.expense_area_id.id),
                        ('project_financing_id', '=', project_financing.id),
                        ('account_analytic_line_budgetary_id', '=',
                         analine_ids[0]),
                        ('partner_id', '=', fsource.res_partner_id.id),
                        ('account_id', '=', w_cuenta_analitica),
                        ('journal_id', '=', w_journal_id),
                        ('general_account_id', '=', w_account_id),
                        ('simulation_cost_line_id', '=', False),
                        ('simulation_cost_id', '=', simulation_cost.id),
                        ('financing_source_id', '=', fsource.id)]
            else:
                cond = [('name', '=', project_financing.name),
                        ('type', '=', 'financing_source'),
                        ('expense_area_id', '=', line.expense_area_id.id),
                        ('project_financing_id', '=', project_financing.id),
                        ('account_analytic_line_budgetary_id', '=',
                         analine_ids[0]),
                        ('partner_id', '=', fsource.res_partner_id.id),
                        ('account_id', '=', w_cuenta_analitica),
                        ('journal_id', '=', w_journal_id),
                        ('general_account_id', '=', w_account_id),
                        ('simulation_cost_line_id', '=', line.id),
                        ('product_id', '=', line.product_id.id),
                        ('simulation_cost_id', '=', simulation_cost.id),
                        ('financing_source_id', '=', fsource.id)]
            analytic_line_ids = analytic_line_obj.search(cr, uid, cond)
        else:
            if not simulation_cost.generate_by_lines:
                cond = [('name', '=', (project_financing.name + ' - ' +
                                       line.expense_area_id.name)),
                        ('type', '=', 'financing_source'),
                        ('expense_area_id', '=', line.expense_area_id.id),
                        ('project_financing_id', '=', project_financing.id),
                        ('account_analytic_line_budgetary_id', '=',
                         analine_ids[0]),
                        ('partner_id', '=', fsource.res_partner_id.id),
                        ('account_id', '=', w_cuenta_analitica),
                        ('journal_id', '=', w_journal_id),
                        ('general_account_id', '=', w_account_id),
                        ('simulation_cost_line_id', '=', False),
                        ('simulation_cost_id', '=', simulation_cost.id),
                        ('financing_source_id', '=', fsource.id)]
            else:
                cond = [('name', '=', (project_financing.name + ' - ' +
                                       line.product_id.name + ' - ' +
                                       line.expense_area_id.name)),
                        ('type', '=', 'financing_source'),
                        ('expense_area_id', '=', line.expense_area_id.id),
                        ('project_financing_id', '=', project_financing.id),
                        ('account_analytic_line_budgetary_id', '=',
                         analine_ids[0]),
                        ('partner_id', '=', fsource.res_partner_id.id),
                        ('account_id', '=', w_cuenta_analitica),
                        ('journal_id', '=', w_journal_id),
                        ('general_account_id', '=', w_account_id),
                        ('simulation_cost_line_id', '=', line.id),
                        ('product_id', '=', line.product_id.id),
                        ('simulation_cost_id', '=', simulation_cost.id),
                        ('financing_source_id', '=', fsource.id)]
            analytic_line_ids = analytic_line_obj.search(cr, uid, cond)
        if not analytic_line_ids:
            if not with_area:
                if not simulation_cost.generate_by_lines:
                    line_vals = {'name': project_financing.name,
                                 'type': 'financing_source',
                                 'expense_area_id': line.expense_area_id.id,
                                 'project_financing_id': project_financing.id,
                                 'account_analytic_line_budgetary_id':
                                 analine_ids[0],
                                 'partner_id': fsource.res_partner_id.id,
                                 'account_id': w_cuenta_analitica,
                                 'journal_id': w_journal_id,
                                 'general_account_id': w_account_id,
                                 'simulation_cost_line_id': False,
                                 'financing_percentage':
                                 project_financing.project_percent,
                                 'simulation_cost_id': simulation_cost.id,
                                 'financing_source_id': fsource.id
                                 }
                else:
                    line_vals = {'name': project_financing.name,
                                 'type': 'financing_source',
                                 'expense_area_id': line.expense_area_id.id,
                                 'project_financing_id': project_financing.id,
                                 'account_analytic_line_budgetary_id':
                                 analine_ids[0],
                                 'partner_id': fsource.res_partner_id.id,
                                 'account_id': w_cuenta_analitica,
                                 'journal_id': w_journal_id,
                                 'general_account_id': w_account_id,
                                 'simulation_cost_line_id': line.id,
                                 'financing_percentage':
                                 project_financing.project_percent,
                                 'product_id': line.product_id.id,
                                 'simulation_cost_id': simulation_cost.id,
                                 'financing_source_id': fsource.id
                                 }
            else:
                if not simulation_cost.generate_by_lines:
                    line_vals = {'name': (project_financing.name + ' - ' +
                                          line.expense_area_id.name),
                                 'type': 'financing_source',
                                 'expense_area_id': line.expense_area_id.id,
                                 'project_financing_id': project_financing.id,
                                 'account_analytic_line_budgetary_id':
                                 analine_ids[0],
                                 'partner_id': fsource.res_partner_id.id,
                                 'account_id': w_cuenta_analitica,
                                 'journal_id': w_journal_id,
                                 'general_account_id': w_account_id,
                                 'simulation_cost_line_id': False,
                                 'financing_percentage':
                                 project_financing.project_percent,
                                 'simulation_cost_id': simulation_cost.id,
                                 'financing_source_id': fsource.id
                                 }
                else:
                    line_vals = {'name': (project_financing.name + ' - ' +
                                          line.product_id.name + ' - ' +
                                          line.expense_area_id.name),
                                 'type': 'financing_source',
                                 'expense_area_id': line.expense_area_id.id,
                                 'project_financing_id': project_financing.id,
                                 'account_analytic_line_budgetary_id':
                                 analine_ids[0],
                                 'partner_id': fsource.res_partner_id.id,
                                 'account_id': w_cuenta_analitica,
                                 'journal_id': w_journal_id,
                                 'general_account_id': w_account_id,
                                 'simulation_cost_line_id': line.id,
                                 'financing_percentage':
                                 project_financing.project_percent,
                                 'product_id': line.product_id.id,
                                 'simulation_cost_id': simulation_cost.id,
                                 'financing_source_id': fsource.id
                                 }
            account_analytic_line_id = analytic_line_obj.create(cr, uid,
                                                                line_vals)
        else:
            account_analytic_line_id = analytic_line_ids[0]
        w_imp = ((line.subtotal_purchase *
                  project_financing.project_percent) / 100)
        if not simulation_cost.generate_by_lines:
            line_vals = {'name': (project_financing.name + ' - ' +
                                  line.expense_area_id.name + ' - ' +
                                  line.product_id.name),
                         'type': 'initial_financial_source',
                         'expense_area_id': line.expense_area_id.id,
                         'project_financing_id': project_financing.id,
                         'account_analytic_line_financing_source_id':
                         account_analytic_line_id,
                         'partner_id': fsource.res_partner_id.id,
                         'account_id': w_cuenta_analitica,
                         'journal_id': w_journal_id,
                         'general_account_id': w_account_id,
                         'product_id': line.product_id.id,
                         'assigned': w_imp,
                         'simulation_cost_line_id': False,
                         'simulation_cost_id': simulation_cost.id
                         }
        else:
            line_vals = {'name': (project_financing.name + ' - ' +
                                  line.product_id.name + ' - ' +
                                  line.expense_area_id.name),
                         'type': 'initial_financial_source',
                         'expense_area_id': line.expense_area_id.id,
                         'project_financing_id': project_financing.id,
                         'account_analytic_line_financing_source_id':
                         account_analytic_line_id,
                         'partner_id': fsource.res_partner_id.id,
                         'account_id': w_cuenta_analitica,
                         'journal_id': w_journal_id,
                         'general_account_id': w_account_id,
                         'product_id': line.product_id.id,
                         'assigned': w_imp,
                         'simulation_cost_line_id': line.id,
                         'simulation_cost_id': simulation_cost.id
                         }
        account_analytic_line_id = analytic_line_obj.create(cr, uid, line_vals)
        # Actualizo el Fondo Financiador (project_financing) con el importe que
        # financia
        w_imp2 = project_financing.amount_awarded + w_imp
        vals = {'amount_awarded': w_imp2,
                'grant': w_imp2}
        project_financing_obj.write(cr, uid, [project_financing.id], vals)
        # Actualizo la linea de simulación como financiada
        simuline_obj.write(cr, uid, line.id, {'financied_line': True})
        # Doy de alta una fila en la tabla que relaciona partidas y
        # simulaciones
        line_vals = {'account_analytic_line_id': account_analytic_line_id,
                     'simulation_cost_id': simulation_cost.id,
                     'simulation_cost_line_id': line.id,
                     'expense_area_id': line.expense_area_id.id,
                     'project_financing_id': project_financing.id,
                     'amount': w_imp,
                     'financing_percentage': project_financing.project_percent
                     }
        account_simuline_obj.create(cr, uid, line_vals)
        return True

    def action_draft(self, cr, uid, ids):
        account_obj = self.pool['account.analytic.account']
        account_line_obj = self.pool['account.analytic.line']
        project_obj = self.pool['project.project']
        picking_obj = self.pool['stock.picking']
        move_obj = self.pool['stock.move']
        sale_obj = self.pool['sale.order']
        sale_line_obj = self.pool['sale.order.line']
        project_financing_obj = self.pool['project.financing']
        if ids:
            for simulation in self.browse(cr, uid, ids):
                if simulation.state == 'financing' and simulation.project_id:
                    if simulation.project_id.sum_expense_request > 0:
                        raise orm.except_orm(_('Error'),
                                             _('Project with imputations'))
                    # Borro los pedidos de venta
                    if simulation.sale_order_ids:
                        for sale_order in simulation.sale_order_ids:
                            if sale_order.picking_ids:
                                for picking in sale_order.picking_ids:
                                    if picking.move_lines:
                                        for move_line in picking.move_lines:
                                            move_obj.action_cancel(
                                                cr, uid, [move_line.id])
                                            vals = {'state': 'draft'}
                                            move_obj.write(
                                                cr, uid, [move_line.id], vals)
                                            move_obj.unlink(
                                                cr, uid, [move_line.id])
                                    vals = {'state': 'draft'}
                                    picking_obj.write(
                                        cr, uid, [picking.id], vals)
                                    picking_obj.unlink(
                                        cr, uid, [picking.id])
                            if sale_order.order_line:
                                for order_line in sale_order.order_line:
                                    sale_line_obj.button_cancel(
                                        cr, uid, [order_line.id])
                                    sale_line_obj.unlink(
                                        cr, uid, [order_line.id])
                            workflow.trg_validate(uid, 'sale.order',
                                                  sale_order.id, 'cancel', cr)
                            sale_obj.unlink(cr, uid, [sale_order.id])
                    # Borro Proyecto y Cuenta Analítica  SOLO SI NO HAY
                    # use_project
                    if not simulation.use_project_id:
                        simu = simulation
                        account_id = simu.project_id.analytic_account_id.id
                        project_obj.unlink(
                            cr, uid, [simulation.project_id.id])
                        account_obj.unlink(
                            cr, uid, [account_id])
                    else:
                        # Borro las líneas de analitica para esta simulacion
                        cond = [('simulation_cost_id', '=', simulation.id)]
                        analytic_line_ids = account_line_obj.search(cr, uid,
                                                                    cond)
                        if analytic_line_ids:
                            account_line_obj.unlink(
                                cr, uid, analytic_line_ids)
                    # Quito el proyecto de la simulacion
                    vals = {'project_id': False}
                    self.write(cr, uid, [simulation.id], vals)
                    # Borro las Fuentes de Financiacion
                    if simulation.financing_source_ids:
                        for financing in simulation.financing_source_ids:
                            project_financing_obj.unlink(
                                cr, uid, financing.id)
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def action_inmodif_budgetary(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state': 'inmodif_budgetary'})
        return True

    def action_closed(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state': 'closed'})
        return True

    def onchange_expense_area(self, cr, uid, ids, expense_area_ids,
                              simulation_category_ids, context=None):
        res = {}
        found = False
        for expense_area in expense_area_ids:
            if expense_area[2]:
                found = True
        if not ids and found:
            return {'value': {'expense_area_ids': False,
                              'simulation_category_ids': False},
                    'warning': {'title': _('Error'),
                                'message': _('You should save before the '
                                             'simulation'),
                                }
                    }
        else:
            if not ids:
                return {'value': res}
        expense_area_obj = self.pool['expense.area']
        simulation_category_obj = self.pool['simulation.category']
        my_category = []
        simulation = self.browse(cr, uid, ids[0], context)
        if simulation.simulation_category_ids:
            for category in simulation.simulation_category_ids:
                simulation_category_obj.unlink(cr, uid, category.id, context)
        for simulation_category in simulation_category_ids:
            if simulation_category[2]:
                item = simulation_category[2]
                if item.get('expense_area_id') in expense_area_ids[0][2]:
                    my_category.append(simulation_category[2])
        for expense_area in expense_area_ids:
            if expense_area[2]:
                expense_area2 = expense_area_obj.browse(
                    cr, uid, expense_area[2], context)
                for exp_area2 in expense_area2:
                    if exp_area2.category_ids:
                        for category in exp_area2.category_ids:
                            found = 0
                            for simulation_category in simulation_category_ids:
                                if simulation_category[2]:
                                    mycategory = simulation_category[2]
                                    if (mycategory.get('expense_area_id') ==
                                            exp_area2.id and
                                            mycategory.get('category_id') ==
                                            category.id):
                                        found = 1
                            if found == 0:
                                line_vals = {'simulation_cost_id': ids[0],
                                             'expense_area_id': exp_area2.id,
                                             'category_id': category.id
                                             }
                                my_category.append(line_vals)
        res = {'simulation_category_ids':  my_category}
        return {'value': res}

    def onchange_financing_source_ids(self, cr, uid, ids,
                                      financing_source_list, context=None):
        res = {}
        warning = {}
        datas = {}
        w_error = 0
        project_financing_obj = self.pool['project.financing']
        for financing_source in financing_source_list:
            if financing_source[2]:
                if w_error == 0:
                    if financing_source[2].get('expense_area_id'):
                        earea_id = financing_source[2].get('expense_area_id')
                    else:
                        earea_id = 0
                    if not financing_source[2].get('project_percent'):
                        w_error = 1
                        warning.update({'title': _('Financing Error'),
                                        'message': _('You must enter the '
                                                     'percentage of financing')
                                        })
                    else:
                        percentaje = financing_source[2].get('project_percent')
                        if percentaje == 0:
                            w_error = 1
                            warning.update({'title': _('Financing Error'),
                                            'message': _('You must enter the '
                                                         'percentage of '
                                                         'financing')
                                            })
                        else:
                            if percentaje > 100:
                                w_error = 1
                                warning.update({'title': _('Financing Error'),
                                                'message': _('The percentage '
                                                             'of financing is '
                                                             '> 100')
                                                })
                            else:
                                w_found = 0
                                for data in datas:
                                    datos_array = datas[data]
                                    w_farea_id = datos_array['expense_area_id']
                                    if w_farea_id == earea_id:
                                        w_found = 1
                                        w_per = datos_array['percentaje']
                                        w_per = w_per + percentaje
                                        vals = {'percentaje': w_per}
                                        datas[data].update(vals)
                                if w_found == 0:
                                    vals = {'expense_area_id': earea_id,
                                            'percentaje': percentaje}
                                    datas[(earea_id)] = vals
        if w_error == 0:
            for data in datas:
                datos_array = datas[data]
                w_found_expense_area_id = datos_array['expense_area_id']
                w_found_percentaje = datos_array['percentaje']
                if w_error == 0:
                    if w_found_percentaje > 100:
                        w_error = 1
                        if w_found_expense_area_id == 0:
                            warning.update({'title': _('Financing Error'),
                                            'message': _('The percentaje for '
                                                         'financing all '
                                                         'expense areas is '
                                                         '%s') %
                                            w_found_percentaje
                                            })
                        else:
                            project_financing = project_financing_obj.browse(
                                cr, uid, w_found_expense_area_id, context)
                            warning.update({'title': _('Financing Error'),
                                            'message': _('The percentaje for '
                                                         'financing %s expense'
                                                         ' areas is %s') %
                                            (project_financing.name,
                                             w_found_percentaje)})
        return {'value': res,
                'warning': warning}

    def onchange_project_type(self, cr, uid, ids, project_type_id,
                              context=None):
        res = {}
        project_type_obj = self.pool['project.type']
        if not project_type_id:
            res.update({'generate_by_lines': False})
        else:
            project_type = project_type_obj.browse(cr, uid, project_type_id,
                                                   context)
            res.update({'generate_by_lines': project_type.generate_by_lines})
        return {'value': res}

    def onchange_use_project_id(self, cr, uid, ids, use_project_id,
                                context=None):
        res = {}
        project_obj = self.pool['project.project']
        if not use_project_id:
            res.update({'parent_project_id': False})
        else:
            project = project_obj.browse(cr, uid, use_project_id, context)
            if project.parent_id:
                cond = [('analytic_account_id', '=', project.parent_id.id)]
                project_ids = project_obj.search(cr, uid, cond)
                if not project_ids:
                    res.update({'parent_project_id': False})
                    raise orm.except_orm(_('ERROR'),
                                         _("Not Project found for 'analytic "
                                           "account: %s") %
                                         (project.parent_id.name,))
                else:
                    res.update({'parent_project_id': project_ids[0]})
            else:
                res.update({'parent_project_id': False})
        return {'value': res}
