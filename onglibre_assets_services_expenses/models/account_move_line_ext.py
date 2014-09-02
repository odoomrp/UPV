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


class AccountMoveLine(orm.Model):
    _inherit = 'account.move.line'

    _columns = {
        # Linea de factura
        'account_invoice_line_id':
            fields.many2one('account.invoice.line', 'Invoice Line'),
        # Partida Presupuestaria
        'budgetary_line_id':
            fields.many2one('account.analytic.line', 'Budgetary Line',
                            domain="[('type', '=', 'budgetary'),"
                                   " ('account_id', '=',"
                                   " analytic_account_id)]"),
        # Fuentes de Financiación
        'line_financing_source_ids':
            fields.one2many('line.financing.source', 'account_move_line_id',
                            'Financing Sources'),
        # Padre Apunte Presupuestaria
        'account_analytic_line_budgetary_id':
            fields.many2one('account.analytic.line', 'Budgetary Parent',
                            domain=[('type', '=', 'budgetary')]),
        # Padre Apunte Presupuestaria sólo lectura
        'account_analytic_line_budgetary_readonly_id':
            fields.many2one('account.analytic.line', 'Budgetary Parent',
                            domain=[('type', '=', 'budgetary')]),
    }

    def create_analytic_lines(self, cr, uid, ids, context=None):
        print '*** ESTOY EN CREATE_ANALYTIC_LINES'
        acc_ana_line_obj = self.pool['account.analytic.line']
        for obj_line in self.browse(cr, uid, ids, context=context):
            if obj_line.analytic_account_id:
                if not obj_line.journal_id.analytic_journal_id:
                    raise orm.except_orm(_('No Analytic Journal !'),
                                         _("You have to define an analytic "
                                           "journal on the '%s' journal!") %
                                         (obj_line.journal_id.name, ))
                amt = (obj_line.credit or 0.0) - (obj_line.debit or 0.0)
                if not obj_line.line_financing_source_ids:
                    print '*** no tiene fuentes de financiacion'
                    vals_lines = {
                        'name': obj_line.name,
                        'date': obj_line.date,
                        'account_id': obj_line.analytic_account_id.id,
                        'unit_amount': obj_line.quantity,
                        'product_id': (obj_line.product_id and
                                       obj_line.product_id.id or False),
                        'product_uom_id': (obj_line.product_uom_id and
                                           obj_line.product_uom_id.id or
                                           False),
                        'amount': amt,
                        'general_account_id': obj_line.account_id.id,
                        'journal_id':
                        obj_line.journal_id.analytic_journal_id.id,
                        'ref': obj_line.ref,
                        'move_id': obj_line.id,
                        'user_id': uid
                        }
                else:
                    print '*** tiene fuentes de financiacion'
                    w_conta = 0
                    for line_financing in obj_line.line_financing_source_ids:
                        w_conta = w_conta + 1
                    w_conta2 = 0
                    w_importe2 = 0
                    for line_financing in obj_line.line_financing_source_ids:
                        w_conta2 = w_conta2 + 1
                        if w_conta == w_conta2:
                            w_importe = amt - w_importe2
                        else:
                            perc = line_financing.line_financing_percentage
                            w_importe = (amt * perc) / 100
                            w_importe2 = w_importe2 + w_importe
                        fsl = line_financing.financial_source_line_id
                        vals_lines = {
                            'name': obj_line.name,
                            'date': obj_line.date,
                            'account_id': obj_line.analytic_account_id.id,
                            'unit_amount': obj_line.quantity,
                            'product_id': (obj_line.product_id and
                                           obj_line.product_id.id or False),
                            'product_uom_id': (obj_line.product_uom_id and
                                               obj_line.product_uom_id.id or
                                               False),
                            'amount': w_importe,
                            'general_account_id': obj_line.account_id.id,
                            'journal_id':
                            obj_line.journal_id.analytic_journal_id.id,
                            'ref': obj_line.ref,
                            'move_id': obj_line.id,
                            'user_id': uid,
                            'expense_area_id': fsl.expense_area_id.id,
                            'account_analytic_line_financing_source_id':
                            fsl.id,
                            'account_analytic_line_budgetary_readonly_id':
                            fsl.account_analytic_line_budgetary_id.id,
                            'account_analytic_line_budgetary_id':
                            fsl.account_analytic_line_budgetary_id.id,
                            'account_invoice_line_id':
                            obj_line.account_invoice_line_id.id,
                            'line_financing_source_id': line_financing.id,
                            'expense_type': 'move_line'
                        }
                        acc_ana_line_obj.create(cr, uid, vals_lines, context)
        return True

    # OnChange de la Cuenta Analitica #
    def onchange_account(self, cr, uid, ids):
        financing_obj = self.pool['line.financing.source']
        if ids:
            for id in ids:
                line = self.browse(cr, uid, id)
                for line_financing in line.line_financing_source_ids:
                    financing_obj.unlink(cr, uid, line_financing.id)
        data = {'budgetary_line_id': None,
                'line_financing_source_ids': None
                }
        return {'value': data}

    # OnChange del campo Línea Presupuestaria #
    def onchange_budgetary_line(self, cr, uid, ids, account_analytic_id,
                                budgetary_line_id):
        financing_obj = self.pool['line.financing.source']
        analytic_line_obj = self.pool['account.analytic.line']
        if ids:
            for id in ids:
                line = self.browse(cr, uid, id)
                for line_financing in line.line_financing_source_ids:
                    financing_obj.unlink(cr, uid, line_financing.id)
        if not budgetary_line_id:
            data = {'line_financing_source_ids': None
                    }
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
                             financer.financing_percentage
                             })
            data = {'line_financing_source_ids': list}
        return {'value': data}
