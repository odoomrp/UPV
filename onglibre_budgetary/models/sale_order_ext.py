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


class SaleOrder(orm.Model):

    _inherit = 'sale.order'

    def _sale_order_name(self, cr, uid, context=None):
        ir_sequence_obj = self.pool['ir.sequence']
        if not context:
            context = {}
        ir_sequence_ids = ir_sequence_obj.search(
            cr, uid, [('prefix', '=', 'SO')], context=context)
        return ir_sequence_obj.get_id(cr, uid, ir_sequence_ids[0])

    _columns = {
        # Tipo de venta
        'sale_type': fields.char('Sale Type', size=12),
        # Area de Gasto
        'expense_area_id': fields.many2one('expense.area', 'Expense Area'),
        # Fondo Financiador
        'financing_source_id':
            fields.many2one('financing.source', 'Project Financer',
                            readonly=True,
                            states={'draft': [('readonly', False)]}),
        # Referencia del pedido de venta
        'name':
            fields.char('Order Reference', size=64, required=True,
                        readonly=True,
                        states={'draft': [('readonly', False)]}, select=True),
    }

    _defaults = {'name': lambda obj, cr, uid, context:
                 obj._sale_order_name(cr, uid),
                 }

    # FUNCION QUE SE EJECUTA CUANDO CONFIRMO UN PEDIDO DE VENTA
    def action_wait(self, cr, uid, ids, context=None):
        project_obj = self.pool['project.project']
        sale_obj = self.pool['sale.order']
        simuline_obj = self.pool['simulation.cost.line']
        account_journal_obj = self.pool['account.analytic.journal']
        account_account_obj = self.pool['account.account']
        # Cojo el diario analítico
        cond = [('name', 'like', 'Presupuestarias')]
        account_analytic_journal_ids = account_journal_obj.search(
            cr, uid, cond, context=context)
        if not account_analytic_journal_ids:
            raise orm.except_orm(_('Sale Order confirmation Error'),
                                 _('Journal with Presupuestarias literal NOT '
                                   'FOUND'))
        # Cojo la cuenta general
        cond = [('name', 'like', 'Your Company')]
        account_account_ids = account_account_obj.search(cr, uid, cond,
                                                         context=context)
        if not account_account_ids:
            raise orm.except_orm(_('Sale Order confirmation Error'),
                                 _('General Account YOUR COMPANY not found'))
        # Accedo al PEDIDO DE VENTA
        sale_order2 = sale_obj.browse(cr, uid, ids[0], context=context)
        # SI EL PEDIDO DE VENTA VIENE DE UNA SIMULACION, COJO LA ÚLTIMA
        # SIMULACIÓN ACTIVA QUE NO ESTE CANCELADA, O LA ÚLTIMA HITORIFICADA
        w_found = 0
        w_simulation_cost_id = 0
        w_maxid = 0
        if sale_order2.simulation_cost_ids:
            # Recorro todas las simulaciones asociadas al pedido de venta
            for simulation_cost in sale_order2.simulation_cost_ids:
                if ((not simulation_cost.historical_ok) and
                        (simulation_cost.state not in ('canceled'))):
                    # Si es una simulación activa, me quedo con este id
                    w_found = 1
                    w_simulation_cost_id = simulation_cost.id
                else:
                    # Si no ha encontrado la activa me quedo con la última
                    # simulación de coste historificada (la mas nueva, la de
                    # mayor id)
                    if w_found == 0:
                        if simulation_cost.id > w_maxid:
                            w_maxid = simulation_cost.id

            if w_simulation_cost_id == 0:
                # Si no he encontrado una simulación de coste activa para ese
                # pedido de venta
                if w_maxid == 0:
                    # Si no he encontrado una simulación de coste historificada
                    # para ese pedido de venta
                    raise orm.except_orm(_('Sale Order confirmation Error'),
                                         _('Simulation Cost not found'))
                else:
                    # Si no he encontrado una simulación de coste activa para
                    # ese pedido de venta, me quedo con el id de la simulación
                    # de coste historificada mas nueva
                    w_simulation_cost_id = w_maxid

        # Si EL PEDIDO DE VENTA VIENE DE UNA SIMULACIÓN, MIRO SI YA TIENE
        # ASOCIADO UN PROYECTO
        if sale_order2.simulation_cost_ids:
            if not sale_order2.project2_id:
                raise orm.except_orm(_('Sale Order confirmation Error'),
                                     _('Simulation Cost WITHOUT PROJECT'))
            else:
                # SI EL PEDIDO DE VENTA TIENE UN PROYECTO ASOCIADO, COJO SU ID
                project_id = sale_order2.project2_id.id
                # Ahora cojo su cuenta analítica
                project = project_obj.browse(cr, uid, project_id, context)
                account_analytic_account_id = project.analytic_account_id.id
        # DOY DE ALTA LINEAS DE ANALITICA
        if sale_order2.simulation_cost_ids:
            for sale_order_line in sale_order2.order_line:
                if sale_order_line.simulation_cost_line_id:
                    simulation_cost_line = simuline_obj.browse(
                        cr, uid, sale_order_line.simulation_cost_line_id.id,
                        context)
                    if (simulation_cost_line.simulation_cost_id.id ==
                            w_simulation_cost_id):
                        if sale_order2.sale_type == 'initial':
                            self._sale_order_initial(
                                cr, uid, simulation_cost_line, sale_order_line,
                                account_analytic_account_id,
                                account_analytic_journal_ids,
                                account_account_ids, w_simulation_cost_id,
                                context=context)
                        else:
                            if sale_order2.sale_type == 'modification':
                                self._sale_order_modification(
                                    cr, uid, simulation_cost_line,
                                    sale_order_line,
                                    account_analytic_account_id,
                                    account_analytic_journal_ids,
                                    account_account_ids, w_simulation_cost_id,
                                    context=context)
        super(SaleOrder, self).action_wait(cr, uid, ids, context)
        return True

    def _sale_order_initial(self, cr, uid, simulation_cost_line,
                            saleline, account_analytic_account_id,
                            account_analytic_journal_ids,
                            account_account_ids, w_simulation_cost_id,
                            context=None):
        account_analytic_line_obj = self.pool['account.analytic.line']
        expenser_area_id = saleline.simulation_cost_line_id.expense_area_id.id
        budgetline_id = saleline.analytic_budgetary_line_id.id
        fsour_id = saleline.financial_source_line_id.id
        if simulation_cost_line.simulation_cost_id.generate_by_lines:
            line_vals = {'name': ('Initial Budgetary - ' +
                                  saleline.product_id.name),
                         'type': 'initial_budgetary',
                         'expense_area_id': expenser_area_id,
                         'account_analytic_line_budgetary_id': budgetline_id,
                         'account_analytic_line_financing_source_id': fsour_id,
                         'account_id': account_analytic_account_id,
                         'journal_id': account_analytic_journal_ids[0],
                         'general_account_id': account_account_ids[0],
                         'product_id': saleline.product_id.id,
                         'unit_amount': saleline.product_uom_qty,
                         'expense_budget': saleline.financied_amount,
                         'updated_expense_budget': saleline.financied_amount,
                         'simulation_cost_line_id': simulation_cost_line.id,
                         'simulation_cost_id': w_simulation_cost_id
                         }
        else:
            line_vals = {'name': ('Initial Budgetary - ' +
                                  saleline.product_id.name),
                         'type': 'initial_budgetary',
                         'expense_area_id': expenser_area_id,
                         'account_analytic_line_budgetary_id':  budgetline_id,
                         'account_analytic_line_financing_source_id': fsour_id,
                         'account_id': account_analytic_account_id,
                         'journal_id': account_analytic_journal_ids[0],
                         'general_account_id': account_account_ids[0],
                         'product_id': saleline.product_id.id,
                         'unit_amount': saleline.product_uom_qty,
                         'expense_budget': saleline.financied_amount,
                         'updated_expense_budget': saleline.financied_amount,
                         'simulation_cost_line_id': False,
                         'simulation_cost_id': w_simulation_cost_id
                         }
        account_analytic_line_obj.create(cr, uid, line_vals, context=context)
        return True

    def _sale_order_modification(self, cr, uid, simulation_cost_line,
                                 saleline, account_analytic_account_id,
                                 account_analytic_journal_ids,
                                 account_account_ids, w_simulation_cost_id,
                                 context=None):
        account_analytic_line_obj = self.pool['account.analytic.line']
        project_financing_obj = self.pool['project.financing']
        account_simuline_obj = self.pool['account.analytic.simulation.line']
        # Busco el apunte MODIFICACION PRESUPUESTARIA
        bline_id = saleline.analytic_budgetary_line_id.id
        f = saleline.financial_source_line_id.id
        expense_area_id = saleline.simulation_cost_line_id.expense_area_id.id
        if simulation_cost_line.simulation_cost_id.generate_by_lines:
            name = saleline.simulation_cost_line_id.product_id.name
            simuline_id = saleline.simulation_cost_line_id.id
            cond = [('name', 'like', 'Modif.Budgetary - ' + name),
                    ('type', '=', 'modif_budgetary'),
                    ('account_analytic_line_budgetary_id', '=', bline_id),
                    ('account_analytic_line_financing_source_id', '=', f),
                    ('expense_area_id', '=', expense_area_id),
                    ('account_id', '=', account_analytic_account_id),
                    ('journal_id', '=', account_analytic_journal_ids[0]),
                    ('general_account_id', '=', account_account_ids[0]),
                    ('simulation_cost_line_id', '=', simuline_id),
                    ('simulation_cost_id', '=', w_simulation_cost_id)]
        else:
            name = saleline.simulation_cost_line_id.expense_area_id.name
            cond = [('name', 'like', 'Modif.Budgetary - ' + name),
                    ('type', '=', 'modif_budgetary'),
                    ('account_analytic_line_budgetary_id', '=', bline_id),
                    ('account_analytic_line_financing_source_id', '=', f),
                    ('expense_area_id', '=', expense_area_id),
                    ('account_id', '=', account_analytic_account_id),
                    ('journal_id', '=', account_analytic_journal_ids[0]),
                    ('general_account_id', '=', account_account_ids[0]),
                    ('simulation_cost_line_id', '=', False),
                    ('simulation_cost_id', '=', w_simulation_cost_id)]
        account_analytic_line_ids = account_analytic_line_obj.search(
            cr, uid, cond, context=context)
        if not account_analytic_line_ids:
            financied_amount = saleline.financied_amount
            if simulation_cost_line.simulation_cost_id.generate_by_lines:
                name = saleline.simulation_cost_line_id.product_id.name
                simuline_id = saleline.simulation_cost_line_id.id
                values_line = {'name': 'Modif.Budgetary - ' + name,
                               'type': 'modif_budgetary',
                               'account_analytic_line_budgetary_id': bline_id,
                               'account_analytic_line_financing_source_id': f,
                               'expense_area_id': expense_area_id,
                               'account_id': account_analytic_account_id,
                               'journal_id': account_analytic_journal_ids[0],
                               'general_account_id': account_account_ids[0],
                               'updated_expense_budget': financied_amount,
                               'simulation_cost_line_id': simuline_id,
                               'simulation_cost_id': w_simulation_cost_id
                               }
            else:
                name = saleline.simulation_cost_line_id.expense_area_id.name
                values_line = {'name': 'Modif.Budgetary - ' + name,
                               'type': 'modif_budgetary',
                               'account_analytic_line_budgetary_id': bline_id,
                               'account_analytic_line_financing_source_id': f,
                               'expense_area_id': expense_area_id,
                               'account_id': account_analytic_account_id,
                               'journal_id': account_analytic_journal_ids[0],
                               'general_account_id': account_account_ids[0],
                               'updated_expense_budget': financied_amount,
                               'simulation_cost_line_id': False,
                               'simulation_cost_id': w_simulation_cost_id
                               }
            account_analytic_line_obj.create(cr, uid, values_line,
                                             context=context)
        else:
            account_analytic_line = account_analytic_line_obj.browse(
                cr, uid, account_analytic_line_ids[0], context=context)
            w_imp = (saleline.financied_amount +
                     account_analytic_line.remainder)
            account_analytic_line_obj.write(
                cr, uid, account_analytic_line_ids[0], {'remainder': w_imp},
                context=context)
        # CREO el apunte MODIFICACION FINANCIERA
        # Cojo el fondo financiador
        analytic_line = account_analytic_line_obj.browse(
            cr, uid, saleline.financial_source_line_id.id, context)
        project_financing = project_financing_obj.browse(
            cr, uid, analytic_line.project_financing_id.id, context)
        expense_area_id = saleline.simulation_cost_line_id.expense_area_id.id
        fs_id = saleline.financial_source_line_id.id
        partner = project_financing.financing_source_id.res_partner_id
        if simulation_cost_line.simulation_cost_id.generate_by_lines:
            name = (project_financing.name + ' - ' + saleline.product_id.name +
                    ' - ' +
                    saleline.simulation_cost_line_id.expense_area_id.name)
            simuline_id = saleline.simulation_cost_line_id.id
            line_vals = {'name': name,
                         'type': 'modif_financial_source',
                         'expense_area_id': expense_area_id,
                         'project_financing_id': project_financing.id,
                         'account_analytic_line_financing_source_id': fs_id,
                         'partner_id': partner.id,
                         'account_id': account_analytic_account_id,
                         'journal_id': account_analytic_journal_ids[0],
                         'general_account_id': account_account_ids[0],
                         'product_id': saleline.product_id.id,
                         'assigned': saleline.financied_amount,
                         'simulation_cost_line_id': simuline_id,
                         'simulation_cost_id': w_simulation_cost_id
                         }
        else:
            name = (project_financing.name + ' - ' +
                    saleline.simulation_cost_line_id.expense_area_id.name +
                    ' - ' + saleline.product_id.name)
            line_vals = {'name': name,
                         'type': 'modif_financial_source',
                         'expense_area_id': expense_area_id,
                         'project_financing_id': project_financing.id,
                         'account_analytic_line_financing_source_id': fs_id,
                         'partner_id': partner.id,
                         'account_id': account_analytic_account_id,
                         'journal_id': account_analytic_journal_ids[0],
                         'general_account_id': account_account_ids[0],
                         'product_id': saleline.product_id.id,
                         'assigned': saleline.financied_amount,
                         'simulation_cost_line_id': False,
                         'simulation_cost_id': w_simulation_cost_id
                         }
        account_analytic_line_id = account_analytic_line_obj.create(
            cr, uid, line_vals, context=context)
        # Doy de alta una fila en la tabla que relaciona partidas y
        # simulaciones
        simuline_id = saleline.simulation_cost_line_id.id
        expense_area_id = saleline.simulation_cost_line_id.expense_area_id.id
        line_vals = {'account_analytic_line_id': account_analytic_line_id,
                     'simulation_cost_id':  w_simulation_cost_id,
                     'simulation_cost_line_id': simuline_id,
                     'expense_area_id': expense_area_id,
                     'project_financing_id': project_financing.id,
                     'amount': saleline.financied_amount
                     }
        account_simuline_obj.create(cr, uid, line_vals, context)
        return True
