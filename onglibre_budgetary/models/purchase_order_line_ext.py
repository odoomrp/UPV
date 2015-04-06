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


class PurchaseOrderLine(orm.Model):
    _inherit = 'purchase.order.line'

    _columns = {
        'type': fields.related('order_id', 'type', 'name', type='char',
                               string='Type', size=128, store=True),
    }

    def _get_type(self, cr, uid, context):
        purchase_type_obj = self.pool['purchase.type']
        type_id = context.get('type', False)
        if type_id:
            return purchase_type_obj.browse(cr, uid, type_id, context).name
        else:
            return ''

    _defaults = {'type': lambda self, cr, uid, c: self._get_type(cr, uid, c),
                 }
