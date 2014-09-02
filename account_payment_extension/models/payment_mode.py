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


class PaymentMode(models.Model):
    _inherit = 'payment.mode'

    type = fields.Many2one(
        'payment.type', string='Payment type', required=True,
        help='Select the Payment Type for the Payment Mode.')
    require_bank_account = fields.Boolean(
        string='Require Bank Account', default=False,
        help='Ensure all lines in the payment order have a bank account when '
             'proposing lines to be added in the payment order.')
    require_received_check = fields.Boolean(
        string='Require Received Check',
        help='Ensure all lines in the payment order have the Received Check '
             'flag set.')
    require_same_bank_account = fields.Boolean(
        string='Require the Same Bank Account',
        help='Ensure all lines in the payment order and the payment mode have '
             'the same account number.')
