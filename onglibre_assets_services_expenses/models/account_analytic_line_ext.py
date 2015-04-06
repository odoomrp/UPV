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


class AccountAnalyticLine(orm.Model):
    _inherit = 'account.analytic.line'

    _columns = {
        # Linea de Pedido de compra
        'purchase_order_line_id': fields.many2one('purchase.order.line',
                                                  'Purchase Line'),
        # Linea de Factura
        'account_invoice_line_id': fields.many2one('account.invoice.line',
                                                   'Invoice Line'),
        # Linea de financiacion
        'line_financing_source_id': fields.many2one('line.financing.source',
                                                    'Line Financing Source'),
        # Tipo de gasto
        'expense_type': fields.char('Expense Type', size=64),
    }
