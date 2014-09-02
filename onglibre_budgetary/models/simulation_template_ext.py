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
from openerp import models, fields, _, api, exceptions


class SimulationTemplate(models.Model):
    _inherit = 'simulation.template'

    amortization_template_lines_ids = fields.One2many(
        'simulation.template.line', 'template_id', string='Amortization Lines',
        domain=[('type_cost', '=', 'Amortization')])
    # Categorias asociadas a la simulacion de coste
    expense_area_ids = fields.Many2many(
        'expense.area', string='Expense Areas')
    # Categorias Permitidas/Excluidas en la plantilla de simulacion
    simulation_template_category_ids = fields.One2many(
        'simulation.template.category', 'simulation_template_id',
        string='Categories', attrs={'readonly': [('historical_ok', '=',
                                                  True)]})

    @api.one
    @api.onchange("expense_area_ids")
    def onchange_expense_area(self):
        my_category = []
        for area in self.expense_area_ids:
            for category in area.category_ids:
                my_category.append({'expense_area_id': area.id,
                                    'category_id': category.id})
        self.simulation_template_category_ids = my_category
            #item = simulation_category[2]
                #if item.get('expense_area_id') in expense_area_ids[0][2]:
                    #my_category.append(simulation_category[2])
        #for expense_area in expense_area_ids:
            #if expense_area[2]:
                #expense_area2 = expense_area_obj.browse(expense_area[2])
                #for exp_area2 in expense_area2:
                    #if exp_area2.category_ids:
                        #for category in exp_area2.category_ids:
                            #found = 0
                            #for simulation_category in template_category_ids:
                                #if simulation_category[2]:
                                    #mycategory = simulation_category[2]
                                    #if (mycategory.get('expense_area_id') ==
                                            #exp_area2.id and
                                            #mycategory.get('category_id') ==
                                            #category.id):
                                        #found = 1
                            #if found == 0:
                                #line_vals = {'simulation_template_id': ids[0],
                                             #'expense_area_id': exp_area2.id,
                                             #'category_id': category.id
                                             #}
                                #my_category.append((0, 0, line_vals))
        #res = {'simulation_template_category_ids':  my_category}
        #print '*** res: ' + str(res)
        #return {'value': res}
