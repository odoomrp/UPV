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


class PaymentOrderCreate(orm.TransientModel):
    _inherit = 'payment.order.create'

    _columns = {
        'communication2': fields.char(
            'Communication 2', size=64,
            help='The successor message of payment communication.'),
        'amount': fields.float(
            'Amount',
            help='Next step will automatically select payments up to this '
                 'amount as long as account moves have bank account if that '
                 'is required by the selected payment mode.'),
        'show_refunds': fields.boolean(
            'Show Refunds', help='Indicates if search should include refunds.'),
    }

    _defaults = {
        'show_refunds': False,
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(PaymentOrderCreate, self).default_get(
            cr, uid, fields, context=context)
        if 'entries' in fields:
            if context.get('line_ids'):
                res.update({'entries': context['line_ids']})
        return res

    def search_entries(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        order_obj = self.pool['payment.order']
        line_obj = self.pool['account.move.line']
        mod_obj = self.pool['ir.model.data']
        data = self.browse(cr, uid, ids, context=context)[0]
        search_due_date = data.duedate
        show_refunds = data.show_refunds
        amount = data.amount
        payment_order = order_obj.browse(cr, uid, context.get('active_id'),
                                         context=context)
        # Search for move line to pay:
        domain = [('reconcile_id', '=', False),
                  ('account_id.type', '=', payment_order.type),
                  ('amount_to_pay', '<>', 0)]
        if not show_refunds:
            if payment_order.type == 'payable':
                domain += [('credit', '>', 0)]
            else:
                domain += [('debit', '>', 0)]
        if payment_order.mode:
            domain += [('payment_type', '=', payment_order.mode.type.id)]
        domain += ['|', ('date_maturity', '<', search_due_date),
                   ('date_maturity', '=', False)]
        line_ids = line_obj.search(cr, uid, domain, order='date_maturity',
                                   context=context)
        selected_ids = []
        if amount > 0.0:
            # If user specified an amount, search what moves match the criteria
            for line in line_obj.browse(cr, uid, line_ids, context):
                if abs(line.amount_to_pay) <= amount:
                    amount -= abs(line.amount_to_pay)
                    selected_ids.append(line.id)
        elif not amount:
            selected_ids = line_ids
        ctx = context.copy()
        ctx.update({'line_ids': selected_ids})
        cond = [('model', '=', 'ir.ui.view'),
                ('name', '=', 'view_create_payment_order_lines')]
        model_data_ids = mod_obj.search(cr, uid, cond, context=context)
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'],
                                   context=context)[0]['res_id']
        return {
            'name': _('Entrie Lines'),
            'context': ctx,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payment.order.create',
            'views': [(resource_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def create_payment(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        order_obj = self.pool['payment.order']
        line_obj = self.pool['account.move.line']
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
            amount_to_pay = line.amount_to_pay
            if payment.type == 'receivable':
                amount_to_pay *= -1
            vals = {
                'move_line_id': line.id,
                'amount_currency': amount_to_pay,
                'bank_id': line2bank.get(line.id),
                'order_id': payment.id,
                'partner_id': line.partner_id.id,
                'communication': ((line.ref and line.name != '/' and
                                   line.ref + '. '+line.name) or line.ref
                                  or line.name or '/'),
                'communication2': data.communication2,
                'date': date_to_pay,
                'currency': line.invoice.currency_id.id,
                'account_id': line.account_id.id
            }
            self.pool['payment.line'].create(cr, uid, vals, context=context)
        return True
