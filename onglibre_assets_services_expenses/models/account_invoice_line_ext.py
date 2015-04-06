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
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    # Padre cuenta analytica
    parent_account_analytic_id = fields.Many2one(
        'account.analytic.account', string='Parent Analytic Account')
    # Línea presupuestaria
    budgetary_line_id = fields.Many2one(
        'account.analytic.line', string='Budgetary Line',
        domain="[('type', '=', 'budgetary'), '|', "
        "('account_id', '=', account_analytic_id), "
        "('account_id', '=', parent_account_analytic_id)]")
    # Fuentes de Financiación
    line_financing_source_ids = fields.One2many(
        'line.financing.source', 'account_invoice_line_id',
        string='Financing Sources')

    @api.model
    @api.one
    def unlink(self):
        # Si la linea de factura, esta asociado a un apunte analitico, borro
        # dicho apunte
        analytic_line_obj = self.env['account.analytic.line']
        project_obj = self.env['project.project']
        if self.invoice_id.state == 'draft' and self.account_analytic_id:
            # Calculo importe con iva O sin iva
            cond = [('analytic_account_id', '=', self.account_analytic_id.id)]
            project = project_obj.search(cond, limit=1)
            if project.deductible_iva:
                # busco el iva
                w_taxes = 0
                for taxes in self.invoice_line_tax_id:
                    if taxes.name.find("iva") >= 0:
                        w_taxes = taxes.amount
                    else:
                        if taxes.name.find("IVA") >= 0:
                            w_taxes = taxes.amount
                if w_taxes == 0:
                    w_importe = self.price_subtotal
                else:
                    w_iva = self.price_subtotal * w_taxes
                    w_importe = self.price_subtotal + w_iva
            else:
                w_importe = self.price_subtotal
            cond = [('name', '=', self.invoice_id.origin),
                    ('product_id', '=', self.product_id.id),
                    ('expense_compromised', '=', w_importe)]
            analytic_lines = analytic_line_obj.search(cond)
            if analytic_lines:
                analytic_lines.unlink()
            cond = [('name', '=', self.invoice_id.origin),
                    ('product_id', '=', self.product_id.id),
                    ('updated_expense_budget', '=', w_importe)]
            analytic_lines = analytic_line_obj.search(cond)
            if analytic_lines:
                analytic_lines.unlink()
        # Llamo al metodo super para borrar la linea de factura
        return super(AccountInvoiceLine, self).unlink()

    @api.model
    def unlink2(self, cr, uid, ids, context=None):
        # Si la linea de factura, esta asociado a un apunte analitico, borro
        # dicho apunte
        analytic_line_obj = self.pool['account.analytic.line']
        project_obj = self.pool['project.project']
        for invoice_line in self.browse(cr, uid, ids, context):
            if invoice_line.invoice_id.state == 'draft':
                if invoice_line.account_analytic_id:
                    # Calculo importe con iva O sin iva
                    cond = [('analytic_account_id', '=',
                             invoice_line.account_analytic_id.id)]
                    project_ids = project_obj.search(cr, uid, cond, context)
                    project = project_obj.browse(cr, uid, project_ids[0],
                                                 context)
                    if project.deductible_iva:
                        # busco el iva
                        w_taxes = 0
                        for taxes in invoice_line.invoice_line_tax_id:
                            if taxes.name.find("iva") >= 0:
                                w_taxes = taxes.amount
                            else:
                                if taxes.name.find("IVA") >= 0:
                                    w_taxes = taxes.amount
                        if w_taxes == 0:
                            w_importe = invoice_line.price_subtotal
                        else:
                            w_iva = invoice_line.price_subtotal * w_taxes
                            w_importe = invoice_line.price_subtotal + w_iva
                    else:
                        w_importe = invoice_line.price_subtotal
                    cond = [('name', '=', invoice_line.invoice_id.origin),
                            ('product_id', '=', invoice_line.product_id.id),
                            ('expense_compromised', '=', w_importe)]
                    analytic_line_ids = analytic_line_obj.search(cr, uid, cond,
                                                                 context)
                    if analytic_line_ids:
                        analytic_line_obj.unlink(cr, uid, analytic_line_ids,
                                                 context)
                    cond = [('name', '=', invoice_line.invoice_id.origin),
                            ('product_id', '=', invoice_line.product_id.id),
                            ('updated_expense_budget', '=', w_importe)]
                    analytic_line_ids = analytic_line_obj.search(cr, uid, cond,
                                                                 context)
                    if analytic_line_ids:
                        analytic_line_obj.unlink(cr, uid, analytic_line_ids,
                                                 context)
        # Llamo al metodo super para borrar la linea de factura
        return super(AccountInvoiceLine, self).unlink(cr, uid, ids, context)

    @api.model
    def create(self, vals):
        sale_order_obj = self.env['sale.order']
        line_financing_source_obj = self.env['line.financing.source']
        origin = vals.get('origin')
        product_id = vals.get('product_id')
        name = vals.get('name')
        quantity = vals.get('quantity')
        price_unit = vals.get('price_unit')
        discount = vals.get('discount')
        cond = [('name', '=', origin)]
        sale_order = sale_order_obj.search(cond, limit=1)
        if sale_order:
            list = []
            for sale_line in sale_order.order_line:
                if (sale_line.product_id.id == product_id and sale_line.name
                        == name and sale_line.product_uom_qty == quantity and
                        sale_line.price_unit == price_unit and
                        sale_line.discount == discount):
                    if sale_line.financial_source_line_id:
                        line = {'budgetary_line_id':
                                sale_line.analytic_budgetary_line_id.id,
                                'financial_source_line_id':
                                sale_line.financial_source_line_id.id,
                                'financing_percentage':
                                sale_line.financing_percentage,
                                'line_financing_percentage':
                                sale_line.financing_percentage
                                }
                        new_id = line_financing_source_obj.create(line)
                        list.append(new_id)
                        vals.update({'account_analytic_id':
                                    sale_line.account_analytic_id.id})
                        vals.update({'analytic_budgetary_line_id':
                                    sale_line.analytic_budgetary_line_id.id})
            vals.update({'line_financing_source_ids':
                         [(6, 0, list)]})
        return super(AccountInvoiceLine, self).create(vals)

    @api.model
    def move_line_get_item(self, line):
        financing_line_obj = self.env['line.financing.source']
        res = super(AccountInvoiceLine, self).move_line_get_item(line)
        list = []
        for line_financing in self.line_financing_source_ids:
            vals = {'purchase_order_line_id': False,
                    'account_invoice_line_id': False}
            new_id = financing_line_obj.copy(line_financing.id, vals)
            list.append(new_id)
        res.update({
            'analytic_account_id': line.account_analytic_id.id,
            'account_invoice_line_id': line.id,
            'budgetary_line_id': line.budgetary_line_id.id,
            'line_financing_source_ids': [(6, 0, list)],
            'account_analytic_line_budgetary_id': line.budgetary_line_id.id,
            'account_analytic_line_budgetary_readonly_id':
            line.budgetary_line_id.id})
        return res

    # OnChange de la Cuenta Analitica #
    def onchange_account(self, cr, uid, ids, account_analytic_id):
        financing_obj = self.pool['line.financing.source']
        account_obj = self.pool['account.analytic.account']
        if ids:
            for id in ids:
                line = self.browse(cr, uid, id)
                for line_financing in line.line_financing_source_ids:
                    financing_obj.unlink(cr, uid, line_financing.id)
        if not account_analytic_id:
            data = {'budgetary_line_id': None,
                    'line_financing_source_ids': None
                    }
        else:
            account = account_obj.browse(cr, uid, account_analytic_id)
            if not account.parent_id:
                data = {'budgetary_line_id': None,
                        'line_financing_source_ids': None
                        }
            else:
                data = {'parent_account_analytic_id': account.parent_id.id,
                        'budgetary_line_id': None,
                        'line_financing_source_ids': None
                        }
        return {'value': data}

    # OnChange del campo Línea Presupuestaria #
    def onchange_budgetary_line(self, cr, uid, ids, account_analytic_id,
                                budgetary_line_id):
        data = {}
        domain = {}
        result = {}
        financing_obj = self.pool['line.financing.source']
        analytic_line_obj = self.pool['account.analytic.line']
        account_obj = self.pool['account.analytic.account']
        category_obj = self.pool['product.category']
        simulation_cost_obj = self.pool['simulation.cost']
        if ids:
            for id in ids:
                line = self.browse(cr, uid, id)
                for line_financing in line.line_financing_source_ids:
                    financing_obj.unlink(cr, uid, line_financing.id)
        if not budgetary_line_id:
            data = {'line_financing_source_ids': None
                    }
            result.update({'value': data})
        else:
            budgetary_line = analytic_line_obj.browse(
                cr, uid, budgetary_line_id)
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
                        for simcat in item.simulation_category_ids:
                            if (simcat.expense_area_id.id ==
                                    budgetary_line.expense_area_id.id and
                                    not simcat.restricted_category):
                                category_ids.append(simcat.category_id.id)
                else:
                    # Si la linea presupuestaria viene con producto, y este
                    # tiene una categoria de tipo normal
                    cat_id = budgetary_line.product_id.categ_id.id
                    if budgetary_line.product_id.categ_id.type == 'normal':
                        category_ids.append(cat_id)
                    else:
                        cond = [('parent_id', 'child_of', [cat_id])]
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
                    result.update({'warning': {'title': 'warning', 'message':
                                               'Category list is empty. '
                                               'Please, you must revise '
                                               'expense areas and categories '
                                               'relationship on Simulation '
                                               'Cost, or product and '
                                               'categories relationship'}})
            data = {'line_financing_source_ids': list,
                    'product_id': None,
                    'product_qty': 1,
                    'name': None,
                    'date_planned': None,
                    'price_unit': 0,
                    'taxes_id': None
                    }
            result.update({'value': data})
        return result

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
                 'product_id', 'invoice_id.partner_id',
                 'invoice_id.currency_id', 'budgetary_line_id')
    def _compute_price(self):
        super(AccountInvoiceLine, self)._compute_price()
        if (self.price_subtotal and self.quantity and self.invoice_id and
                self.budgetary_line_id):
            if self.invoice_id.type == 'in_invoice':
                if (self.price_subtotal >
                        self.budgetary_line_id.sum_available_expense):
                    raise Warning(_('Amount Error. The amount of this line, is'
                                    ' greater than the available budget line'))
