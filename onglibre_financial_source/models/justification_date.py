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


class JustificationDate(orm.Model):

    _name = 'justification.date'
    _description = 'Justification Date'

    _columns = {
        # Nombre
        'name': fields.char('Name', size=64, required=True),
        # Fecha
        'date': fields.date('Justification Date'),
        # Fuente de Financiación
        'financing_source_id':
            fields.many2one('financing.source', 'Financing Source'),
        # Apuntes Analíticos
        'account_analytic_line_ids':
            fields.many2many('account.analytic.line',
                             'justifdate_analyticline_rel',
                             'justification_date_id',
                             'account_analytic_line_id', 'Analytic Lines'),
        # WORKFLOW DE LA SIMULACION DEL COSTE
        'state': fields.selection([('draft', 'Draft'),
                                   ('confirmed', 'Confirmed'),
                                   ], 'State', readonly=True)
    }
    _defaults = {'state': lambda *a: 'draft',
                 'financing_source_id': lambda self, cr, uid,
                 context: context.get('my_finansource_id', False),
                 }

    def action_draft(self, cr, uid, ids):
        analytic_line_obj = self.pool['account.analytic.line']
        if ids:
            for justification in self.browse(cr, uid, ids):
                if justification.account_analytic_line_ids:
                    for line in justification.account_analytic_line_ids:
                        if line.type == 'justification':
                            analytic_line_obj.unlink(cr, uid, line.id)
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def action_confirm(self, cr, uid, ids):
        analytic_line_obj = self.pool['account.analytic.line']
        if ids:
            for justification in self.browse(cr, uid, ids):
                my_lines = []
                if justification.account_analytic_line_ids:
                    for line in justification.account_analytic_line_ids:
                        l = line
                        fsid = l.account_analytic_line_financing_source_id.id
                        bid = l.account_analytic_line_budgetary_readonly_id.id
                        if line.type == 'imputation':
                            my_lines.append(line.id)
                            vals = {
                                'amount': line.amount,
                                'name': line.name,
                                'unit_amount': line.unit_amount,
                                'date': line.date,
                                'company_id': line.company_id.id,
                                'account_id': line.account_id.id,
                                'general_account_id':
                                line.general_account_id.id,
                                'product_id': line.product_id.id,
                                'product_uom_id': line.product_uom_id.id,
                                'journal_id': line.journal_id.id,
                                'amount_currency': line.amount_currency,
                                'ref': line.ref,
                                'expense_compromised': 0,
                                'project_id': line.project_id.id,
                                'type': 'justification',
                                'available_expense': 0,
                                'real_expense': 0,
                                'justified_expense': line.real_expense,
                                'account_analytic_line_budgetary_id':
                                line.account_analytic_line_budgetary_id.id,
                                'account_analytic_line_financing_source_id':
                                fsid,
                                'parent_line_id': line.parent_line_id.id,
                                'account_analytic_line_budgetary_readonly_id':
                                bid,
                                'expense_area_id':
                                line.expense_area_id.id,
                                'financing_source_id':
                                line.financing_source_id.id,
                                'account_invoice_line_id':
                                line.account_invoice_line_id.id,
                                'line_financing_source_id':
                                line.line_financing_source_id.id,
                                'expense_type': 'justification'
                                    }
                            new_id = analytic_line_obj.create(cr, uid, vals)
                            my_lines.append(new_id)
                if my_lines:
                    vals = {'account_analytic_line_ids': [(6, 0, my_lines)]}
                    self.write(cr, uid, [justification.id], vals)
        self.write(cr, uid, ids, {'state': 'confirmed'})
        return True
