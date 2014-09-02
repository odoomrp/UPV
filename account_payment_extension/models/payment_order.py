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
from openerp import models, fields, api, exceptions, _


class PaymentOrder(models.Model):
    _inherit = 'payment.order'

    def _default_type(self):
        return self.env.context.get('type', 'payable')

    @api.model
    def _default_reference(self):
        sequence_obj = self.env['ir.sequence']
        type = self.env.context.get('type', 'payable')
        model = 'payment.order' if type == 'payable' else 'rec.payment.order'
        return sequence_obj.get(model)

    @api.model
    @api.returns('account.period')
    def _default_period(self):
        period_obj = self.env['account.period']
        try:
            # find() function will throw an exception if no period can be found
            # for current date. That should not be a problem because user would
            # be notified but as this model inherits an existing one, once
            # installed it will create the new field and try to update
            # existing records (even if there are no records yet) So we must
            # ensure no exception is thrown, otherwise the module can only be
            # installed once periods are created.
            periods = period_obj.find() #self.env.cr, self.env.uid)
            return periods[0]
        except:
            return False

    @api.one
    def _name_get(self):
        self.name = rec.reference

    type = fields.Selection(
        [('payable', 'Payable'), ('receivable', 'Receivable')],
        string='Type', readonly=True, select=True, default=_default_type)
    # invisible field to filter payment order lines by payment type
    payment_type = fields.Many2one('payment.type', related="mode.type",
                                   string="Payment type name")
    # The field name is necessary to add attachement documents to payment orders
    name = fields.Char(compute=_name_get, string="Name")
    create_account_moves = fields.Selection(
        [('bank-statement', 'Bank Statement'),
         ('direct-payment', 'Direct Payment')], string='Create Account Moves',
        required=True, states={'done': [('readonly', True)]},
        help='Indicates when account moves should be created for order payment '
             'lines. "Bank Statement" will wait until user introduces those '
             'payments in bank a bank statement. "Direct Payment" will mark '
             'all payment lines as payied once the order is done.',
        default='bank-statement')
    period_id = fields.Many2one(
        'account.period', string='Period',
        states={'done': [('readonly', True)]}, default=_default_period)

    #_defaults = {
        #'reference': _get_reference_default,
    #}

    @api.multi
    def unlink(self):
        for order in self:
            if order.state not in ('draft', 'cancel'):
                raise exceptions.Warning(
                    _('Invalid action!'),
                    _('You cannot delete payment order(s) which are already '
                      'confirmed or done!'))
        return super(PaymentOrder, self).unlink()

    @api.one
    def cancel_from_done(self):
        for line in self.line_ids:
            if line.payment_move_id:
                line.payment_move_id.button_cancel()
                line.payment_move_id.unlink()
        self.write({'state': 'cancel'})
        return True

    @api.multi
    @api.model
    def set_done_new(self):
        result = super(PaymentOrder, self).set_done()
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        currency_obj = self.env['res.currency']
        payment_line_obj = self.env['payment.line']
        currency = self.company_id.currency_id
        company_currency_id = currency.id
        for order in self:
            if order.create_account_moves != 'direct-payment':
                continue
            # This process creates a simple account move with bank and line
            # accounts and line's amount. At the end it will reconcile or
            # partial reconcile both entries if that is possible.
            move = move_obj.create(
                {'name': '/',
                 'journal_id': order.mode.journal.id,
                 'period_id': order.period_id.id})
            for line in order.line_ids:
                if not line.amount:
                    continue
                if not line.account_id:
                    raise exceptions.Warning(
                        _('Error!'),
                        _('Payment order should create account moves but line '
                          'with amount %.2f for partner "%s" has no account '
                          'assigned.') % (line.amount, line.partner_id.name))
                currency_id = (order.mode.journal.currency.id or
                               company_currency_id)
                line_amount = line.amount_currency or line.amount
                if line.type == 'receivable':
                    line_amount *= -1
                if line_amount >= 0:
                    account_id = order.mode.journal.default_credit_account_id.id
                else:
                    account_id = order.mode.journal.default_debit_account_id.id
                val = {}
                if currency_id != company_currency_id:
                    acc_cur = ((line_amount <= 0) and
                               order.mode.journal.default_debit_account_id
                               ) or line.account_id
                    ctx = context.copy()
                    ctx['res.currency.compute.account'] = acc_cur
                    line_amount = currency_obj.compute(
                        currency_id, company_currency_id, line_amount)
                    amount_cur = currency_obj.compute(company_currency_id,
                                                      currency_id, amount)
                    val['amount_currency'] = -amount_cur
                    val['currency_id'] = currency_id
                val.update({
                    'name': line.move_line_id.name or '/',
                    'move_id': move.id,
                    'date': order.date_done,
                    'ref': line.move_line_id.ref,
                    'partner_id': line.partner_id.id,
                    'account_id': line.account_id.id,
                    'debit': ((line_amount > 0) and line_amount) or 0.0,
                    'credit': ((line_amount < 0) and -line_amount) or 0.0,
                    'journal_id': order.mode.journal.id,
                    'period_id': order.period_id.id,
                    'currency_id': currency_id,
                    'state': 'valid'
                })
                if (line.account_id and line.account_id.currency_id and
                        line.account_id.currency_id.id != company_currency_id):
                    val['currency_id'] = line.account_id.currency_id.id
                    if company_currency_id == line.account_id.currency_id.id:
                        amount_cur = line_amount
                    else:
                        amount_cur = currency_obj.compute(
                            company_currency_id, line.account_id.currency_id.id,
                            amount)
                    val['amount_currency'] = amount_cur
                partner_line_id = move_line_obj.create(val, check=False)
                # Fill the secondary amount/currency
                # if currency is not the same than the company
                if currency_id != company_currency_id:
                    amount_currency = line_amount
                    move_currency_id = currency_id
                else:
                    amount_currency = False
                    move_currency_id = False
                move_line_obj.create({
                    'name': line.move_line_id.name or '/',
                    'move_id': move.id,
                    'date': order.date_done,
                    'ref': line.move_line_id.ref,
                    'partner_id': line.partner_id.id,
                    'account_id': account_id,
                    'debit': ((amount < 0) and -amount) or 0.0,
                    'credit': ((amount > 0) and amount) or 0.0,
                    'journal_id': order.mode.journal.id,
                    'period_id': order.period_id.id,
                    'amount_currency': amount_currency,
                    'currency_id': move_currency_id,
                    'state': 'valid',
                }, check=False)
                if line.move_line_id and not line.move_line_id.reconcile_id:
                    # If payment line has a related move line, we try to
                    # reconcile it with the move we just created.
                    lines_to_reconcile = [
                        partner_line_id,
                    ]
                    # Check if payment line move is already partially
                    # reconciled and use those moves in that case.
                    if line.move_line_id.reconcile_partial_id:
                        m = line.move_line_id
                        for rline in m.reconcile_partial_id.line_partial_ids:
                            lines_to_reconcile.append(rline.id)
                    else:
                        lines_to_reconcile.append(line.move_line_id.id)
                    amount = 0.0
                    for rline in move_line_obj.browse(lines_to_reconcile):
                        amount += rline.debit - rline.credit
                    if currency_obj.is_zero(currency, amount):
                        move_line_obj.reconcile(lines_to_reconcile, 'payment')
                    else:
                        move_line_obj.reconcile_partial(lines_to_reconcile,
                                                        'payment')
                # Annotate the move id
                line.write({'payment_move_id': move.id})
            # Post the move
            if order.mode.journal.entry_posted:
                move.post()
        return result

    def set_done(self, cr, uid, ids, context=None):
        result = super(PaymentOrder, self).set_done(cr, uid, ids, context)
        move_obj = self.pool['account.move']
        move_line_obj = self.pool['account.move.line']
        currency_obj = self.pool['res.currency']
        payment_line_obj = self.pool['payment.line']
        users_obj = self.pool['res.users']
        user = users_obj.browse(cr, uid, uid, context=context)
        currency = user.company_id.currency_id
        company_currency_id = currency.id
        for order in self.browse(cr, uid, ids, context):
            if order.create_account_moves != 'direct-payment':
                continue
            # This process creates a simple account move with bank and line
            # accounts and line's amount. At the end it will reconcile or
            # partial reconcile both entries if that is possible.
            vals = {'name': '/',
                    'journal_id': order.mode.journal.id,
                    'period_id': order.period_id.id
                    }
            move_id = move_obj.create(cr, uid, vals, context)
            for line in order.line_ids:
                if not line.amount:
                    continue
                if not line.account_id:
                    raise orm.except_orm(_('Error!'),
                                         _('Payment order should create '
                                           'account moves but line with '
                                           'amount %.2f for partner "%s" has '
                                           'no account assigned.')
                                         % (line.amount, line.partner_id.name))
                currency_id = (order.mode.journal.currency and
                               order.mode.journal.currency.id or
                               company_currency_id)
                if line.type == 'payable':
                    line_amount = line.amount_currency or line.amount
                else:
                    line_amount = -line.amount_currency or -line.amount
                mjournal = order.mode.journal
                if line_amount >= 0:
                    account_id = mjournal.default_credit_account_id.id
                else:
                    account_id = mjournal.default_debit_account_id.id
                acc_cur = ((line_amount <= 0) and
                           order.mode.journal.default_debit_account_id
                           ) or line.account_id
                ctx = context.copy()
                ctx['res.currency.compute.account'] = acc_cur
                amount = currency_obj.compute(cr, uid, currency_id,
                                              company_currency_id, line_amount,
                                              context=ctx)
                val = {
                    'name': (line.move_line_id and line.move_line_id.name or
                             '/'),
                    'move_id': move_id,
                    'date': order.date_done,
                    'ref': (line.move_line_id and line.move_line_id.ref or
                            False),
                    'partner_id': (line.partner_id and line.partner_id.id or
                                   False),
                    'account_id': line.account_id.id,
                    'debit': ((amount > 0) and amount) or 0.0,
                    'credit': ((amount < 0) and -amount) or 0.0,
                    'journal_id': order.mode.journal.id,
                    'period_id': order.period_id.id,
                    'state': 'valid'
                }
                if currency_id != company_currency_id:
                    vals['currency_id'] = currency_id
                    amount_cur = currency_obj.compute(cr, uid,
                                                      company_currency_id,
                                                      currency_id, amount,
                                                      context=ctx)
                    val['amount_currency'] = -amount_cur
                if (line.account_id and line.account_id.currency_id and
                        line.account_id.currency_id.id != company_currency_id):
                    val['currency_id'] = line.account_id.currency_id.id
                    if company_currency_id == line.account_id.currency_id.id:
                        amount_cur = line_amount
                    else:
                        amount_cur = currency_obj.compute(
                            cr, uid, company_currency_id,
                            line.account_id.currency_id.id, amount,
                            context=ctx)
                    val['amount_currency'] = amount_cur
                partner_line_id = move_line_obj.create(cr, uid, val,
                                                       context=context,
                                                       check=False)
                # Fill the secondary amount/currency
                # if currency is not the same than the company
                if currency_id != company_currency_id:
                    amount_currency = line_amount
                    move_currency_id = currency_id
                else:
                    amount_currency = False
                    move_currency_id = False

                move_line_obj.create(cr, uid, {
                    'name': (line.move_line_id and line.move_line_id.name or
                             '/'),
                    'move_id': move_id,
                    'date': order.date_done,
                    'ref': (line.move_line_id and line.move_line_id.ref or
                            False),
                    'partner_id': (line.partner_id and line.partner_id.id or
                                   False),
                    'account_id': account_id,
                    'debit': ((amount < 0) and -amount) or 0.0,
                    'credit': ((amount > 0) and amount) or 0.0,
                    'journal_id': order.mode.journal.id,
                    'period_id': order.period_id.id,
                    'amount_currency': amount_currency,
                    'currency_id': move_currency_id,
                    'state': 'valid',
                }, context=context, check=False)
                if line.move_line_id and not line.move_line_id.reconcile_id:
                    # If payment line has a related move line, we try to
                    # reconcile it with the move we just created.
                    lines_to_reconcile = [
                        partner_line_id,
                    ]
                    # Check if payment line move is already partially
                    # reconciled and use those moves in that case.
                    if line.move_line_id.reconcile_partial_id:
                        m = line.move_line_id
                        for rline in m.reconcile_partial_id.line_partial_ids:
                            lines_to_reconcile.append(rline.id)
                    else:
                        lines_to_reconcile.append(line.move_line_id.id)
                    amount = 0.0
                    for rline in move_line_obj.browse(cr, uid,
                                                      lines_to_reconcile,
                                                      context=context):
                        amount += rline.debit - rline.credit
                    if currency_obj.is_zero(cr, uid, currency, amount):
                        move_line_obj.reconcile(cr, uid, lines_to_reconcile,
                                                'payment', context=context)
                    else:
                        move_line_obj.reconcile_partial(cr, uid,
                                                        lines_to_reconcile,
                                                        'payment',
                                                        context=context)
                # Annotate the move id
                payment_line_obj.write(cr, uid, [line.id], {
                    'payment_move_id': move_id,
                }, context)
            # Post the move
            if order.mode.journal.entry_posted:
                move_obj.post(cr, uid, [move_id], context=context)
        return result


class PaymentLine(models.Model):
    _inherit = 'payment.line'

    move_line_id = fields.Many2one(
        'account.move.line', string='Entry line',
        domain="[('reconcile_id', '=', False),"
               " ('amount_to_pay', '<>', 0),"
               " ('account_id.type', '=', parent.type),"
               " ('payment_type', '=', payment_type.id)]",
        help='This Entry Line will be referred for the information of the '
             'ordering customer.')
    payment_move_id = fields.Many2one(
        'account.move', string='Payment Move', readonly=True,
        help='Account move that pays this debt.')
    account_id = fields.Many2one('account.account', string='Account')
    type = fields.Selection(related='order_id.type',
                            #selection=[('payable', 'Payable'),
                                  #('receivable', 'Receivable')],
                            string='Type', store=True),

    def _auto_init_old(self, cr, context=None):
        cr.execute("SELECT column_name FROM information_schema.columns WHERE "
                   "table_name = 'payment_line' and column_name='type'")
        if cr.fetchone():
            update_sign = False
        else:
            update_sign = True
        result = super(PaymentLine, self)._auto_init(cr, context=context)
        if update_sign:
            # Ensure related store value of field 'type' is updated in the
            # database. Note that by forcing the update here we also ensure
            # everything is done in the same transaction. Because
            # addons/__init__.py will execute a commit just after creating
            # table fields.
            result.sort()
            for item in result:
                item[1](cr, *item[2])
            # Change sign of 'receivable' payment lines
            cr.execute("UPDATE payment_line SET amount_currency = "
                       "-amount_currency WHERE type='receivable'")
        return result

    def onchange_move_line(self, cr, uid, ids, move_line_id, payment_type,
                           date_prefered, date_scheduled, currency=False,
                           company_currency=False, context=None):
        move_line_obj = self.pool['account.move.line']
        payment_order_obj = self.pool['payment.order']
        # Adds account.move.line name to the payment line communication
        res = super(PaymentLine, self).onchange_move_line(
            cr, uid, ids, move_line_id, payment_type, date_prefered,
            date_scheduled, currency, company_currency, context)
        if move_line_id:
            line = move_line_obj.browse(cr, uid, move_line_id, context)
            if line.name != '/':
                res['value']['communication'] = (res['value']['communication']
                                                 + '. ' + line.name)
            res['value']['account_id'] = line.account_id.id
            if context.get('order_id'):
                payment_order = payment_order_obj.browse(
                    cr, uid, context['order_id'], context=context)
                if payment_order.type == 'receivable':
                    res['value']['amount'] *= -1
                    res['value']['amount_currency'] *= -1
        return res
