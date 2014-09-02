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


class AccountMoveReconcile(orm.Model):
    _inherit = 'account.move.reconcile'

    def unlink(self, cr, uid, ids, context=None):
        account_move_line_obj = self.pool['account.move.line']
        if ids:
            for reconcile in self.browse(cr, uid, ids, context=context):
                cond = [('reconcile_id', '=', reconcile.id)]
                account_move_line_ids = account_move_line_obj.search(
                    cr, uid, cond, context=context)
                if account_move_line_ids:
                    self._continue_unlink(cr, uid, account_move_line_ids,
                                          context=context)
        return super(AccountMoveReconcile, self).unlink(cr, uid, ids,
                                                        context=context)

    def _continue_unlink(self, cr, uid, account_move_line_ids, context=None):
        account_move_line_obj = self.pool['account.move.line']
        account_invoice_obj = self.pool['account.invoice']
        financing_source_obj = self.pool['financing.source']
        iline_obj = self.pool['account.invoice.line']
        project_financing_obj = self.pool['project.financing']
        w_found = 0
        for account_move_line in account_move_line_obj.browse(
                cr, uid, account_move_line_ids, context):
            if account_move_line.invoice and w_found == 0:
                w_found = 1
                if account_move_line.invoice:
                    account_invoice = account_invoice_obj.browse(
                        cr, uid, account_move_line.invoice.id, context)
                    for line in account_invoice.invoice_line:
                        if (line.financing_source_id and not
                                line.account_analytic_id):
                            financing_source = financing_source_obj.browse(
                                cr, uid, line.financing_source_id.id, context)
                            tib = (financing_source.total_invoices_billed -
                                   line.price_subtotal)
                            vals = {'total_invoices_billed': tib}
                            financing_source_obj.write(
                                cr, uid, [financing_source.id], vals, context)
                            financing_source = financing_source_obj.browse(
                                cr, uid, financing_source.id, context)
                            if financing_source.project_ids:
                                ids = financing_source.project_ids
                                for project_financing in ids:
                                    tib2 = 0
                                    if project_financing.project_id:
                                        p = project_financing.project_id
                                        if p.analytic_account_id:
                                            aa_id = p.analytic_account_id.id
                                            cond = [('account_analytic_id',
                                                     '=', aa_id)]
                                            line_ids = iline_obj.search(
                                                cr, uid, cond, context=context)
                                            if line_ids:
                                                for il in iline_obj.browse(
                                                    cr, uid, line_ids,
                                                        context):
                                                    ps = il.price_subtotal
                                                    if (il.invoice_id.state ==
                                                            'paid'):
                                                        tib2 += ps
                                    if tib == 0 or tib2 == 0:
                                        vals = {'percentage_total_invoices_'
                                                'billed': 0}
                                        project_financing_obj.write(
                                            cr, uid, [project_financing.id],
                                            vals, context=context)
                                    else:
                                        percentage_tib = (tib2 * 100) / tib
                                        vals = {'percentage_total_invoices_'
                                                'billed': percentage_tib}
                                        project_financing_obj.write(
                                            cr, uid, [project_financing.id],
                                            vals, context=context)
        return True
