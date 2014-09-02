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
from openerp.osv import fields, orm
from openerp.tools.translate import _
import datetime


class TransferFundWizard(orm.TransientModel):
    _name = "transfer.fund.wizard"
    _description = "Transfer Fund"

    _columns = {
        # Fecha del traspaso
        'date': fields.date('Date', required=True),
        # Importe del traspaso
        'amount': fields.float('Amount', digits=(2, 1), required=True),
        # Motivo
        'reason': fields.text('Reason'),
        # Fuente de Financiación Origen
        'financing_source_origin_id':
            fields.many2one('financing.source', 'Financing Source Origin',
                            readonly=True, required=True),
        # Fuente de Financiación Target
        'financing_source_target_id':
            fields.many2one('financing.source', 'Financing Source Target',
                            required=True),
        # Disponible Origen
        'available_origin': fields.float('Available Origin', digits=(2, 2),
                                         readonly=True),
        # Pendiente de Asignación Origen
        'pending_allocation_origin':
            fields.float('Pending Allocation Origin', digits=(2, 2),
                         readonly=True),
    }

    def default_get(self, cr, uid, fields_list, context=None):
        financing_source_obj = self.pool['financing.source']
        financing_source = financing_source_obj.browse(
            cr, uid, context['active_id'], context=context)
        if financing_source.financier_fund_income_id.own_fund:
            raise orm.except_orm(_('Error'),
                                 _('Financier Fund Income is own fund'))
        vals = {
            'financing_source_origin_id': context['active_id'],
            'date': datetime.date.today().strftime('%Y-%m-%d'),
            'available_origin': financing_source.sum_available_expense,
            'pending_allocation_origin': financing_source.pending_allocation,
            }
        return vals

    def transfer_fund(self, cr, uid, ids, context=None):
        financing_source_obj = self.pool['financing.source']
        res = {}
        for item in self.browse(cr, uid, ids, context):
            if item.amount <= 0:
                raise orm.except_orm(_('Error'),
                                     _('Amount must be a positive number'))
            financing_source = financing_source_obj.browse(
                cr, uid, context['active_id'], context=context)
            tuple = (financing_source.sum_available_expense,
                     financing_source.pending_allocation)
            limit = min(tuple)
            if item.amount <= limit:
                transfer_fund_obj = self.pool.get('transfer.fund')
                values = {
                    'date': item.date,
                    'amount': item.amount,
                    'reason': item.reason,
                    'financing_source_origin_id':
                    item.financing_source_origin_id.id,
                    'financing_source_target_id':
                    item.financing_source_target_id.id
                    }
                transfer_fund_obj.create(cr, uid, values, context)
            else:
                raise orm.except_orm(_('Error'),
                                     _('Amount value must not be greater than'
                                       ' minium value of Available and '
                                       'Pending Allocation'))
        return res

    def onchange_financing_source_origin(self, cr, uid, ids,
                                         financing_source_origin_id):
        financing_source_obj = self.pool['financing.source']
        if financing_source_origin_id:
            financing_source_origin = financing_source_obj.browse(
                cr, uid, financing_source_origin_id)
            domain = [('financier_fund_income_id', '=',
                       financing_source_origin.financier_fund_income_id.id)]
        return {'domain': {'financing_source_target_id': domain}}
