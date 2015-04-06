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
from openerp.osv import orm
from openerp.tools.translate import _


class AccountBankStatement(orm.Model):
    _inherit = 'account.bank.statement'

    def button_confirm_bank(self, cr, uid, ids, context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        financing_source_obj = self.pool['financing.source']
        # Verifico que la linea del extracto bancario tenga cuenta analitica
        # y fuente de financiacion
        for account_bank in self.browse(cr, uid, ids, context=context):
            for line in account_bank.line_ids:
                if not line.analytic_account_id:
                    raise orm.except_orm(_('No Analytic Account Found !'),
                                         _('Please define analytic account for'
                                           ' Entry Date: %s, '
                                           'Communication: %s,'
                                           ' Amount: %s') % (str(line.date),
                                                             line.name,
                                                             str(line.amount)))
                if not line.line_financing_source_ids:
                    raise orm.except_orm(_('No Financers Found !'),
                                         _('Please define financers for'
                                           ' Entry Date: %s, '
                                           'Communication: %s,'
                                           ' Amount: %s') % (str(line.date),
                                                             line.name,
                                                             str(line.amount)))
        # Llamo al metodo padre
        res = super(AccountBankStatement, self).button_confirm_bank(
            cr, uid, ids, context)
        # Control de Importes de Fuentes de Financiación
        datas = {}
        for account_bank in self.browse(cr, uid, ids, context=context):
            for line in account_bank.line_ids:
                w_contador = 0
                for line_financing_source in line.line_financing_source_ids:
                    w_contador = w_contador + 1
                w_contador2 = 0
                w_importe2 = 0
                w_importe3 = 0
                for line_fs in line.line_financing_source_ids:
                    w_contador2 = w_contador2 + 1
                    if w_contador == w_contador2:
                        w_importe2 = line.amount - w_importe3
                    else:
                        w_importe2 = ((line.amount *
                                       line_fs.line_financing_percentage) /
                                      100)
                        w_importe3 = w_importe3 + w_importe2
                    w_found = 0
                    for data in datas:
                        datos_array = datas[data]
                        fs_id = datos_array['financing_source_id']
                        amount = datos_array['amount']
                        li_fs = line_fs.financial_source_line_id
                        if fs_id == li_fs.financing_source_id.id:
                            w_found = 1
                            amount = amount + w_importe2
                            datas[data].update({'amount': amount})
                    if w_found == 0:
                        li_fs = line_fs.financial_source_line_id
                        vals = {'financing_source_id':
                                li_fs.financing_source_id.id,
                                'amount': w_importe2}
                        datas[(li_fs.financing_source_id.id)] = vals
        if datas:
            for data in datas:
                datos_array = datas[data]
                financing_source_id = datos_array['financing_source_id']
                amount = datos_array['amount']
                financing_source = financing_source_obj.browse(
                    cr, uid, financing_source_id, context)
                if financing_source.availability_fund == 'granted':
                    if amount > financing_source.grant:
                        raise orm.except_orm(_('Financing Source ERROR'),
                                             _("The Financing Source '%s', "
                                               "only have an amount available "
                                               "for %s euros and can not "
                                               "finance %s euros") %
                                             (financing_source.name,
                                              financing_source.grant, amount))
                if financing_source.availability_fund == 'accepted':
                    if amount > (financing_source.total_recognized +
                                 financing_source.transfered):
                        t = (financing_source.total_recognized +
                             financing_source.transfered)
                        raise orm.except_orm(_('Financing Source ERROR'),
                                             _("The Financing Source '%s', "
                                               "only have an amount available "
                                               "for %s euros and can not "
                                               "finance %s euros") %
                                             (financing_source.name, str(t),
                                              str(amount)))
                if financing_source.availability_fund == 'charged':
                    if amount > (financing_source.total_invoices_billed +
                                 financing_source.transfered):
                        t = (financing_source.total_invoices_billed +
                             financing_source.transfered)
                        raise orm.except_orm(_('Financing Source ERROR'),
                                             _("The Financing Source '%s', "
                                               "only have an amount available "
                                               "for %s euros and can not "
                                               "finance %s euros") %
                                             (financing_source.name, str(t),
                                              str(amount)))
        # Doy de alta líneas de analítica
        for account_bank in self.browse(cr, uid, ids, context=context):
            for line in account_bank.line_ids:
                w_contador = 0
                for line_financing_source in line.line_financing_source_ids:
                    w_contador = w_contador + 1
                w_contador2 = 0
                w_importe2 = 0
                w_importe3 = 0
                for lfs in line.line_financing_source_ids:
                    w_contador2 = w_contador2 + 1
                    if w_contador == w_contador2:
                        w_importe2 = line.amount - w_importe3
                    else:
                        perc = lfs.line_financing_percentage
                        w_importe2 = (line.amount * perc) / 100
                        w_importe3 = w_importe3 + w_importe2
                    sourceline = lfs.financial_source_line_id
                    lb_id = sourceline.account_analytic_line_budgetary_id.id
                    line = {'name': line.name,
                            'account_id': line.analytic_account_id.id,
                            'general_account_id': line.account_id.id,
                            'journal_id':
                            account_bank.journal_id.analytic_journal_id.id,
                            'sale_amount':  0,
                            'paid_expense': w_importe2,
                            'type': 'imputation',
                            'expense_area_id':
                            lfs.financial_source_line_id.expense_area_id.id,
                            'account_analytic_line_financing_source_id':
                            lfs.financial_source_line_id.id,
                            'account_analytic_line_budgetary_readonly_id':
                            lb_id,
                            'account_analytic_line_budgetary_id': lb_id,
                            'line_financing_source_id': lfs.id,
                            'expense_type': 'bank_statement',
                            'financing_source_id':
                            lfs.financial_source_line_id.financing_source_id.id
                            }
                    analytic_line_obj.create(cr, uid, line, vals, context)
        return res
