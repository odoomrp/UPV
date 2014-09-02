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
from openerp.osv import orm
from openerp.tools.translate import _


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    def _get_financial_source_line_invoice(self, cursor, user, picking,
                                           move_line):
        financing_line_obj = self.pool['line.financing.source']
        list = []
        if picking.purchase_id and move_line.purchase_line_id:
            if move_line.purchase_line_id.line_financing_source_ids:
                lfs_ids = move_line.purchase_line_id.line_financing_source_ids
                for financer in lfs_ids:
                    vals = {'purchase_order_line_id': False}
                    new_id = financing_line_obj.copy(
                        cursor, user, financer.id, vals)
                    list.append(new_id)
        return list

    def _get_budgetary_line_invoice(self, cursor, user, picking, move_line):
        if not move_line.purchase_line_id:
            return False
        if not move_line.purchase_line_id.budgetary_line_id:
            return False
        return move_line.purchase_line_id.budgetary_line_id.id

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line,
                              invoice_id, invoice_vals, context=None):
        res = super(StockPicking, self)._prepare_invoice_line(
            cr, uid, group, picking, move_line, invoice_id, invoice_vals,
            context)
        list = self._get_financial_source_line_invoice(
            cr, uid, picking, move_line)
        res.update({'line_financing_source_ids': [(6, 0, list)]})
        res.update({'budgetary_line_id':
                    self._get_budgetary_line_invoice(cr, uid, picking,
                                                     move_line)})
        return res

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        invoice_line_obj = self.pool['account.invoice.line']
        financing_line_obj = self.pool['line.financing.source']
        list = []
        if move_line.purchase_line_id.line_financing_source_ids:
            lfs_ids = move_line.purchase_line_id.line_financing_source_id
            for financer in lfs_ids:
                vals = {'purchase_order_line_id': False}
                new_id = financing_line_obj.copy(cr, uid, financer.id, vals)
                list.append(new_id)
        if move_line.purchase_line_id.budgetary_line_id:
            vals = {'line_financing_source_ids': [(6, 0, list)],
                    'budgetary_line_id':
                    move_line.purchase_line_id.budgetary_line_id.id}
            invoice_line_obj.write(cr, uid, [invoice_line_id], vals)
        else:
            vals = {'line_financing_source_ids': [(6, 0, list)]}
            invoice_line_obj.write(cr, uid, [invoice_line_id], vals)
        return super(StockPicking, self)._invoice_line_hook(
            cr, uid, move_line, invoice_line_id)

    # FUNCION QUE SE EJECUTA CUANDO CANCELO UN ALBARAN
    def action_cancel(self, cr, uid, ids, context=None):
        if ids:
            for picking in self.browse(cr, uid, ids, context=context):
                if picking.type == 'in':
                    for move_line in picking.move_lines:
                        if move_line.purchase_line_id:
                            purchase_line = move_line.purchase_line_id
                            if purchase_line.line_financing_source_ids:
                                self._action_cancel_financial_source(
                                    cr, uid, move_line, purchase_line,
                                    context=context)
        super(StockPicking, self).action_cancel(cr, uid, ids, context)
        return True

    def _action_cancel_financial_source(self, cr, uid, move_line,
                                        purchase_line, context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        project_obj = self.pool['project.project']
        account_journal_obj = self.pool['account.analytic.journal']
        w_contador = 0
        lfs_ids = move_line.purchase_line_id.line_financing_source_ids
        for line_financing_source in lfs_ids:
            w_contador = w_contador + 1
        w_contador2 = 0
        w_importe2 = 0
        w_importe3 = 0
        for line_financing_source in lfs_ids:
            cond = [('purchase_order_line_id', '=',
                     move_line.purchase_line_id.id),
                    ('line_financing_source_id', '=',
                     line_financing_source.id),
                    ('expense_type', '=', 'purchase_expense')]
            analytic_line_ids = analytic_line_obj.search(cr, uid, cond,
                                                         context=context)
            if analytic_line_ids:
                # Si no existe la linea de analitica es que han dado de alta
                # una linea de pedido estando en estado REQUEST
                # Calculo el campo GENERAL_ACCOUNT_ID, esto esta basado en la
                # funcion on_change_unit_amount, del objeto
                # account_analytic_line
                prod = move_line.purchase_line_id.product_id
                aincome = prod.product_tmpl_id.property_account_income
                cincome = prod.categ_id.property_account_income_categ
                if not aincome and not cincome:
                    name = prod.name
                    raise orm.except_orm(_('Error !'),
                                         _('There is no income account defined'
                                           ' for this product: "%s" (id:%d)') %
                                         (name, purchase_line.product_id.id))
                if aincome:
                    a = aincome
                else:
                    a = cincome
                # Ahora cojo el valor para journal_id, esto esta basado en la
                # funcion on_change_unit_amount, del objeto
                # account_analytic_line
                cond = [('type', '=', 'purchase')]
                j_ids = account_journal_obj.search(cr, uid, cond,
                                                   context=context)
                journal_id = j_ids and j_ids[0] or False
                if not journal_id:
                    raise orm.except_orm(_('Load In Analytical Notes ERROR'),
                                         _('NOT ACCOUNT ANALYTIC JOURNAL '
                                           'FOUND'))
                # Calculo importe con iva O sin iva
                cond = [('analytic_account_id', '=',
                         move_line.purchase_line_id.account_analytic_id.id)]
                project_ids = project_obj.search(cr, uid, cond,
                                                 context=context)
                project = project_obj.browse(cr, uid, project_ids[0],
                                             context=context)
                if not project.deductible_iva:
                    # busco el iva
                    w_taxes = 0
                    for taxes in move_line.purchase_line_id.taxes_id:
                        if taxes.name.find("iva") >= 0:
                            w_taxes = taxes.amount
                        else:
                            if taxes.name.find("IVA") >= 0:
                                w_taxes = taxes.amount
                    if w_taxes == 0:
                        w_importe = move_line.purchase_line_id.price_subtotal
                    else:
                        w_iva = (move_line.purchase_line_id.price_subtotal *
                                 w_taxes)
                        w_importe = (move_line.purchase_line_id.price_subtotal
                                     + w_iva)
                else:
                    w_importe = move_line.purchase_line_id.price_subtotal
                w_importe = ((w_importe /
                              move_line.purchase_line_id.product_qty) *
                             move_line.product_qty)
                w_contador2 = w_contador2 + 1
                if w_contador == w_contador2:
                    w_importe2 = w_importe - w_importe3
                else:
                    perc = line_financing_source.line_financing_percentage
                    w_importe2 = (w_importe * perc) / 100
                    w_importe3 = w_importe3 + w_importe2
                fsl = line_financing_source.financial_source_line_id
                line = {'name': move_line.purchase_line_id.order_id.name,
                        'account_id':
                        move_line.purchase_line_id.account_analytic_id.id,
                        'general_account_id': a,
                        'journal_id': journal_id,
                        'unit_amount': move_line.purchase_line_id.product_qty,
                        'product_id': move_line.purchase_line_id.product_id.id,
                        'product_uom_id':
                        move_line.purchase_line_id.product_uom.id,
                        'sale_amount':  0,
                        'type': 'imputation',
                        'expense_request': (w_importe2 * -1),
                        'expense_area_id': fsl.expense_area_id.id,
                        'account_analytic_line_financing_source_id': fsl.id,
                        'account_analytic_line_budgetary_id':
                        fsl.account_analytic_line_budgetary_id.id,
                        'account_analytic_line_budgetary_readonly_id':
                        fsl.account_analytic_line_budgetary_id.id,
                        'purchase_order_line_id':
                        move_line.purchase_line_id.id,
                        'line_financing_source_id': line_financing_source.id,
                        'expense_type': 'purchase_expense'}
                analytic_line_obj.create(cr, uid, line, context=context)
        w_importe2 = 0
        w_importe3 = 0
        lfs_ids = move_line.purchase_line_id.line_financing_source_ids
        for line_financing_source in lfs_ids:
            cond = [('purchase_order_line_id', '=',
                     move_line.purchase_line_id.id),
                    ('line_financing_source_id', '=',
                     line_financing_source.id),
                    ('expense_type', '=', 'purchase_compromised')]
            analytic_line_ids = analytic_line_obj.search(cr, uid, cond,
                                                         context=context)
            if analytic_line_ids:
                # Si no existe la linea de analitica es que han dado de alta
                # una linea de pedido estando en estado REQUEST Calculo el
                # campo GENERAL_ACCOUNT_ID, esto esta basado en la funcion
                # on_change_unit_amount, del objeto account_analytic_line
                pro = move_line.purchase_line_id.product_id
                aincome = pro.product_tmpl_id.property_account_income
                cincome = pro.categ_id.property_account_income_categ
                if not aincome and not cincome:
                    name = pro.name
                    raise orm.except_orm(_('Error !'),
                                         _('There is no income account defined'
                                           ' for this product: "%s" (id:%d)') %
                                         (name, purchase_line.product_id.id))
                if aincome:
                    a = aincome
                else:
                    a = cincome
                # Ahora cojo el valor para journal_id, esto esta basado en la
                # funcion on_change_unit_amount, del objeto
                # account_analytic_line
                cond = [('type', '=', 'purchase')]
                j_ids = account_journal_obj.search(cr, uid, cond,
                                                   context=context)
                journal_id = j_ids and j_ids[0] or False
                if not journal_id:
                    raise orm.except_orm(_('Load In Analytical Notes ERROR'),
                                         _('NOT ACCOUNT ANALYTIC JOURNAL '
                                           'FOUND'))
                # Calculo importe con iva O sin iva
                cond = [('analytic_account_id', '=',
                         move_line.purchase_line_id.account_analytic_id.id)]
                project_ids = project_obj.search(cr, uid, cond,
                                                 context=context)
                project = project_obj.browse(
                    cr, uid, project_ids[0], context=context)
                if not project.deductible_iva:
                    # busco el iva
                    w_taxes = 0
                    for taxes in move_line.purchase_line_id.taxes_id:
                        if taxes.name.find("iva") >= 0:
                            w_taxes = taxes.amount
                        else:
                            if taxes.name.find("IVA") >= 0:
                                w_taxes = taxes.amount
                    if w_taxes == 0:
                        w_importe = move_line.purchase_line_id.price_subtotal
                    else:
                        w_iva = (move_line.purchase_line_id.price_subtotal *
                                 w_taxes)
                        w_importe = (move_line.purchase_line_id.price_subtotal
                                     + w_iva)
                else:
                    w_importe = move_line.purchase_line_id.price_subtotal
                w_importe = ((w_importe /
                              move_line.purchase_line_id.product_qty) *
                             move_line.product_qty)
                w_contador2 = w_contador2 + 1
                if w_contador == w_contador2:
                    w_importe2 = w_importe - w_importe3
                else:
                    perc = line_financing_source.line_financing_percentage
                    w_importe2 = (w_importe * perc) / 100
                    w_importe3 = w_importe3 + w_importe2
                fsl = line_financing_source.financial_source_line_id
                line = {'name': move_line.purchase_line_id.order_id.name,
                        'account_id':
                        move_line.purchase_line_id.account_analytic_id.id,
                        'general_account_id': a,
                        'journal_id': journal_id,
                        'unit_amount': move_line.purchase_line_id.product_qty,
                        'product_id': move_line.purchase_line_id.product_id.id,
                        'product_uom_id':
                        move_line.purchase_line_id.product_uom.id,
                        'sale_amount':  0,
                        'type': 'imputation',
                        'expense_request': w_importe2,
                        'expense_compromised': (w_importe2 * -1),
                        'expense_area_id': fsl.expense_area_id.id,
                        'account_analytic_line_financing_source_id': fsl.id,
                        'account_analytic_line_budgetary_id':
                        fsl.account_analytic_line_budgetary_id.id,
                        'account_analytic_line_budgetary_readonly_id':
                        fsl.account_analytic_line_budgetary_id.id,
                        'purchase_order_line_id':
                        move_line.purchase_line_id.id,
                        'line_financing_source_id': line_financing_source.id,
                        'expense_type': 'purchase_compromised'}
                analytic_line_obj.create(cr, uid, line, context=context)
        return True
