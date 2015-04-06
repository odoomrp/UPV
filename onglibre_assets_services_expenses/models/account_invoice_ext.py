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
from openerp import models, api, _
from openerp.exceptions import except_orm
import time


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.multi
    def action_move_create(self):
        print '*** ESTOY EN ACTION_MOVE_CREATE'
        analytic_line_obj = self.env['account.analytic.line']
        res = super(AccountInvoice, self).action_move_create()
        for invoice in self:
            print '*** invoice_type: ' + str(invoice.type)
            if invoice.type in ('in_refund', 'in_invoice'):
                for line in invoice.invoice_line:
                    print '*** linea factura, fuentes financiación: ' + str(line.line_financing_source_ids)
                    if line.line_financing_source_ids:
                        for line2 in line.line_financing_source_ids:
                            w_importe2 = ((line.price_subtotal *
                                           line2.line_financing_percentage) /
                                          100)
                            journal_id = invoice.journal_id.analytic_journal_id
                            fsl = line2.financial_source_line_id
                            budget_id = fsl.account_analytic_line_budgetary_id
                            vals = {'name' : str(invoice.number),
                                    'account_id': line.account_analytic_id.id,
                                    'general_account_id': line.account_id.id,
                                    'journal_id': journal_id.id,
                                    'unit_amount': line.quantity,
                                    'product_id': line.product_id.id,
                                    'product_uom_id': line.uos_id.id,
                                    'sale_amount':  0,
                                    'type': 'imputation',
                                    'real_expense': w_importe2,
                                    'imputed': w_importe2,
                                    'expense_compromised': (w_importe2 * -1),
                                    'expense_area_id': fsl.expense_area_id.id,
                                    'account_analytic_line_financing_source'
                                    '_id': fsl.id,
                                    'account_analytic_line_budgetary_readonly'
                                    '_id': budget_id.id,
                                    'account_analytic_line_budgetary_id':
                                    budget_id.id,
                                    'account_invoice_line_id': line.id,
                                    'line_financing_source_id': line2.id,
                                    'expense_type': 'invoice_aproved'
                                  }
                            print '*** creo linea de analitica con vals: ' + str(vals)
                            analytic_line_obj.create(vals)
        return res

    @api.multi
    def action_cancel(self):
        # Borro los apuntes analiticos generados por la factura
        account_analytic_line_obj = self.env['account.analytic.line']
        for invoice in self:
            for invoice_line in invoice.invoice_line:
                if invoice.state == 'open':
                    cond = [('account_invoice_line_id', '=',
                             invoice_line.id),
                            ('expense_type', '=', 'invoice_aproved')]
                    analytic_line_ids = account_analytic_line_obj.search(cond)
                    if analytic_line_ids:
                        analytic_line_ids.unlink()
        super(AccountInvoice, self).action_cancel()
        return True

    @api.multi
    def _get_analytic_lines(self):
        """ Return a list of dict for creating analytic lines for self[0] """
        company_currency = self.company_id.currency_id
        sign = 1 if self.type in ('out_invoice', 'in_refund') else -1

        iml = self.env['account.invoice.line'].move_line_get(self.id)
        for il in iml:
            if il['account_analytic_id']:
                if self.type in ('in_invoice', 'in_refund'):
                    ref = self.reference
                else:
                    ref = self._convert_ref(self.number)
                if not self.journal_id.analytic_journal_id:
                    raise except_orm(_('No Analytic Journal!'),
                                     _("You have to define an analytic journal"
                                       " on the '%s' journal!") %
                                     (self.journal_id.name,))
                currency = self.currency_id.with_context(
                    date=self.date_invoice)
                il['analytic_lines'] = [(0, 0, {
                    'name': il['name'],
                    'date': self.date_invoice,
                    'account_id': il['account_analytic_id'],
                    'unit_amount': il['quantity'],
                    'amount': (currency.compute(il['price'], company_currency)
                               * sign),
                    'product_id': il['product_id'],
                    'product_uom_id': il['uos_id'],
                    'general_account_id': il['account_id'],
                    'journal_id': self.journal_id.analytic_journal_id.id,
                    'ref': ref,
                    'account_invoice_line_id': il['account_invoice_line_id'],
                    'budgetary_line_id': il['budgetary_line_id'],
                    'line_financing_source_ids':
                    il['line_financing_source_ids'],
                    'account_analytic_line_budgetary_id':
                    il['account_analytic_line_budgetary_id'],
                    'account_analytic_line_budgetary_readonly_id':
                    il['account_analytic_line_budgetary_readonly_id']
                })]
        return iml

    @api.model
    def line_get_convert(self, x, part, date):
        res = super(AccountInvoice, self).line_get_convert(x, part, date)
        res.update({
            'account_invoice_line_id': x.get('account_invoice_line_id', False),
            'budgetary_line_id': x.get('budgetary_line_id', False),
            'line_financing_source_ids':
            x.get('line_financing_source_ids', False),
            'account_analytic_line_budgetary_id':
            x.get('account_analytic_line_budgetary_id', False),
            'account_analytic_line_budgetary_readonly_id':
            x.get('account_analytic_line_budgetary_readonly_id', False), })
        return res

        return True

    def _refund_cleanup_lines(self, cr, uid, lines):
        for line in lines:
            del line['id']
            del line['invoice_id']
            if line.get('line_financing_source_ids'):
                    line.pop('line_financing_source_ids')
            for field in ('company_id', 'partner_id', 'account_id',
                          'product_id', 'uos_id', 'account_analytic_id',
                          'tax_code_id', 'base_code_id', 'budgetary_line_id',
                          'purchase_type', 'move_id'):
                if line.get(field):
                    line[field] = line[field][0]
            if 'invoice_line_tax_id' in line:
                line['invoice_line_tax_id'] = [(6, 0,
                                                line.get('invoice_line_tax_id',
                                                         []))]
        return map(lambda x: (0, 0, x), lines)

    def refund(self, cr, uid, ids, date=None, period_id=None, description=None,
               journal_id=None):
        obj_invoice_line = self.pool['account.invoice.line']
        obj_invoice_tax = self.pool['account.invoice.tax']
        obj_journal = self.pool['account.journal']
        financing_line_obj = self.pool['line.financing.source']
        invoices = self.read(
            cr, uid, ids, ['name', 'type', 'number', 'reference', 'comment',
                           'date_due', 'partner_id', 'address_contact_id',
                           'address_invoice_id', 'partner_contact',
                           'partner_insite', 'partner_ref', 'payment_term',
                           'account_id', 'currency_id', 'invoice_line',
                           'tax_line', 'journal_id', 'payment_type'])
        new_ids = []
        for invoice in invoices:
            old_invoice_id = invoice['id']
            del invoice['id']
            type_dict = {
                'out_invoice': 'out_refund',
                'in_invoice': 'in_refund',
                'out_refund': 'out_invoice',
                'in_refund': 'in_invoice'
            }
            invoice_lines = obj_invoice_line.read(cr, uid,
                                                  invoice['invoice_line'])
            invoice_lines = self._refund_cleanup_lines(cr, uid, invoice_lines)
            tax_lines = obj_invoice_tax.read(cr, uid, invoice['tax_line'])
            tax_lines = filter(lambda l: l['manual'], tax_lines)
            tax_lines = self._refund_cleanup_lines(cr, uid, tax_lines)
            if journal_id:
                refund_journal_ids = [journal_id]
            elif invoice['type'] == 'in_invoice':
                cond = [('type', '=', 'purchase_refund')]
                refund_journal_ids = obj_journal.search(cr, uid, cond)
            else:
                cond = [('type', '=', 'sale_refund')]
                refund_journal_ids = obj_journal.search(cr, uid, cond)
            if not date:
                date = time.strftime('%Y-%m-%d')
            invoice.update({
                'type': type_dict[invoice['type']],
                'date_invoice': date,
                'state': 'draft',
                'number': False,
                'invoice_line': invoice_lines,
                'tax_line': tax_lines,
                'journal_id': refund_journal_ids
                })
            if period_id:
                invoice.update({
                    'period_id': period_id,
                })
            if description:
                invoice.update({
                    'name': description,
                })
            # take the id part of the tuple returned for many2one fields
            for field in ('address_contact_id', 'address_invoice_id',
                          'partner_id', 'account_id', 'currency_id',
                          'payment_term', 'journal_id', 'payment_type'):
                invoice[field] = invoice[field] and invoice[field][0]
            # create the new invoice
            new_invoice_id = self.create(cr, uid, invoice)
            new_ids.append(new_invoice_id)
            # Nuevo tratamiento para copiar financiadores de las lineas
            old_invoice = self.browse(cr, uid, old_invoice_id)
            new_invoice = self.browse(cr, uid, new_invoice_id)
            # Trato las lineas de la factura rectificativa
            for new_invoice_line in new_invoice.invoice_line:
                list = []
                for old_invoice_line in old_invoice.invoice_line:
                    # Busco las misma linea en la factura origen y la factura
                    # nueva
                    if (new_invoice_line.product_id.id ==
                            old_invoice_line.product_id.id and
                            new_invoice_line.price_unit ==
                            old_invoice_line.price_unit and
                            new_invoice_line.quantity ==
                            old_invoice_line.quantity and
                            new_invoice_line.discount ==
                            old_invoice_line.discount and
                            new_invoice_line.account_id.id ==
                            old_invoice_line.account_id.id and
                            new_invoice_line.budgetary_line_id.id ==
                            old_invoice_line.budgetary_line_id.id):
                        if old_invoice_line.line_financing_source_ids:
                            old_invline = old_invoice_line
                            for line in old_invline.line_financing_source_ids:
                                vals = {'purchase_order_line_id': False,
                                        'account_invoice_line_id': False}
                                new_id = financing_line_obj.copy(
                                    cr, uid, line.id, vals)
                                list.append(new_id)
                # Actualizo la linea de la factura con los financiadores
                vals = {'line_financing_source_ids': [(6, 0, list)]}
                obj_invoice_line.write(cr, uid, new_invoice_line.id, vals)
        return new_ids
