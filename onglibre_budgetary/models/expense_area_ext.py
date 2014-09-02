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


class ExpenseArea(orm.Model):
    _inherit = 'expense.area'

    _columns = {
        # Simulaciones asociadas al area de gasto
        'simulation_template_ids':
            fields.many2many('simulation.template',
                             'simulationtemplate_expensearea_rel',
                             'expense_area_id', 'simulation_template_id',
                             'Simulation Templates', readonly=True),
        # Plantillas de Simulaciones asociadas al area de gasto
        'simulation_cost_ids':
            fields.many2many('simulation.cost', 'simucost_expensearea_rel',
                             'expense_area_id', 'simulation_cost_id',
                             'Simulation Costs', readonly=True,
                             domain=[('state', '!=', 'closed')]),
        # Líneas de simulación asociadas al area de gasto
        'simulation_cost_line_ids':
            fields.many2many('simulation.cost.line',
                             'simucostline_expensearea_rel',
                             'expense_area_id', 'simulation_cost_line_id',
                             'Simulation Costs'),
        # Líneas de simulación asociadas al area de gasto
        'project_financing_ids':
            fields.many2many('project.financing',
                             'projectfinancing_expensearea_rel',
                             'expense_area_id', 'project_financing_id',
                             'Simulation Costs'),
    }
