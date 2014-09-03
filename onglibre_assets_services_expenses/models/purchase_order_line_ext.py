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


class PurchaseOrderLine(orm.Model):
    _inherit = 'purchase.order.line'

    _columns = {
        # Cuenta analítica
        'account_analytic_id':
            fields.many2one('account.analytic.account', 'Analytic Account',
                            required=True),
        # Padre cuenta analuytica
        'parent_account_analytic_id':
            fields.many2one('account.analytic.account',
                            'Parent Analytic Account'),
        # Partida Presupuestaria
        'budgetary_line_id':
            fields.many2one('account.analytic.line', 'Budgetary Line',
                            domain="[('type', '=', 'budgetary'), '|', "
                            "('account_id', '=', account_analytic_id), "
                            "('account_id', '=', parent_account_analytic_id)]",
                            required=True),
        # Fuentes de Financiación
        'line_financing_source_ids':
            fields.one2many('line.financing.source', 'purchase_order_line_id',
                            'Financing Sources'),
    }

    def unlink(self, cr, uid, ids, context=None):
        # Si la linea de pedido de compra, esta asociado a un apunte analitico,
        # borro dicho apunte
        analytic_line_obj = self.pool['account.analytic.line']
        for purchase_line in self.browse(cr, uid, ids, context):
            if purchase_line.order_id.state == 'request':
                cond = [('purchase_order_line_id', '=', purchase_line.id)]
                analytic_line_ids = analytic_line_obj.search(cr, uid, cond,
                                                             context=context)
                if analytic_line_ids:
                    analytic_line_obj.unlink(cr, uid, analytic_line_ids,
                                             context=context)
        # Llamo al metodo super para borrar la linea de pedido de compra
        return super(PurchaseOrderLine, self).unlink(cr, uid, ids,
                                                     context=context)

    # OnChange de la Cuenta Analitica
    def onchange_account(self, cr, uid, ids, account_analytic_id):
        account_obj = self.pool['account.analytic.account']
        financing_obj = self.pool['line.financing.source']
        simulation_cost_obj = self.pool['simulation.cost']
        data = {}
        domain = {}
        result = {}
        if not account_analytic_id:
            data = {'budgetary_line_id': None,
                    'line_financing_source_ids': None,
                    'product_id': None,
                    'product_qty': 1,
                    'name': None,
                    'date_planned': None,
                    'price_unit': None,
                    'taxes_id': None
                    }
        else:
            account = account_obj.browse(cr, uid, account_analytic_id)
            if not account.parent_id:
                data = {'budgetary_line_id': None,
                        'line_financing_source_ids': None,
                        'product_id': None,
                        'product_qty': 1,
                        'name': None,
                        'date_planned': None,
                        'price_unit': None,
                        'taxes_id': None
                        }
            else:
                data = {'parent_account_analytic_id': account.parent_id.id,
                        'budgetary_line_id': None,
                        'line_financing_source_ids': None,
                        'product_id': None,
                        'product_qty': 1,
                        'name': None,
                        'date_planned': None,
                        'price_unit': None,
                        'taxes_id': None
                        }
        if ids:
            for id in ids:
                line = self.browse(cr, uid, id)
                for line_financing in line.line_financing_source_ids:
                    financing_obj.unlink(cr, uid, line_financing.id)
        if account_analytic_id:
            account_analytic_account = account_obj.browse(cr, uid,
                                                          account_analytic_id)
            if account_analytic_account.project_id:
                cond = [('project_id', '=',
                         account_analytic_account.project_id.id)]
                simulation_cost_ids = simulation_cost_obj.search(cr, uid, cond)
                simulation_cost_list = simulation_cost_obj.browse(
                    cr, uid, simulation_cost_ids)
                category_ids = []
                for item in simulation_cost_list:
                    for simulation_category in item.simulation_category_ids:
                        if not simulation_category.restricted_category:
                            simcat = simulation_category
                            category_ids.append(simcat.category_id.id)
                domain = [('purchase_ok', '=', True),
                          ('categ_id', 'in', category_ids),
                          ('categ_id.type', '=', 'normal')]
                result = {'value': data,
                          'domain': {'product_id': domain}}
                if category_ids == []:
                    result.update({'warning': {'title': 'warning',
                                               'message': _('Category list is '
                                                            'empty. Please, '
                                                            'you must revise '
                                                            'expense areas and'
                                                            ' categories '
                                                            'relationship on '
                                                            'Simulation Cost, '
                                                            'or product and '
                                                            'categories '
                                                            'relationship')}})
        return result

    # OnChange del campo Línea Presupuestaria #
    def onchange_budgetary_line(self, cr, uid, ids, account_analytic_id,
                                budgetary_line_id):
        financing_obj = self.pool['line.financing.source']
        analytic_line_obj = self.pool['account.analytic.line']
        category_obj = self.pool['product.category']
        account_obj = self.pool['account.analytic.account']
        simulation_cost_obj = self.pool['simulation.cost']
        data = {}
        domain = {}
        result = {}
        if ids:
            for id in ids:
                line = self.browse(cr, uid, id)
                for line_financing in line.line_financing_source_ids:
                    financing_obj.unlink(cr, uid, line_financing.id)
        if not budgetary_line_id:
            data = {'line_financing_source_ids': None}
            result.update({'value': data})
        else:
            budgetary_line = analytic_line_obj.browse(cr, uid,
                                                      budgetary_line_id)
            cond = [('type', '=', 'financing_source'),
                    ('account_analytic_line_budgetary_id', '=',
                     budgetary_line.id),
                    ('account_id', '=', budgetary_line.account_id.id),
                    ('journal_id', '=', budgetary_line.journal_id.id),
                    ('general_account_id', '=',
                     budgetary_line.general_account_id.id)]
            financers_ids = analytic_line_obj.search(cr, uid, cond)
            list = []
            for financer in analytic_line_obj.browse(cr, uid, financers_ids):
                list.append({'account_analytic_id': account_analytic_id,
                             'budgetary_line_id': budgetary_line_id,
                             'financial_source_line_id': financer.id,
                             'financing_percentage':
                             financer.financing_percentage,
                             'line_financing_percentage':
                             financer.financing_percentage})
            if budgetary_line.account_id:
                category_ids = []
                # Si la linea presupuestaria viene sin producto, busco por
                # expense_area
                if not budgetary_line.product_id:
                    account_analytic_account = account_obj.browse(
                        cr, uid, budgetary_line.account_id.id)
                    cond = [('project_id', '=',
                             account_analytic_account.project_id.id)]
                    simulation_cost_ids = simulation_cost_obj.search(cr, uid,
                                                                     cond)
                    simulation_cost_list = simulation_cost_obj.browse(
                        cr, uid, simulation_cost_ids)
                    for item in simulation_cost_list:
                        simcat_ids = item.simulation_category_ids
                        for simulation_category in simcat_ids:
                            if (simulation_category.expense_area_id.id ==
                                    budgetary_line.expense_area_id.id and
                                    not
                                    simulation_category.restricted_category):
                                simcat = simulation_category
                                category_ids.append(simcat.category_id.id)
                else:
                    # Si la linea presupuestaria viene con producto, y este
                    # tiene una categoria de tipo normal
                    if budgetary_line.product_id.categ_id.type == 'normal':
                        budgetl = budgetary_line
                        category_ids.append(budgetl.product_id.categ_id.id)
                    else:
                        cond = [('parent_id', 'child_of',
                                 [budgetary_line.product_id.categ_id.id])]
                        child_ids = category_obj.search(cr, uid, cond)
                        if child_ids:
                            for child in category_obj.browse(cr, uid,
                                                             child_ids):
                                if child.type == 'normal':
                                    category_ids.append(child.id)

                domain = [('purchase_ok', '=', True),
                          ('categ_id', 'in', category_ids),
                          ('categ_id.type', '=', 'normal')]
                result = {'value': data, 'domain': {'product_id': domain}}
                if category_ids == []:
                    result.update({'warning': {'title': 'warning',
                                               'message': _('Category list is'
                                                            ' empty. Please, '
                                                            'you must revise '
                                                            'expense areas '
                                                            'and categories '
                                                            'relationship on '
                                                            'Simulation Cost,'
                                                            ' or product and '
                                                            'categories '
                                                            'relationship')}})
            data = {'line_financing_source_ids': list,
                    'product_id': None,
                    'product_qty': 1,
                    'name': None,
                    'date_planned': None,
                    'price_unit': None,
                    'taxes_id': None
                    }
            result.update({'value': data})
        return result

    def onchange_product_id_ong(self, cr, uid, ids, pricelist_id, product_id,
                                qty, uom_id, partner_id, date_order=False,
                                fiscal_position_id=False, date_planned=False,
                                name=False, price_unit=False, state='draft',
                                budgetary_line_id=False, context=None):
        cur_obj = self.pool['res.currency']
        tax_obj = self.pool['account.tax']
        pricelist_obj = self.pool['product.pricelist']
        analytic_line_obj = self.pool['account.analytic.line']
        if context is None:
            context = {}
        res = super(PurchaseOrderLine, self).onchange_product_id(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order, fiscal_position_id, date_planned, name, price_unit,
            state, context)
        # Calculo el importe total de la línea
        value = res['value']
        valid = 0
        if value.get('price_unit') and value.get('product_qty'):
            valid = 1
            if value.get('taxes_id'):
                tax_id = value.get('taxes_id')
                tax = tax_obj.browse(cr, uid, tax_id[0], context=context)
                taxes = tax_obj.compute_all(
                    cr, uid, [tax], value.get('price_unit'),
                    value.get('product_qty'))
            else:
                taxes = tax_obj.compute_all(
                    cr, uid, [], value.get('price_unit'),
                    value.get('product_qty'))
            pricelist = pricelist_obj.browse(cr, uid, pricelist_id,
                                             context=context)
            cur = pricelist.currency_id
            total = cur_obj.round(cr, uid, cur, taxes['total'])
            value.update({'price_subtotal': total})
        if valid == 1:
            res.update({'value': value})
            if budgetary_line_id:
                budgetary = analytic_line_obj.browse(
                    cr, uid, budgetary_line_id, context=context)
                if total > budgetary.sum_available_expense:
                    res.update({'warning': {'title': _('Amount Error'),
                                'message': _('The amount of this line, is '
                                             'greater than the available '
                                             'budget line')}
                                })
        return res

    def onchange_price_unit_ong(self, cr, uid, ids, pricelist_id, taxes_id,
                                qty=False, price_unit=False,
                                budgetary_line_id=False, context=None):
        cur_obj = self.pool['res.currency']
        tax_obj = self.pool['account.tax']
        pricelist_obj = self.pool['product.pricelist']
        analytic_line_obj = self.pool['account.analytic.line']
        if context is None:
            context = {}
        res = {}
        if qty and price_unit:
            if not taxes_id:
                taxes = tax_obj.compute_all(cr, uid, [], price_unit, qty)
            else:
                tax_id = 0
                total = 0
                for tax in taxes_id:
                    if tax[2]:
                        my_tax = tax[2]
                        tax_id = my_tax[0]
                if tax_id == 0:
                    taxes = tax_obj.compute_all(cr, uid, [], price_unit, qty)
                else:
                    tax = tax_obj.browse(cr, uid, tax_id, context=context)
                    taxes = tax_obj.compute_all(
                        cr, uid, [tax], price_unit, qty)
            pricelist = pricelist_obj.browse(cr, uid, pricelist_id,
                                             context=context)
            cur = pricelist.currency_id
            total = cur_obj.round(cr, uid, cur, taxes['total'])
            if not budgetary_line_id:
                return {'value': {'price_subtotal': total}}
            else:
                budgetary = analytic_line_obj.browse(
                    cr, uid, budgetary_line_id, context=context)
                if total > budgetary.sum_available_expense:
                    return {'value': {'price_subtotal': total},
                            'warning': {'title': _('Amount Error'),
                                        'message': _('The amount of this line,'
                                                     ' is greater than the '
                                                     'available budget line')
                                        }
                            }
                else:
                    return {'value': {'price_subtotal': total}}
        else:
            return {'value': res}
