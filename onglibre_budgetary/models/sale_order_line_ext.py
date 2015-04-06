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


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def fields_get(self, cr, uid, fields=None, context=None):
        res = super(SaleOrderLine, self).fields_get(cr, uid, fields, context)
        if 'simulation' not in context or not context['simulation']:
            if 'product_id' in res:
                res['product_id']['domain'] = [('sale_ok', '=', True),
                                               ('categ_id.type', '=',
                                                'normal')]
                my_context = context.copy()
                my_context['simulation'] = True
                res['context'] = my_context
        return res

    _columns = {
        # Cuenta Analitica
        'account_analytic_id':
            fields.many2one('account.analytic.account', 'Analytic Account'),
        # Campo para saber cual es su apunte de tipo PRESUPUESTARIA
        'analytic_budgetary_line_id':
            fields.many2one('account.analytic.line', 'Analytic Budgetary Line',
                            domain="[('type', '=', 'budgetary'), "
                            "('account_id','=',account_analytic_id)]"),
        # Campo para saber cual es su apunte de tipo FUENTE DE FINANCIACION
        'financial_source_line_id':
            fields.many2one('account.analytic.line', 'Financing Source Line',
                            domain="[('type', '=', 'financing_source'), "
                            "('account_analytic_line_budgetary_id', '=',"
                            "analytic_budgetary_line_id)]"),
        # Campo para saber que linea de simulación se refiere la linea de
        # venta
        'simulation_cost_line_id':
            fields.many2one('simulation.cost.line', 'Simulation Cost Line'),
        # Porcentaje que financia
        'financing_percentage': fields.float('Financing %'),
        # Importe financiado:
        'financied_amount':
            fields.float('Financied Amount',
                         digits_compute=dp.get_precision('Purchase Price'),
                         readonly=True),
    }

    def unlink(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context):
            if line.simulation_cost_line_id:
                if line.order_id.sale_type == 'initial':
                    self._drop_project_financing_initial(cr, uid, line,
                                                         context=context)
                else:
                    if line.order_id.sale_type == 'modification':
                        self._drop_project_financing_modification(
                            cr, uid, line, context=context)
        return super(SaleOrderLine, self).unlink(cr, uid, ids, context)

    def _drop_project_financing_initial(self, cr, uid, line, context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        project_financing_obj = self.pool['project.financing']
        # Borro datos de PROJECT_FINANCING
        if (line.simulation_cost_line_id.project_financing_id and
                not line.simulation_cost_line_id.financied_line):
            pfinancing = line.simulation_cost_line_id.project_financing_id
            w_imp = (line.simulation_cost_line_id.subtotal_purchase *
                     pfinancing.project_percent) / 100
            project_financing = project_financing_obj.browse(
                cr, uid, line.simulation_cost_line_id.project_financing_id.id,
                context=context)
            w_imp2 = project_financing.amount_awarded - w_imp
            vals = {'amount_awarded': w_imp2,
                    'grant': w_imp2
                    }
            financing_id = line.simulation_cost_line_id.project_financing_id
            project_financing_obj.write(cr, uid, [financing_id.id], vals,
                                        context)
        else:
            # BUSCO FONDOS FINANCIADORES QUE FINANCIEN EL AREA DE GASTO DE LA
            # LINEA DE SIMULACION
            simulation_id = line.simulation_cost_line_id.simulation_cost_id.id
            expense_area_id = line.simulation_cost_line_id.expense_area_id.id
            cond = [('simulation_cost_id', '=', simulation_id),
                    ('expense_area_id', '=', expense_area_id)]
            project_financing_ids = project_financing_obj.search(
                cr, uid, cond, context)
            if not project_financing_ids:
                # BUSCO FONDOS FINANCIADORES QUE FINANCIEN TODAS LAS AREAS DE
                # GASTO
                cond = [('simulation_cost_id', '=', simulation_id),
                        ('expense_area_id', '=', False)]
                project_financing_ids = project_financing_obj.search(
                    cr, uid, cond, context)
            # TRATO LOS FONDOS FINANCIADORES
            if project_financing_ids:
                for project_financing in project_financing_obj.browse(
                        cr, uid, project_financing_ids, context=context):
                    w_imp = (line.simulation_cost_line_id.subtotal_purchase *
                             project_financing.project_percent) / 100
                    w_imp2 = project_financing.amount_awarded - w_imp
                    vals = {'amount_awarded': w_imp2,
                            'grant': w_imp2}
                    project_financing_obj.write(
                        cr, uid, [project_financing.id], vals, context)
        # BORRO LINEAS DE ANALITICA
        simulation_id = line.simulation_cost_line_id.simulation_cost_id.id
        expense_area_id = line.simulation_cost_line_id.expense_area_id.id
        budgetline_id = line.analytic_budgetary_line_id.id
        account_id = line.order_id.project2_id.analytic_account_id.id
        fsl_id = line.financial_source_line_id.id
        if line.simulation_cost_line_id.simulation_cost_id.generate_by_lines:
            simulation_line_id = line.simulation_cost_line_id.id
            cond = [('type', '=', 'initial_budgetary'),
                    ('simulation_cost_id', '=', simulation_id),
                    ('expense_area_id', '=', expense_area_id),
                    ('account_analytic_line_budgetary_id', '=', budgetline_id),
                    ('account_analytic_line_financing_source_id', '=', fsl_id),
                    ('account_id', '=', account_id),
                    ('product_id', '=', line.product_id.id),
                    ('unit_amount', '=', line.product_uom_qty),
                    ('expense_budget', '=', line.financied_amount),
                    ('updated_expense_budget', '=', line.financied_amount),
                    ('simulation_cost_line_id', '=', simulation_line_id)]
        else:
            cond = [('type', '=', 'initial_budgetary'),
                    ('simulation_cost_id', '=', simulation_id),
                    ('expense_area_id', '=', expense_area_id),
                    ('account_analytic_line_budgetary_id', '=', budgetline_id),
                    ('account_analytic_line_financing_source_id', '=', fsl_id),
                    ('account_id', '=', account_id.id),
                    ('product_id', '=', line.product_id.id),
                    ('unit_amount', '=', line.product_uom_qty),
                    ('expense_budget', '=', line.financied_amount),
                    ('updated_expense_budget', '=', line.financied_amount),
                    ('simulation_cost_line_id', '=', False)]
        analytic_line_ids = analytic_line_obj.search(cr, uid, cond,
                                                     context=context)
        if analytic_line_ids:
            analytic_line_obj.unlink(cr, uid, analytic_line_ids, context)
        return True

    def _drop_project_financing_modificaction(self, cr, uid, line,
                                              context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        simulation_line_obj = self.pool['simulation.cost.line']
        project_financing_obj = self.pool['project.financing']
        # Borro los MODIF FINANCIAL SOURCE
        analytic_line = analytic_line_obj.browse(
            cr, uid, line.financial_source_line_id.id, context=context)
        project_financing = project_financing_obj.browse(
            cr, uid, analytic_line.project_financing_id.id, context=context)
        simulation_id = line.simulation_cost_line_id.simulation_cost_id.id
        expense_area_id = line.simulation_cost_line_id.expense_area_id.id
        fsl_id = line.financial_source_line_id.id
        partner_id = project_financing.financing_source_id.res_partner_id.id
        account_id = line.order_id.project2_id.analytic_account_id.id
        if line.simulation_cost_line_id.simulation_cost_id.generate_by_lines:
            cost_line_id = line.simulation_cost_line_id.id
            cond = [('type', '=', 'modif_financial_source'),
                    ('simulation_cost_id', '=', simulation_id),
                    ('expense_area_id', '=', expense_area_id),
                    ('project_financing_id', '=', project_financing.id),
                    ('account_analytic_line_financing_source_id', '=', fsl_id),
                    ('partner_id', '=', partner_id)
                    ('account_id', '=', account_id),
                    ('product_id', '=', line.product_id.id),
                    ('assigned', '=', line.financied_amount),
                    ('simulation_cost_line_id', '=', cost_line_id)]
        else:
            cond = [('type', '=', 'modif_financial_source'),
                    ('simulation_cost_id', '=', simulation_id),
                    ('expense_area_id', '=', expense_area_id),
                    ('project_financing_id', '=', project_financing.id),
                    ('account_analytic_line_financing_source_id', '=', fsl_id),
                    ('partner_id', '=', partner_id)
                    ('account_id', '=', account_id),
                    ('product_id', '=', line.product_id.id),
                    ('assigned', '=', line.financied_amount),
                    ('simulation_cost_line_id', '=', False)]
        analytic_line_ids = analytic_line_obj.search(cr, uid, cond,
                                                     context=context)
        if analytic_line_ids:
            analytic_line_obj.unlink(cr, uid, analytic_line_ids,
                                     context=context)
        # Borro los MODIF BUDGETARY
        bline_id = line.analytic_budgetary_line_id.id
        account_id = line.order_id.project2_id.analytic_account_id.id
        if line.simulation_cost_line_id.simulation_cost_id.generate_by_lines:
            cost_line_id = line.simulation_cost_line_id.id
            cond = [('type', '=', 'modif_budgetary'),
                    ('simulation_cost_id', '=', simulation_id),
                    ('expense_area_id', '=', expense_area_id),
                    ('account_analytic_line_budgetary_id', '=', bline_id),
                    ('account_analytic_line_financing_source_id', '=', fsl_id),
                    ('account_id', '=', account_id),
                    ('simulation_cost_line_id', '=', cost_line_id)]
        else:
            cond = [('type', '=', 'modif_budgetary'),
                    ('simulation_cost_id', '=', simulation_id),
                    ('expense_area_id', '=', expense_area_id),
                    ('account_analytic_line_budgetary_id', '=', bline_id),
                    ('account_analytic_line_financing_source_id', '=', fsl_id),
                    ('account_id', '=', account_id),
                    ('simulation_cost_line_id', '=', False)]
        analytic_line_ids = analytic_line_obj.search(cr, uid, cond,
                                                     context=context)
        if analytic_line_ids:
            for analytic_line in analytic_line_obj.browse(cr, uid,
                                                          analytic_line_ids,
                                                          context):
                if (analytic_line.updated_expense_budget ==
                        line.financied_amount):
                    if analytic_line.remainder:
                        if analytic_line.remainder > 0:
                            raise orm.except_orm(_('Error'),
                                                 _('You must be deleted before'
                                                   ' other lines'))
                        else:
                            analytic_line_obj.unlink(
                                cr, uid, [analytic_line.id], contexyt=context)
                    else:
                        analytic_line_obj.unlink(
                            cr, uid, [analytic_line.id], context=context)
                else:
                    w_imp = (line.financied_amount + analytic_line.remainder -
                             line.financied_amount)
                    vals = {'remainder': w_imp}
                    analytic_line_obj.write(cr, uid, analytic_line.id, vals,
                                            context=context)
        # Borro el id de la linea del pedido de venta de la línea de la
        # simulación
        simulation_line_id = line.simulation_cost_line_id.id
        cond = [('id', '!=', line.id),
                ('simulation_cost_line_id', '=', simulation_line_id)]
        order_line_ids = self.search(cr, uid, cond, limit=1)
        if not order_line_ids:
            vals = {'sale_order_line_id': False}
            simulation_line_obj.write(cr, uid, line.simulation_cost_line_id.id,
                                      vals, context=context)
        return True
