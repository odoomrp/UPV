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
from openerp import models, fields, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    # Fuente de Financiación
    financing_source_id = fields.Many2one(
        'financing.source', string='Financing Source')
    # Cliente
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 related='invoice_id.partner_id', store=True,
                                 default=lambda self:
                                 self._context.get('partner_id', False))

    @api.model
    def create(self, vals):
        origin = vals.get('origin')
        sale_order_obj = self.env['sale.order']
        invoice_line_id = super(AccountInvoiceLine, self).create(vals)
        invoice_line = self.browse(invoice_line_id.id)
        if not invoice_line.financing_source_id:
            if origin:
                cond = [('name', '=', origin)]
                sale_order = sale_order_obj.search(cond, limit=1)
                if sale_order:
                    for sale_line in sale_order.order_line:
                        if (sale_line.product_id.id ==
                            invoice_line.product_id.id and sale_line.name ==
                            invoice_line.name and sale_line.product_uom_qty ==
                            invoice_line.quantity and sale_line.price_unit ==
                            invoice_line.price_unit and sale_line.discount ==
                                invoice_line.discount):
                            if sale_line.financing_source_id:
                                val = {'financing_source_id':
                                       sale_line.financing_source_id.id}
                                self.write(val)
            else:
                if invoice_line.invoice_id.financing_source_id:
                    val = {'financing_source_id':
                           invoice_line.invoice_id.financing_source_id.id}
                    self.write(val)
        return invoice_line_id

    def unlink(self, cr, uid, ids, context=None):
        financing_source_obj = self.pool('financing.source')
        project_financing_obj = self.pool('project.financing')
        datas = {}
        if ids:
            for line in self.browse(cr, uid, ids, context=context):
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
        super(AccountInvoiceLine, self).unlink(cr, uid, ids, context=context)
        if ids:
            for data in datas:
                # Cojo los datos del array
                datos_array = datas[data]
                financing_source_id = datos_array['financing_source_id']
                cond = [('financing_source_id', '=', financing_source_id)]
                account_invoice_line_ids = self.search(cr, uid, cond,
                                                       context=context)
                if account_invoice_line_ids:
                    amount = 0
                    for invoice_line in self.browse(
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
                        cr, uid, financing_source_id, context)
                    if financing_source.project_ids:
                        for project_financing in financing_source.project_ids:
                            tie = 0
                            if project_financing.project_id:
                                for il in self.browse(
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
