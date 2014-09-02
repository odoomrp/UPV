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


class ProjectFinancing(orm.Model):
    _inherit = 'project.financing'

    _columns = {
        # Porcentaje Total Reconocido
        'percentage_total_recognized': fields.float(
            '% Total Recognized', reaonly=True),
        # Porcentajte Total Facturas Emitidas
        'percentage_total_invoices_emitted': fields.float(
            '% Total Invoices Emitted', reaonly=True),
        # Porcentajte Total Facturas Cobradas
        'percentage_total_invoices_billed': fields.float(
            '% Total Invoices Billed', reaonly=True),
        # Campos económicos del proyecto
        'sum_expense_budget': fields.related(
            'project_id', 'sum_expense_budget', type='float',
            string='Expense Budget', readonly=True, store=True),
        'sum_remainder': fields.related(
            'project_id', 'sum_remainder', type='float', string='Remainder',
            readonly=True, store=True),
        'sum_expense_request': fields.related(
            'project_id', 'sum_expense_request', type='float',
            string='Expense Request', readonly=True, store=True),
        'sum_updated_expense_budget': fields.related(
            'project_id', 'sum_updated_expense_budget', type='float',
            string='Updated Expense Budget', readonly=True, store=True),
        'sum_expense_compromised': fields.related(
            'project_id', 'sum_expense_compromised', type='float',
            string='Expense Compromised', readonly=True, store=True),
        'sum_available_expense': fields.related(
            'project_id', 'sum_available_expense', type='float',
            string='Available Expense', readonly=True, store=True),
        'sum_real_expense': fields.related(
            'project_id', 'sum_real_expense', type='float',
            string='Real Expense', readonly=True, store=True),
        'sum_paid_expense': fields.related(
            'project_id', 'sum_paid_expense', type='float',
            string='Paid Expense', readonly=True, store=True),
        'sum_justified_expense': fields.related(
            'project_id', 'sum_justified_expense', type='float',
            string='Justified Expense', readonly=True, store=True),
    }
