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


class PaymentType(models.Model):
    _name = 'payment.type'
    _description = 'Payment type'

    name = fields.Char('Name', size=64, required=True, help='Payment Type',
                       translate=True)
    code = fields.Char('Code', size=64, required=True,
                       help='Specify the Code for Payment Type')
    suitable_bank_types = fields.Many2many(
        'res.partner.bank.type', string='Suitable bank types')
    active = fields.Boolean('Active', select=True, default=True)
    note = fields.Text('Description', translate=True,
                       help="Description of the payment type that will be "
                            "shown in the invoices")
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'payment.type'))
