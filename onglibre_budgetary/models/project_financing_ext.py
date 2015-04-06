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


class ProjectFinancing(orm.Model):
    _inherit = 'project.financing'

    _columns = {
        # Simulacion de costes
        'simulation_cost_id':
            fields.many2one('simulation.cost', 'Simulation Cost',
                            ondelete='cascade'),
        # Linea de simulacion de costes
        'simulation_cost_line_id':
            fields.many2one('simulation.cost.line', 'Simulation Cost Line',
                            ondelete='cascade'),
        # Estado de la simulacion
        'simulation_cost_state':
            fields.related('simulation_cost_id', 'state', type="selection",
                           selection=[('draft', 'Draft'),
                                      ('financing', 'Financing'),
                                      ('open', 'Open'),
                                      ('inmodif_budgetary',
                                       'In Budgetary Modification'),
                                      ('closed', 'Closed'),
                                      ('accepted', 'Accepted'),
                                      ('canceled', 'Canceled')],
                           string='Simulation Cost State', readonly=True),
        # Proyecto
        'project_id': fields.many2one('project.project', 'Project'),
        # Pedido de Venta
        'sale_order_id': fields.many2one('sale.order', 'Sale Order',
                                         readonly=True),
        # Importe factura venta
        'amount_untaxed':
            fields.related('sale_order_id', 'amount_untaxed', type='float',
                           string='Untaxed Amount', digits=(12, 2)),
        # Impuestos
        'amount_tax':
            fields.related('sale_order_id', 'amount_tax', type='float',
                           string='Taxes', digits=(12, 2)),
        # Impuestos
        'amount_total':
            fields.related('sale_order_id', 'amount_total', type='float',
                           string='Total', digits=(12, 2)),
        # Categorias asociadas a la Fuente de Financiacion de la simulacion
        'expense_area_ids':
            fields.many2many('expense.area',
                             'projectfinancing_expensearea_rel',
                             'project_financing_id', 'expense_area_id',
                             'Expense Areas'),
        # Financiador Tratado
        'treaty': fields.boolean('Treaty'),
    }
    _defaults = {
        'simulation_cost_id': lambda self, cr, uid, context:
            context.get('simulation_cost_id', False),
        'simulation_cost_state': lambda self, cr, uid, context:
            context.get('simulation_cost_state', False),
        'project_id': lambda self, cr, uid, context:
            context.get('simulation_cost_project_id', False),
            }

    def default_get(self, cr, uid, fields, context=None):
        my_expense_area = []
        if 'simu_expense_area_ids' in context:
            expense_area_ids = context['simu_expense_area_ids']
            for expense_area in expense_area_ids:
                if expense_area[2]:
                    my_expense_area = expense_area[2]
        res = super(ProjectFinancing, self).default_get(
            cr, uid, fields, context=context)
        res.update({'expense_area_ids': my_expense_area})
        return res

    def create(self, cr, uid, vals, context=None):
        simulation_obj = self.pool['simulation.cost']
        res = super(ProjectFinancing, self).create(cr, uid, vals, context)
        financing = self.browse(cr, uid, res, context)
        if financing.simulation_cost_id:
            simulation = simulation_obj.browse(
                cr, uid, financing.simulation_cost_id.id, context)
            if simulation.state in ('financing', 'inmodif_budgetary'):
                if not financing.project_id:
                    if simulation.project_id:
                        vals = {'project_id': simulation.project_id.id}
                        self.write(cr, uid, [res], vals, context)
            else:
                raise orm.except_orm(_('Invalid action !'),
                                     _('You cant not insert financers'))
        return res
