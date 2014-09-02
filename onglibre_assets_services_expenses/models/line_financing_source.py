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


class LineFinancingSource(orm.Model):
    _name = 'line.financing.source'
    _description = 'Line Financing Source'

    _columns = {
        # Linea de Pedido de Compra
        'purchase_order_line_id':
            fields.many2one('purchase.order.line', 'Purchase Order Line',
                            ondelete='cascade'),
        # Linea de Factura de Proveedor
        'account_invoice_line_id':
            fields.many2one('account.invoice.line', 'Account Invoice Line',
                            ondelete='cascade'),
        # Linea de Apunte contable
        'account_move_line_id':
            fields.many2one('account.move.line', 'Account Move Line',
                            ondelete='cascade'),
        # Linea de Extracto Bancario
        'account_bank_statement_line_id':
            fields.many2one('account.bank.statement.line', 'Account Move Line',
                            ondelete='cascade'),
        # Cuenta Analítica
        'account_analytic_id': fields.many2one('account.analytic.account',
                                               'Analytic Account'),
        # Partida Presupuestaria
        'budgetary_line_id':
            fields.many2one('account.analytic.line', 'Budgetary Line',
                            domain="[('type', '=', 'budgetary'), "
                            "('account_id', '=', account_analytic_id)]"),
        # Fuente de Financiación
        'financial_source_line_id':
        fields.many2one('account.analytic.line', 'Financing Source Line',
                        required=True,
                        domain="[('type', '=', 'financing_source'), "
                        "('account_analytic_line_budgetary_id', '=', "
                        "budgetary_line_id)]"),
        # Porcentaje que viene de la Fuente de financiacion
        'financing_percentage': fields.float('Project Financing %',
                                             readonly=True),
        # Porcentaje a aplicar a la linea
        'line_financing_percentage': fields.float('Line Financing %',
                                                  required=True),
    }

    _defaults = {'account_analytic_id': lambda self, cr, uid, context:
                 context.get('account_analytic_id', False),
                 'budgetary_line_id': lambda self, cr, uid, context:
                 context.get('budgetary_line_id', False),
                 'financing_percentage': lambda *a: 100
                 }

    def create(self, cr, uid, vals, context=None):
        account_analytic_line_obj = self.pool['account.analytic.line']
        line_financing_percentage = vals.get('line_financing_percentage')
        if line_financing_percentage > 0:
            financial_source_line_id = vals.get('financial_source_line_id')
            account_analytic_line = account_analytic_line_obj.browse(
                cr, uid, financial_source_line_id, context)
            vals.update({'financing_percentage':
                         account_analytic_line.financing_percentage})
            return super(LineFinancingSource, self).create(cr, uid, vals,
                                                           context)
        else:
            return True

    # Si cambian el pedido, valido que si han cambiado las lineas, también se
    # cambien en analitica
    def write(self, cr, uid, ids, vals, context=None):
        if 'line_financing_percentage' in vals:
            line_financing_percentage = vals.get('line_financing_percentage')
            if line_financing_percentage > 0:
                return super(LineFinancingSource, self).write(
                    cr, uid, ids, vals, context=context)
            else:
                self.unlink(cr, uid, ids, context)
                return True
        else:
            id_modificado = super(LineFinancingSource, self).write(
                cr, uid, ids, vals, context=context)
            return id_modificado

    def onchange_financial_source_line(self, cr, uid, ids,
                                       financial_source_line_id, context=None):
        res = {}
        account_analytic_line_obj = self.pool['account.analytic.line']
        if not financial_source_line_id:
            res.update({'financing_percentage': 0})
        else:
            account_analytic_line = account_analytic_line_obj.browse(
                cr, uid, financial_source_line_id, context=context)
            res.update({'financing_percentage':
                        account_analytic_line.financing_percentage})
        return {'value': res}

    def onchange_line_financing_percentage(self, cr, uid, ids,
                                           line_financing_percentage,
                                           context=None):
        res = {}
        if line_financing_percentage:
            if line_financing_percentage > 100:
                raise orm.except_orm(_('Line Financing Percentage Error'),
                                     _('Line financing percentage > 100'))
        return {'value': res}
