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


class AccountBankStatementLine(orm.Model):
    _inherit = 'account.bank.statement.line'

    _columns = {
        'analytic_account_id': fields.many2one('account.analytic.account',
                                               'Analytic Account'),
        # Partida Presupuestaria
        'budgetary_line_id':
            fields.many2one('account.analytic.line', 'Budgetary Line',
                            domain="[('type', '=', 'budgetary'),"
                            " ('account_id', '=', analytic_account_id)]"),
        # Fuentes de Financiación
        'line_financing_source_ids':
            fields.one2many('line.financing.source',
                            'account_bank_statement_line_id',
                            'Financing Sources')
    }

    # OnChange de la Cuenta Analitica
    def onchange_account(self, cr, uid, ids):
        financing_obj = self.pool['line.financing.source']
        if ids:
            for line in self.browse(cr, uid, ids):
                for line_financing in line.line_financing_source_ids:
                    financing_obj.unlink(cr, uid, line_financing.id)
        data = {'budgetary_line_id': None,
                'line_financing_source_ids': None}
        return {'value': data}

    # OnChange del campo Línea Presupuestaria
    def onchange_budgetary_line(self, cr, uid,
                                ids, account_analytic_id, budgetary_line_id):
        financing_obj = self.pool['line.financing.source']
        analytic_line_obj = self.pool['account.analytic.line']
        if ids:
            for line in self.browse(cr, uid, ids):
                for line_financing in line.line_financing_source_ids:
                    financing_obj.unlink(cr, uid, line_financing.id)
        if not budgetary_line_id:
            data = {'line_financing_source_ids': None}
        else:
            budgetary_line = analytic_line_obj.browse(cr, uid,
                                                      budgetary_line_id)
            cond = [('type', '=', 'financing_source'),
                    ('account_analytic_line_budgetary_id', '=',
                     budgetary_line.id),
                    ('account_id', '=', budgetary_line.account_id.id),
                    ('journal_id', '=', budgetary_line.journal_id.id),
                    ('general_account_id', '=',
                     budgetary_line.general_account_id.id)]
            financers_ids = analytic_line_obj.search(cr, uid, cond)
            list = []
            for financer in analytic_line_obj.browse(cr, uid, financers_ids):
                list.append({'account_analytic_id': account_analytic_id,
                             'budgetary_line_id': budgetary_line_id,
                             'financial_source_line_id': financer.id,
                             'financing_percentage':
                             financer.financing_percentage,
                             'line_financing_percentage':
                             financer.financing_percentage})
            data = {'line_financing_source_ids': list}
        return {'value': data}
