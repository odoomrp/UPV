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


class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    def _have_comment_ref(self, cr, uid, ids, name, args, context=None):
        res = {}
        for account_invoice in self.browse(cr, uid, ids, context=context):
            if account_invoice.comment:
                res[account_invoice.id] = True
            else:
                res[account_invoice.id] = False
        return res

    _columns = {
        # Campo para indicar si la factura tiene comentarios
        'have_comment':
            fields.function(_have_comment_ref, method=True, type="boolean",
                            string='HaveComments', store=False),
    }


class AccountInvoiceLine(orm.Model):
    _inherit = 'account.invoice.line'

    def _calc_paid_import(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            paid = line.invoice_id.amount_total - line.invoice_id.residual
            res[line.id] = paid
        return res

    def _calc_last_pay_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            last_date = False
            if line.invoice_id and line.invoice_id.move_id:
                for m_line in line.invoice_id.move_id.line_id:
                    if m_line.date_maturity:
                        if m_line.date_maturity > last_date:
                            last_date = m_line.date_maturity
            res[line.id] = last_date
        return res

    def _calc_purchase_type(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            purchase_type = False
            p_line_list = line.purchase_line_ids
            if p_line_list:
                p_line = p_line_list[0]
                purchase_type = p_line.order_id.type.id
            res[line.id] = purchase_type
        return res

    def _calc_project_list(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            text = ''
            for p_line in line.project_ids:
                if text == '':
                    text = p_line.project_id.name
                else:
                    text = text + ' : ' + p_line.project_id.name
            res[line.id] = text
        return res

    def _get_project(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            analy_name = ''
            project_id = line.account_analytic_id.name
            if project_id:
                analy_name = project_id.split('-')[0]
            res[line.id] = analy_name
        return res

    def onchange_to_import(self, cr, uid, ids, to_import, subtotal,
                           context=None):
        if isinstance(ids, int):
            ids = [ids]
        to_percent = 0.0
        if subtotal:
            to_percent = (to_import / subtotal) * 100
        return {'value': {'to_justified_percent': to_percent}}

    def onchange_to_percent(self, cr, uid, ids, to_percent, subtotal,
                            context=None):
        if isinstance(ids, int):
            ids = [ids]
        to_import = (subtotal * to_percent) / 100
        return {'value': {'to_justified_import': to_import}}

    _columns = {
        'vat':
            fields.related('partner_id', 'vat', type="char", string="VAT",
                           size=32, store=False),
        'inv_date':
            fields.related('invoice_id', 'date_invoice', type="date",
                           string="Invoice Date", store=True),
        'move_id':
            fields.related('invoice_id', 'move_id', type="many2one",
                           relation="account.move", string="Journal Entry",
                           store=False),
        'justified_percent':
            fields.float('Justified %', digits=(10, 2), readonly=True),
        'justified_import':
            fields.float('Justified amount',
                         digits_compute=dp.get_precision('Account'),
                         readonly=True),
        'paid_import':
            fields.function(_calc_paid_import, method=True, type="float",
                            digits_compute=dp.get_precision('Account'),
                            string="Amount paid", store=False),
        'last_pay_date':
            fields.function(_calc_last_pay_date, method=True, type="date",
                            string="Payment date", store=False),
        'purchase_type':
            fields.function(_calc_purchase_type, method=True, type="many2one",
                            relation='purchase.type', string="Purchase type",
                            store=True),
        'purchase_line_ids':
            fields.many2many('purchase.order.line',
                             'purchase_order_line_invoice_rel', 'invoice_id',
                             'order_line_id', string='Purchase Lines',
                             readonly=True),
        'invoice_type':
            fields.related('invoice_id', 'type', type="selection",
                           selection=[('out_invoice', 'Customer Invoice'),
                                      ('in_invoice', 'Supplier Invoice'),
                                      ('out_refund', 'Customer Refund'),
                                      ('in_refund', 'Supplier Refund')],
                           string="Invoice type", store=True),
        'justification_ids':
            fields.many2many('project.justification',
                             'invoice_justification_lines_rel',
                             'invoice_line_id', 'justification_id',
                             'Justifications'),
        'project_ids':
            fields.many2many('project.justification',
                             'invoice_justification_lines_rel',
                             'invoice_line_id', 'justification_id',
                             'Justifications'),
        'project_text_list':
            fields.function(_calc_project_list, method=True, type="text",
                            string="Projects", store=False),
        'to_justified_import':
            fields.float('Import to justified',
                         digits_compute=dp.get_precision('Account')),
        'to_justified_percent': fields.float('Percent to justified',
                                             digits=(10, 2)),
        'justified_invoice_id':
            fields.one2many('justified.invoice.import', 'invoice_line_id',
                            'Justified Imports'),
        'check_justification': fields.boolean('Chose'),
        'project_id':
            fields.function(_get_project, method=True, string='Project',
                            type="char", size=128, store=True),
        'state':
            fields.related('invoice_id', 'state', type="selection",
                           selection=[('draft', 'Draft'),
                                      ('proforma', 'Pro-forma'),
                                      ('proforma2', 'Pro-forma'),
                                      ('open', 'Open'),
                                      ('paid', 'Paid'),
                                      ('cancel', 'Cancelled')],
                           string="Invoice state", store=True),
        'note':fields.char('Notes', size=128),
    }
    _defaults = {'invoice_type': lambda self, cr, uid, c:
                 c.get('invoice_type', False)
                 }
