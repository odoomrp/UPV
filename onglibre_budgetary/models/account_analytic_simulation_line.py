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


class AccountAnalyticSimulationLine(orm.Model):
    _name = 'account.analytic.simulation.line'
    _description = 'Account Analytic Simulation Line'

    _columns = {
        # Linea de analítica
        'account_analytic_line_id':
            fields.many2one('account.analytic.line', 'Analytic Line',
                            ondelete='cascade'),
        # Simulacion
        'simulation_cost_id': fields.many2one('simulation.cost',
                                              'Simulation Cost'),
        # Línea de simulacion
        'simulation_cost_line_id': fields.many2one('simulation.cost.line',
                                                   'Simulation Cost Line'),
        # Area de Gasto
        'expense_area_id': fields.many2one('expense.area', 'Expense Area'),
        # Fondo Financiador
        'project_financing_id': fields.many2one('project.financing',
                                                'Project Financing'),
        # Porcentaje que financia
        'financing_percentage': fields.float('Financing %'),
        # Importe que financia
        'amount':
            fields.float('Amount',
                         digits_compute=dp.get_precision('Sale Price')),
    }
