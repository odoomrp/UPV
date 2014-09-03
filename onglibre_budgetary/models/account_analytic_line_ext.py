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


class AccountAnalyticLine(orm.Model):
    _inherit = 'account.analytic.line'

    _columns = {
        # Fondo Financiador
        'project_financing_id':
            fields.many2one('project.financing', 'Project Financing'),
        # Líneas de simulacion que financia
        'account_analytic_simulation_line_ids':
            fields.one2many('account.analytic.simulation.line',
                            'account_analytic_line_id',
                            'Account Analytic Simulation Lines'),
        # Simulación de costes
        'simulation_cost_id': fields.many2one('simulation.cost',
                                              'Simulation Cost'),
        # Linea de simulación a la que corresponde el apunte analitico. Este
        # campo se usa para cuando se generan lineas presupuestarias por cada
        # linea de simulacion
        'simulation_cost_line_id': fields.many2one('simulation.cost.line',
                                                   'Simulation Cost Line'),
        # Porcentaje de financiacion para lineas de tipo FINANCING SOURCE
        'financing_percentage': fields.float('Financing %', readonly=True),
        # Fuente de Financiacion
        'financing_source_id': fields.many2one('financing.source',
                                               'Financing Source'),
    }

    def create(self, cr, uid, data, context=None):
        if data is None:
            data = {}
        new_id = super(AccountAnalyticLine, self).create(cr, uid, data,
                                                         context=context)
        line = self.browse(cr, uid, new_id, context)
        if line.type:
            if line.type in('imputation', 'initial_budgetary',
                            'modif_budgetary', 'initial_financial_source',
                            'modif_financial_source'):
                fsource_id = line.account_analytic_line_financing_source_id.id
                line2 = self.browse(cr, uid, fsource_id, context=context)
                vals = {'financing_source_id': line2.financing_source_id.id}
                self.write(cr, uid, [line.id], vals, context=context)
            if line.simulation_cost_id:
                if line.simulation_cost_id.project_id:
                    project = line.simulation_cost_id.project_id
                    vals = {'project_id': project.id}
                    self.write(cr, uid, [line.id], vals, context=context)
        return new_id
