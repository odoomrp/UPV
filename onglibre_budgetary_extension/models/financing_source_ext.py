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
from openerp.addons import decimal_precision as dp


class financing_source(orm.Model):
    _inherit = 'financing.source'

    def _get_account_analytic_lines(self, cr, uid, ids):
        account_analytic_line_obj = self.pool['account.analytic.line']
        account_analytic_line_parent_ids = account_analytic_line_obj.search(
            cr, uid, [('financing_source_id', '=', ids[0])])
        cond = [('account_analytic_line_financing_source_id', 'in',
                 account_analytic_line_parent_ids)]
        return account_analytic_line_obj.search(cr, uid, cond)

    def _calc_limit_expense(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if len(ids) > 1:
            return res
        retult = 0
        for data in self.browse(cr, uid, ids, context=context):
            if data.availability_fund == "granted":
                retult = data.grant
            if data.availability_fund == "accepted":
                retult = data.total_recognized + data.transfered
            if data.availability_fund == "charged":
                retult = data.total_invoices_billed + data.transfered
            res[data.id] = retult
        return res

    def _calc_sum_expense_compromised(self, cr, uid, ids, field_name, arg,
                                      context=None):
        res = {}
        if len(ids) > 1:
            return res
        account_analytic_line_obj = self.pool['account.analytic.line']
        account_analytic_line_ids = self._get_account_analytic_lines(cr, uid,
                                                                     ids)
        for data in self.browse(cr, uid, ids, context=context):
            sum = 0
            for account_analytic in account_analytic_line_obj.browse(
                    cr, uid, account_analytic_line_ids, context=context):
                sum = sum + account_analytic.expense_compromised
            res[data.id] = sum
        return res

    def _calc_sum_expense_compromised_percent(self, cr, uid, ids, field_name,
                                              arg, context=None):
        res = {}
        if len(ids) > 1:
            return res
        for data in self.browse(cr, uid, ids, context=context):
            result = 0
            if data.limit_expense != 0:
                result = (data.sum_expense_compromised / data.limit_expense *
                          100)
            res[data.id] = result
        return res

    def _calc_sum_real_expense(self, cr, uid, ids, field_name, arg,
                               context=None):
        res = {}
        if len(ids) > 1:
            return res
        account_analytic_line_obj = self.pool['account.analytic.line']
        account_analytic_line_ids = self._get_account_analytic_lines(cr, uid,
                                                                     ids)
        for data in self.browse(cr, uid, ids, context=context):
            sum = 0
            for account_analytic in account_analytic_line_obj.browse(
                    cr, uid, account_analytic_line_ids, context=context):
                sum = sum + account_analytic.real_expense
            res[data.id] = sum
        return res

    def _calc_sum_real_expense_percent(self, cr, uid, ids, field_name, arg,
                                       context=None):
        res = {}
        if len(ids) > 1:
            return res
        for data in self.browse(cr, uid, ids, context=context):
            result = 0
            if data.limit_expense != 0:
                result = data.sum_real_expense / data.limit_expense * 100
            res[data.id] = result
        return res

    def _calc_sum_paid_expense(self, cr, uid, ids, field_name, arg,
                               context=None):
        res = {}
        if len(ids) > 1:
            return res
        account_analytic_line_obj = self.pool['account.analytic.line']
        account_analytic_line_ids = self._get_account_analytic_lines(cr, uid,
                                                                     ids)
        for data in self.browse(cr, uid, ids, context=context):
            sum = 0
            for account_analytic in account_analytic_line_obj.browse(
                    cr, uid, account_analytic_line_ids, context=context):
                sum = sum + account_analytic.paid_expense
            res[data.id] = sum
        return res

    def _calc_sum_paid_expense_percent(self, cr, uid, ids, field_name, arg,
                                       context=None):
        res = {}
        if len(ids) > 1:
            return res
        for data in self.browse(cr, uid, ids, context=context):
            result = 0
            if data.sum_real_expense != 0:
                result = data.sum_paid_expense / data.sum_real_expense * 100
            res[data.id] = result
        return res

    def _calc_sum_justified_expense(self, cr, uid, ids, field_name, arg,
                                    context=None):
        res = {}
        if len(ids) > 1:
            return res
        account_analytic_line_obj = self.pool['account.analytic.line']
        account_analytic_line_ids = self._get_account_analytic_lines(cr, uid,
                                                                     ids)
        for data in self.browse(cr, uid, ids, context=context):
            sum = 0
            for account_analytic in account_analytic_line_obj.browse(
                    cr, uid, account_analytic_line_ids, context=context):
                sum = sum + account_analytic.justified_expense
            res[data.id] = sum
        return res

    def _calc_sum_available_expense(self, cr, uid, ids, field_name, arg,
                                    context=None):
        res = {}
        if len(ids) > 1:
            return res
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = (data.limit_expense - data.sum_expense_compromised -
                            data.sum_real_expense)
        return res

    def _calc_sum_available_expense_percent(self, cr, uid, ids, field_name,
                                            arg, context=None):
        res = {}
        if len(ids) > 1:
            return res
        for data in self.browse(cr, uid, ids, context=context):
            result = 0
            if data.limit_expense != 0:
                result = data.sum_available_expense / data.limit_expense * 100
            res[data.id] = result
        return res

    _columns = {
        # Pedidos de Venta asociados a la Fuente de Financiacion
        'sale_order_ids': fields.one2many(
            'sale.order', 'financing_source_id', 'Sale Orders',
            domain=[('simulation_cost_ids', '=', False)]),
        # Líneas de Pedidos de Venta asociados a la Fuente de Financiacion
        'sale_order_line_ids': fields.one2many(
            'sale.order.line', 'financing_source_id', 'Sale Orders Lines',
            domain=[('simulation_cost_line_id', '=', False)]),
        # Facturas de clientes asociados a la Fuente de Financiacion
        'account_invoice_ids': fields.one2many(
            'account.invoice', 'financing_source_id', 'Invoices'),
        # Lineas de Facturas de clientes asociados a la Fuente de Financiacion
        'account_invoice_line_ids': fields.one2many(
            'account.invoice.line', 'financing_source_id', 'Invoice Lines'),
        # Total Reconocido = Sumatorio de Importes de líneas de Pedidos de
        # Venta Confirmados
        'total_recognized': fields.float(
            'Total Recognized', digits_compute=dp.get_precision('Sale Price'),
            readonly=True),
        # Total Facturas Emitidas = Sumatorio de Importes de líneas de Pedidos
        # de Venta Confirmados y Facturados
        'total_invoices_emitted': fields.float(
            'Total Invoices Emitted',
            digits_compute=dp.get_precision('Sale Price'), readonly=True),
        # Total Facturas Cobradas = Sumatorio de Importes de líneas de Pedidos
        # de Venta Confirmados, Facturados y Cobrados
        'total_invoices_billed': fields.float(
            'Total Invoices Billed',
            digits_compute=dp.get_precision('Sale Price'), readonly=True),
        # RD Preliminar = Check que indica si la línea de pedido de venta
        # modifica automáticamente el valor del Concedido sin overheads.
        'rd_preliminary': fields.boolean('RD Preliminary'),
        # Límite de Gastos = campo calculado de acuerdo al “Sistema de
        # disposición de fondos”.
        # Si concedido: Concedido.
        # Si reconocido: Total RD Preliminar + traspasado.
        # Si cobrado: Total Cobrado + traspasado
        'limit_expense': fields.function(
            _calc_limit_expense, method=True, string='Limit Expense',
            type="float", store=False),
        # Comprometido = Sumatorio de Comprometidos de Líneas Analíticas
        'sum_expense_compromised': fields.function(
            _calc_sum_expense_compromised, method=True,
            string='Expense Compromised', type="float", store=False),
        # Comprometido % = sum_expense_compromised / limit_expense * 100
        'sum_expense_compromised_percent': fields.function(
            _calc_sum_expense_compromised_percent, method=True,
            string='Expense Compromised %', type="float", store=False),
        # Real = Sumatorio de Real de Líneas Analíticas
        'sum_real_expense': fields.function(
            _calc_sum_real_expense, method=True, string='Real Expense',
            type="float", store=False),
        # Real % = sum_real_expense / limit_expense * 100
        'sum_real_expense_percent': fields.function(
            _calc_sum_real_expense_percent, method=True,
            string='Real Expense %', type="float", store=False),
        # Pagado = Sumatorio de Pagado de Líneas Analíticas
        'sum_paid_expense': fields.function(
            _calc_sum_paid_expense, method=True, string='Paid Expense',
            type="float", store=False),
        # Pagado % = sum_paid_expense / sum_real_expense * 100
        'sum_paid_expense_percent': fields.function(
            _calc_sum_paid_expense_percent, method=True,
            string='Paid Expense %', type="float", store=False),
        # Justificado = Sumatorio de Justificado de Líneas Analíticas
        'sum_justified_expense': fields.function(
            _calc_sum_justified_expense, method=True,
            string='Justified Expense', type="float", store=False),
        # Disponible = limit_expense - sum_expense_compromised -
        # sum_real_expense
        'sum_available_expense': fields.function(
            _calc_sum_available_expense, method=True,
            string='Available Expense', type="float", store=False),
        # Disponible % = sum_available_expense / limit_expense * 100
        'sum_available_expense_percent': fields.function(
            _calc_sum_available_expense_percent, method=True,
            string='Available Expense %', type="float", store=False),
    }
