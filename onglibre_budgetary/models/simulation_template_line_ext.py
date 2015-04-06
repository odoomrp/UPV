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


class SimulationTemplateLine(orm.Model):
    _inherit = 'simulation.template.line'

    _columns = {
        # Tipo de coste
        'type_cost': fields.selection([('Purchase', 'Purchase'),
                                       ('Investment', 'Investment'),
                                       ('Subcontracting Services',
                                        'Subcontracting'),
                                       ('Task', 'Internal Task'),
                                       ('Others', 'Others'),
                                       ('Amortization', 'Amortizations I+D')],
                                      'Type of Cost'),
        # Area de Gasto
        'expense_area_id': fields.many2one('expense.area', 'Expense Area',
                                           required=True),
    }
    _defaults = {'template_id': lambda self, cr, uid, context:
                 context.get('template_id', False),
                 }

    def onchange_product(self, cr, uid, ids, product_id, context=None):
        res = {}
        if product_id:
            product_obj = self.pool['product.product']
            product = product_obj.browse(cr, uid, product_id, context)
            res = {'name': (product.name or ''),
                   'description': (product.description or ''),
                   'uom_id': product.uom_id.id,
                   'amortization_rate': product.amortization_rate,
                   'indirect_cost_rate': product.indirect_cost_rate,
                   }
        return {'value': res}

    def onchange_expense_area(self, cr, uid, ids, expense_area_id, template_id,
                              context=None):
        res = {}
        domain_product = {}
        domain_expense_area = {}
        simulation_template_obj = self.pool['simulation.template']
        # Accedo a los datos de la simulacion
        simulation_template = simulation_template_obj.browse(
            cr, uid, template_id, context)
        expense_area_ids = []
        if simulation_template.expense_area_ids:
            for expense_area in simulation_template.expense_area_ids:
                expense_area_ids.append(expense_area.id)
        domain_expense_area = [('id', 'in', expense_area_ids)]
        category_ids = []
        if expense_area_id:
            sim = simulation_template
            for simulation_category in sim.simulation_template_category_ids:
                if expense_area_id == simulation_category.expense_area_id.id:
                    if not simulation_category.restricted_category:
                        category_ids.append(simulation_category.category_id.id)
        domain_product = [('categ_id', 'in', category_ids)]
        res.update({'product_id': False})
        return {'value': res,
                #'domain': {'product_id': domain_product,
                           #'expense_area_id': domain_expense_area
                           #}
                }
