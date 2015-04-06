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
from openerp import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # Fuente de Financiación
    financing_source_id = fields.Many2one(
        'financing.source', string='Financing Source')
    # Tipo Factura
    type = fields.Selection([('out_invoice', 'Customer Invoice'),
                             ('in_invoice', 'Supplier Invoice'),
                             ('out_refund', 'Customer Refund'),
                             ('in_refund', 'Supplier Refund'),
                             ], string='Type', readonly=True, index=True,
                            change_default=True, select=True,
                            track_visibility='always',
                            default=lambda self:
                            self._context.get('type', 'out_invoice'))
    partner_id = fields.Many2one(
        'res.partner', string='Partner', change_default=True, required=True,
        readonly=True, states={'draft': [('readonly', False)]},
        track_visibility='always',
        default=lambda self: self._context.get('partner_id', False))
    # RD SERPA
    rd_serpa = fields.Char(string='RD SERPA', size=32, readonly=True,
                           states={'draft': [('readonly', False)]})
    # Expendiente SERPA
    expedient_serpa = fields.Char(
        string='Expedient SERPA', readonly=True, size=128,
        states={'draft': [('readonly', False)]})
    # Fecha SERPA
    serpa_date = fields.Date(string='SERPA Date', readonly=True,
                             states={'draft': [('readonly', False)]})

    def create(self, cr, uid, vals, context=None):
        sale_order_obj = self.pool('sale.order')
        account_invoice_id = super(AccountInvoice, self).create(
            cr, uid, vals, context)
        invoice = self.browse(cr, uid, account_invoice_id, context=context)
        if invoice.type == 'out_invoice':
            if invoice.origin:
                if not invoice.financing_source_id:
                    cond = [('name', '=', invoice.origin)]
                    sale_order_ids = sale_order_obj.search(
                        cr, uid, cond, context=context)
                    if sale_order_ids:
                        sale_order = sale_order_obj.browse(
                            cr, uid, sale_order_ids[0], context=context)
                        if sale_order.financing_source_id:
                            val = {'financing_source_id':
                                   sale_order.financing_source_id.id}
                            self.write(cr, uid, [account_invoice_id], val,
                                       context=context)
        return account_invoice_id

    def write(self, cr, uid, ids, vals, context=None):
        financing_source_obj = self.pool('financing.source')
        account_invoice_line_obj = self.pool('account.invoice.line')
        project_financing_obj = self.pool('project.financing')
        w_found = 0
        if vals.get('state'):
            if vals.get('state') == 'open':
                w_found = 1
        res = super(AccountInvoice, self).write(cr, uid, ids, vals,
                                                context=context)
        if ids and w_found == 1:
            datas = {}
            for invoice in self.browse(cr, uid, ids, context):
                for line in invoice.invoice_line:
                    if line.financing_source_id:
                        found = 0
                        for data in datas:
                            datos_array = datas[data]
                            fs_id = datos_array['financing_source_id']
                            if fs_id == line.financing_source_id.id:
                                found = 1
                        if found == 0:
                            val = {'financing_source_id':
                                   line.financing_source_id.id}
                            datas[(line.financing_source_id.id)] = val
            for data in datas:
                # Cojo los datos del array
                datos_array = datas[data]
                financing_source_id = datos_array['financing_source_id']
                cond = [('financing_source_id', '=', financing_source_id)]
                account_invoice_line_ids = account_invoice_line_obj.search(
                    cr, uid, cond, context=context)
                if account_invoice_line_ids:
                    amount = 0
                    for invoice_line in account_invoice_line_obj.browse(
                            cr, uid, account_invoice_line_ids,
                            context=context):
                        if (invoice_line.invoice_id.state not in
                            ('cancel', 'draft') and not
                                invoice_line.account_analytic_id):
                            amount = amount + invoice_line.price_subtotal
                    val = {'total_invoices_emitted': amount}
                    financing_source_obj.write(cr, uid, [financing_source_id],
                                               val, context=context)
                    financing_source = financing_source_obj.browse(
                        cr, uid, financing_source_id, context=context)
                    if financing_source.project_ids:
                        for project_financing in financing_source.project_ids:
                            tim = 0
                            if project_financing.project_id:
                                for il in account_invoice_line_obj.browse(
                                        cr, uid, account_invoice_line_ids,
                                        context=context):
                                    if (il.invoice_id.state != 'cancel' and
                                            il.invoice_id.state != 'draft'):
                                        if il.account_analytic_id:
                                            p = project_financing.project_id
                                            if (p.analytic_account_id.id ==
                                                    il.account_analytic_id.id):
                                                tim += il.price_subtotal
                            if amount == 0 or tim == 0:
                                val = {'percentage_total_invoices_emitted': 0}
                                project_financing_obj.write(
                                    cr, uid, [project_financing.id], val,
                                    context=context)
                            else:
                                percentage_tim = (tim * 100) / amount
                                val = {'percentage_total_invoices_emitted':
                                       percentage_tim}
                                project_financing_obj.write(
                                    cr, uid, [project_financing.id], val,
                                    context=context)
        return res

    def action_cancel(self, cr, uid, ids, context=None):
        financing_source_obj = self.pool('financing.source')
        account_invoice_line_obj = self.pool('account.invoice.line')
        project_financing_obj = self.pool('project.financing')
        datas = {}
        super(AccountInvoice, self).action_cancel(cr, uid, ids, context)
        if ids:
            datas = {}
            for invoice in self.browse(cr, uid, ids, context=context):
                for line in invoice.invoice_line:
                    if line.financing_source_id:
                        found = 0
                        for data in datas:
                            datos_array = datas[data]
                            fs_id = datos_array['financing_source_id']
                            if fs_id == line.financing_source_id.id:
                                found = 1
                        if found == 0:
                            vals = {'financing_source_id':
                                    line.financing_source_id.id}
                            datas[(line.financing_source_id.id)] = vals
            for data in datas:
                # Cojo los datos del array
                datos_array = datas[data]
                financing_source_id = datos_array['financing_source_id']
                cond = [('financing_source_id', '=', financing_source_id)]
                account_invoice_line_ids = account_invoice_line_obj.search(
                    cr, uid, cond, context=context)
                if account_invoice_line_ids:
                    amount = 0
                    for invoice_line in account_invoice_line_obj.browse(
                            cr, uid, account_invoice_line_ids,
                            context=context):
                        if (invoice_line.invoice_id.state not in
                            ('cancel', 'draft') and not
                                invoice_line.account_analytic_id):
                            amount = amount + invoice_line.price_subtotal
                    vals = {'total_invoices_emitted': amount}
                    financing_source_obj.write(
                        cr, uid, [financing_source_id], vals, context=context)
                    financing_source = financing_source_obj.browse(
                        cr, uid, financing_source_id, context=context)
                    if financing_source.project_ids:
                        for project_financing in financing_source.project_ids:
                            tie = 0
                            if project_financing.project_id:
                                for il in account_invoice_line_obj.browse(
                                        cr, uid, account_invoice_line_ids,
                                        context=context):
                                    if (il.invoice_id.state != 'cancel' and
                                            il.invoice_id.state != 'draft'):
                                        if il.account_analytic_id:
                                            p = project_financing.project_id
                                            if (p.analytic_account_id.id ==
                                                    il.account_analytic_id.id):
                                                tie += il.price_subtotal
                            if amount == 0 or tie == 0:
                                vals = {'percentage_total_invoices_emitted': 0}
                                project_financing_obj.write(
                                    cr, uid, [project_financing.id], vals,
                                    context=context)
                            else:
                                percentage_tie = (tie * 100) / amount
                                vals = {'percentage_total_invoices_emitted':
                                        percentage_tie}
                                project_financing_obj.write(
                                    cr, uid, [project_financing.id], vals,
                                    context=context)
                else:
                    vals = {'total_invoices_emitted': 0}
                    financing_source_obj.write(
                        cr, uid, [financing_source_id], vals, context=context)
                    financing_source = financing_source_obj.browse(
                        cr, uid, financing_source_id, context=context)
                    if financing_source.project_ids:
                        for project_financing in financing_source.project_ids:
                            vals = {'percentage_total_invoices_emitted': 0}
                            project_financing_obj.write(
                                cr, uid, [project_financing.id], vals,
                                context=context)
        return True

    def action_cancel_draft(self, cr, uid, ids, *args):
        financing_source_obj = self.pool('financing.source')
        account_invoice_line_obj = self.pool('account.invoice.line')
        project_financing_obj = self.pool('project.financing')
        datas = {}
        super(AccountInvoice, self).action_cancel_draft(cr, uid, ids, *args)
        if ids:
            datas = {}
            for invoice in self.browse(cr, uid, ids):
                for line in invoice.invoice_line:
                    if line.financing_source_id:
                        found = 0
                        for data in datas:
                            datos_array = datas[data]
                            fs_id = datos_array['financing_source_id']
                            if fs_id == line.financing_source_id.id:
                                found = 1
                        if found == 0:
                            vals = {'financing_source_id':
                                    line.financing_source_id.id}
                            datas[(line.financing_source_id.id)] = vals
            for data in datas:
                # Cojo los datos del array
                datos_array = datas[data]
                financing_source_id = datos_array['financing_source_id']
                cond = [('financing_source_id', '=', financing_source_id)]
                account_invoice_line_ids = account_invoice_line_obj.search(
                    cr, uid, cond)
                if account_invoice_line_ids:
                    amount = 0
                    for invoice_line in account_invoice_line_obj.browse(
                            cr, uid, account_invoice_line_ids):
                        if (invoice_line.invoice_id.state not in
                            ('cancel', 'draft') and not
                                invoice_line.account_analytic_id):
                            amount = amount + invoice_line.price_subtotal
                    vals = {'total_invoices_emitted': amount}
                    financing_source_obj.write(cr, uid, [financing_source_id],
                                               vals)
                    financing_source = financing_source_obj.browse(
                        cr, uid, financing_source_id)
                    if financing_source.project_ids:
                        for project_financing in financing_source.project_ids:
                            tie = 0
                            if project_financing.project_id:
                                for il in account_invoice_line_obj.browse(
                                        cr, uid, account_invoice_line_ids):
                                    if (il.invoice_id.state != 'cancel' and
                                            il.invoice_id.state != 'draft'):
                                        if il.account_analytic_id:
                                            p = project_financing.project_id
                                            if (p.analytic_account_id.id ==
                                                    il.account_analytic_id.id):
                                                tie += il.price_subtotal
                            if amount == 0 or tie == 0:
                                vals = {'percentage_total_invoices_emitted': 0}
                                project_financing_obj.write(
                                    cr, uid, [project_financing.id], vals)
                            else:
                                percentage_tie = (tie * 100) / amount
                                vals = {'percentage_total_invoices_emitted':
                                        percentage_tie}
                                project_financing_obj.write(
                                    cr, uid, [project_financing.id], vals)
                else:
                    vals = {'total_invoices_emitted': 0}
                    financing_source_obj.write(cr, uid, [financing_source_id],
                                               vals)
                    financing_source = financing_source_obj.browse(
                        cr, uid, financing_source_id)
                    if financing_source.project_ids:
                        for project_financing in financing_source.project_ids:
                            vals = {'percentage_total_invoices_emitted': 0}
                            project_financing_obj.write(
                                cr, uid, [project_financing.id], vals)
        return True

    # Heredo accion de workflow cuando se paga la factura
    def confirm_paid(self, cr, uid, ids, context=None):
        financing_source_obj = self.pool('financing.source')
        account_invoice_line_obj = self.pool('account.invoice.line')
        project_financing_obj = self.pool('project.financing')
        datas = {}
        # Llamo al metodo super
        super(AccountInvoice, self).confirm_paid(cr, uid, ids, context)
        if ids:
            datas = {}
            for invoice in self.browse(cr, uid, ids, context=context):
                for line in invoice.invoice_line:
                    if line.financing_source_id:
                        found = 0
                        for data in datas:
                            datos_array = datas[data]
                            fs_id = datos_array['financing_source_id']
                            if fs_id == line.financing_source_id.id:
                                found = 1
                        if found == 0:
                            vals = {'financing_source_id':
                                    line.financing_source_id.id}
                            datas[(line.financing_source_id.id)] = vals
            for data in datas:
                # Cojo los datos del array
                datos_array = datas[data]
                financing_source_id = datos_array['financing_source_id']
                cond = [('financing_source_id', '=', financing_source_id)]
                account_invoice_ids = account_invoice_line_obj.search(
                    cr, uid, cond, context=context)
                if account_invoice_ids:
                    amount = 0
                    for invoice_line in account_invoice_line_obj.browse(
                            cr, uid, account_invoice_ids, context=context):
                        if (invoice_line.invoice_id.state == 'paid' and not
                                invoice_line.account_analytic_id):
                            amount = amount + invoice_line.price_subtotal
                    vals = {'total_invoices_billed': amount}
                    financing_source_obj.write(
                        cr, uid, [financing_source_id], vals, context=context)
                    financing_source = financing_source_obj.browse(
                        cr, uid, financing_source_id, context)
                    if financing_source.project_ids:
                        for project_financing in financing_source.project_ids:
                            tib = 0
                            if project_financing.project_id:
                                for il in account_invoice_line_obj.browse(
                                        cr, uid, account_invoice_ids, context):
                                    if il.invoice_id.state == 'paid':
                                        if il.account_analytic_id:
                                            p = project_financing.project_id
                                            if (p.analytic_account_id.id ==
                                                    il.account_analytic_id.id):
                                                tib += il.price_subtotal
                            if amount == 0 or tib == 0:
                                vals = {'percentage_total_invoices_billed': 0}
                                project_financing_obj.write(
                                    cr, uid, [project_financing.id], vals,
                                    context=context)
                            else:
                                percentage_tib = (tib * 100) / amount
                                vals = {'percentage_total_invoices_billed':
                                        percentage_tib}
                                project_financing_obj.write(
                                    cr, uid, [project_financing.id], vals,
                                    context=context)
                else:
                    vals = {'total_invoices_billed': 0}
                    financing_source_obj.write(
                        cr, uid, [financing_source_id], vals, context=context)
                    financing_source = financing_source_obj.browse(
                        cr, uid, financing_source_id, context)
                    if financing_source.project_ids:
                        for project_financing in financing_source.project_ids:
                            vals = {'percentage_total_invoices_billed': 0}
                            project_financing_obj.write(
                                cr, uid, [project_financing.id], vals,
                                context=context)
        return True
