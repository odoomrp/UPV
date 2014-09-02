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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    payment_type_customer = fields.Many2one(
        'payment.type', string='Customer Payment Type',
        help="Payment type of the customer", company_depending=True)
    payment_type_supplier = fields.Many2one(
        'payment.type', string='Supplier Payment Type',
        help="Payment type of the supplier", company_depending=True)


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    default_bank = fields.Boolean('Default')

    def _deactivate_default(self, cr, uid, partner_id, state, id=None,
                            context=None):
        """Remove default check in the rest of the banks of the partner."""
        partner_banks_ids = self.search(cr, uid,
                                        [('partner_id', '=', partner_id),
                                         ('default_bank', '=', True),
                                         ('id', '!=', id or False)],
                                        context=context)
        self.write(cr, uid, partner_banks_ids,
                   {'default_bank': False}, context=context)

    def create(self, cr, uid, vals, context=None):
        if 'default_bank' in vals and 'partner_id' in vals and 'state' in vals:
            self._deactivate_default(cr, uid, vals['partner_id'], vals['state'],
                                     context=context)
        return super(ResPartnerBank, self).create(cr, uid, vals,
                                                  context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('default_bank'):
            for partner_bank in self.browse(cr, uid, ids, context=context):
                state = vals.get('state') or partner_bank.state
                self._deactivate_default(cr, uid, partner_bank.partner_id.id,
                                         state, id=partner_bank.id)
        return super(ResPartnerBank, self).write(cr, uid, ids,
                                                 vals, context=context)