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


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    payment_type = fields.Many2one('payment.type', string='Payment type')

    @api.multi
    def onchange_partner_id(
            self, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):
        result = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if type in ('in_invoice', 'in_refund'):
                payment_type = partner.payment_type_supplier.id
            else:
                payment_type = partner.payment_type_customer.id
            result['value']['payment_type'] = payment_type
        return result

    @api.multi
    def onchange_payment_type(self, payment_type_id, partner_id):
        payment_type_obj = self.env['payment.type']
        result = {'partner_bank_id': False}
        if payment_type_id and partner_id:
            payment_type = payment_type_obj.browse(payment_type_id)
            if payment_type.suitable_bank_types:
                bank_types = [x.code for x in payment_type.suitable_bank_types]
                partner_bank_obj = self.env['res.partner.bank']
                bank_account_ids = partner_bank_obj.search(
                    [('partner_id', '=', partner_id),
                     ('default_bank', '=', 1),
                     ('state', 'in', bank_types)])
                if bank_account_ids:
                    result['partner_bank_id'] = bank_account_ids[0]
        return {'value': result}

    @api.multi
    def action_move_create(self):
        """Write partner bank to move lines."""
        res = super(AccountInvoice, self).action_move_create()
        for invoice in self:
            if invoice.partner_bank_id:
                vals = {'partner_bank_id': invoice.partner_bank_id.id}
                for move_line in invoice.move_id.line_id:
                    if move_line.account_id.type in ('receivable', 'payable') \
                            and move_line.state != 'reconciled' \
                            and not move_line.reconcile_id.id:
                        move_line.write(vals)
        return res
