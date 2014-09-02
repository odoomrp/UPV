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
from openerp import models, fields, api, _


class PaymentOrderCreate(models.TransientModel):
    _inherit = 'payment.order.create'

    communication2 = fields.Char(
        string='Communication 2', size=64,
        help='The successor message of payment communication.')
    amount = fields.Float(
        string='Amount',
        help='Next step will automatically select payments up to this amount '
             'as long as account moves have bank account if that is required '
             'by the selected payment mode.')
    show_refunds = fields.Boolean(
        string='Show Refunds', default=False,
        help='Indicates if search should include refunds.')

    @api.model
    def default_get(self, fields):
        res = super(PaymentOrderCreate, self).default_get(fields)
        if 'entries' in fields:
            if self.env.context.get('line_ids'):
                res.update({'entries': self.env.context['line_ids']})
        return res

    @api.one
    @api.model
    def search_entries(self):
        payment_order_obj = self.env['payment.order']
        move_line_obj = self.env['account.move.line']
        mod_obj = self.env['ir.model.data']
        payment_order = payment_order_obj.browse(
            self.env.context.get('active_id'))
        # Search for move line to pay:
        domain = [('reconcile_id', '=', False),
                  ('account_id.type', '=', payment_order.type),
                  ('amount_to_pay', '<>', 0)]
        if not self.show_refunds:
            if payment_order.type == 'payable':
                domain += [('credit', '>', 0)]
            else:
                domain += [('debit', '>', 0)]
        if payment_order.mode:
            domain += [('payment_type', '=', payment_order.mode.type.id)]
        domain += ['|', ('date_maturity', '<', self.duedate),
                   ('date_maturity', '=', False)]
        move_lines = move_line_obj.search(domain, order='date_maturity')
        amount = self.amount
        if amount > 0.0:
            # If user specified an amount, search what moves match the criteria
            selected_lines = []
            for line in move_lines:
                if abs(line.amount_to_pay) <= amount:
                    amount -= abs(line.amount_to_pay)
                    selected_lines.append(line)
        elif not amount:
            selected_lines = move_lines
        #self.entries = selected_lines
        ctx = self.env.context.copy()
        ctx['entries'] = selected_lines
        model_datas = mod_obj.search(
            [('model', '=', 'ir.ui.view'),
             ('name', '=', 'view_create_payment_order_lines')])
        return {
            'name': _('Entrie Lines'),
            'context': ctx,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payment.order.create',
            'res_id': self.id,
            'views': [(model_datas[0].res_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def create_payment(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        order_obj = self.pool['payment.order']
        line_obj = self.pool['account.move.line']
        payment_obj = self.pool['payment.line']
        data = self.browse(cr, uid, ids, context=context)[0]
        line_ids = [entry.id for entry in data.entries]
        if not line_ids:
            return {'type': 'ir.actions.act_window_close'}
        payment = order_obj.browse(
            cr, uid, context['active_id'], context=context)
        t = payment.mode and payment.mode.id or None
        line2bank = line_obj.line2bank(cr, uid, line_ids, t, context)
        # Finally populate the current payment with new lines:
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            if payment.date_prefered == "now":
                date_to_pay = False
            elif payment.date_prefered == 'due':
                date_to_pay = line.date_maturity
            elif payment.date_prefered == 'fixed':
                date_to_pay = payment.date_scheduled
            if payment.type == 'payable':
                amount_to_pay = line.amount_to_pay
            else:
                amount_to_pay = -line.amount_to_pay
            vals = {'move_line_id': line.id,
                    'amount_currency': amount_to_pay,
                    'bank_id': line2bank.get(line.id),
                    'order_id': payment.id,
                    'partner_id': (line.partner_id and line.partner_id.id or
                                   False),
                    'communication': ((line.ref and line.name != '/' and
                                       line.ref + '. '+line.name) or line.ref
                                      or line.name or '/'),
                    'communication2': data.communication2,
                    'date': date_to_pay,
                    'currency': (line.invoice and line.invoice.currency_id.id
                                 or False),
                    'account_id': line.account_id.id
                    }
            payment_obj.create(cr, uid, vals, context=context)
        return {'type': 'ir.actions.act_window_close'}
