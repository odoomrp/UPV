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
from openerp.addons import decimal_precision as dp


class SimulationCostLine(orm.Model):
    _inherit = "simulation.cost.line"

    def _get_margin_percent(self, cr, uid, ids, name, args, context=None):
        res = {}
        for cost_line in self.browse(cr, uid, ids, context):
            if cost_line.estimated_margin:
                res[cost_line.id] = cost_line.estimated_margin * 100
        return res

    def _calc_cost(self, cr, uid, ids, field_name, args, context):
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(['amortization_cost', 'indirect_cost'], 0.0)
        for model in self.browse(cr, uid, ids, context):
            if model.amortization_rate != 0 and model.amount != 0:
                res[model.id]['amortization_cost'] = (model.amortization_rate *
                                                      model.amount)
            if model.indirect_cost_rate and model.amount != 0:
                res[model.id]['indirect_cost'] = (model.indirect_cost_rate *
                                                  model.amount)
        return res

    def _subtotal_sale_ref(self, cr, uid, ids, name, args, context=None):
        res = {}
        for cost_line in self.browse(cr, uid, ids, context):
            if cost_line.sale_price and cost_line.sale_amount:
                res[cost_line.id] = (cost_line.sale_price *
                                     cost_line.sale_amount)
            else:
                res[cost_line.id] = 0
        return res

    _columns = {
        'stage': fields.char('Stage', size=128),
        'sale_amount':
            fields.float('Amount',
                         digits_compute=dp.get_precision('Product UoM')),
        'sale_uom': fields.many2one('product.uom', 'Sale UoM'),
        'margin_percent': fields.float('Margin %', digits=(3, 6)),
        'type_cost':
            fields.selection([('Purchase', 'Purchase'),
                              ('Investment', 'Investment'),
                              ('Subcontracting Services', 'Subcontracting'),
                              ('Task', 'Internal Task'),
                              ('Amortization', 'Amortization I+D'),
                              ('Others', 'Others')],
                             'Type of Cost'),
        'amortization_cost':
            fields.function(_calc_cost, method=True, type='float',
                            string='Amortization Cost', digits=(7, 2),
                            multi='calc', store=True),
        'indirect_cost':
            fields.function(_calc_cost, method=True, type='float',
                            string='Indirect Cost', digits=(7, 2),
                            multi='calc', store=True),
        'subtotal_sale':
            fields.function(_subtotal_sale_ref, method=True, digits=(7, 2),
                            string='Subtotal Sale', store=False),
        # Margen estimado
        'estimated_margin': fields.float('Estimated Margin', digits=(3, 6)),
        # Fondo financiador
        'project_financing_id':
            fields.many2one('project.financing', 'Project Financing'),
        # Estado de la simulacion
        'simulation_cost_state':
            fields.related('simulation_cost_id', 'state', type="selection",
                           selection=[('draft', 'Draft'),
                                      ('financing', 'Financing'),
                                      ('open', 'Open'),
                                      ('inmodif_budgetary',
                                       'In Budgetary Modification'),
                                      ('closed', 'Closed'),
                                      ('accepted', 'Accepted'),
                                      ('canceled', 'Canceled')],
                           string='Simulation Cost State', readonly=True),
        # Proyecto de la simulacion
        'simulation_cost_project_id':
            fields.related('simulation_cost_id', 'project_id', type='many2one',
                           relation='project.project', string='Project1',
                           readonly=True),
        # Iva deducible
        'deductible_iva':
            fields.related('simulation_cost_id', 'deductible_iva',
                           type='boolean', relation='simulation.cost',
                           string='Deductible IVA'),
        # Area de Gasto
        'expense_area_id': fields.many2one('expense.area', 'Expense Area',
                                           required=True),
        # Campo para saber si la linea ya esta financiada
        'financied_line': fields.boolean('Financied Line'),
        # Pedido de venta para el fondo financiador definido
        'sale_order_id':
            fields.related('project_financing_id', 'sale_order_id',
                           type="many2one", relation='sale.order',
                           string="Sale Order"),
        # Importe factura venta
        'amount_untaxed':
            fields.related('sale_order_id', 'amount_untaxed', type='float',
                           string='Untaxed Amount', digits=(12, 2)),
        # Impuestos
        'amount_tax':
            fields.related('sale_order_id', 'amount_tax', type='float',
                           string='Taxes', digits=(12, 2)),
        # Impuestos
        'amount_total':
            fields.related('sale_order_id', 'amount_total', type='float',
                           string='Total', digits=(12, 2)),
        # Grant del fondo financiador
        'project_financing_grant':
            fields.related('project_financing_id', 'grant', type='integer',
                           string='Grant'),
        # Categorias asociadas a la simulacion de coste
        'category_ids':
            fields.many2many('product.category', 'simucostline_category_rel',
                             'simulation_cost_line_id', 'category_id',
                             'Categories'),
        # Categorias asociadas a la simulacion de coste
        'expense_area_ids':
            fields.many2many('expense.area', 'simucostline_expensearea_rel',
                             'simulation_cost_line_id', 'expense_area_id',
                             'Expense Areas'),
    }
    _defaults = {
        'simulation_cost_id': lambda self, cr, uid, context:
            context.get('simulation_cost_id', False),
        'simulation_cost_state': lambda self, cr, uid, context:
            context.get('simulation_cost_state', False),
        'simulation_cost_project_id': lambda self, cr, uid, context:
            context.get('simulation_cost_project_id', False),
        'deductible_iva': lambda self, cr, uid, context:
            context.get('deductible_iva', False),
        'financied_line': lambda *a: False,
        }

    def default_get(self, cr, uid, fields, context=None):
        my_category = []
        my_expense_area = []
        if 'simu_category_ids' in context:
            category_ids = context['simu_category_ids']
            for category in category_ids:
                if category[2]:
                    if not category[2].get('restricted_category'):
                        my_category.append(category[2].get('category_id'))
        if 'simu_expense_area_ids' in context:
            expense_area_ids = context['simu_expense_area_ids']
            for expense_area in expense_area_ids:
                if expense_area[2]:
                    my_expense_area = expense_area[2]
        res = super(SimulationCostLine, self).default_get(cr, uid, fields,
                                                          context=context)
        res.update({'category_ids': my_category,
                    'expense_area_ids': my_expense_area})
        return res

    def create(self, cr, uid, data, context=None):
        simulation_cost_obj = self.pool['simulation.cost']
        project_financing_obj = self.pool['project.financing']
        result = super(SimulationCostLine, self).create(cr, uid, data,
                                                        context)
        line = self.browse(cr, uid, result, context)
        if line.project_financing_id:
            vals = {'simulation_cost_id': False,
                    'simulation_cost_line_id': line.id,
                    'expense_area_id': line.expense_area_id.id,
                    'project_percent': 100}
            project_financing_obj.write(
                cr, uid, [line.project_financing_id.id], vals, context)
        simulation = simulation_cost_obj.browse(
            cr, uid, line.simulation_cost_id.id, context)
        categories = []
        if simulation.simulation_category_ids:
            for category_simu in simulation.simulation_category_ids:
                categories.append(category_simu.id)
        if line.expense_area_id.category_ids:
            for category in line.expense_area_id.category_ids:
                if category.id not in categories:
                    categories.append(category.id)
        vals = {'category_ids': [(6, 0, categories)]}
        simulation_cost_obj.write(cr, uid, simulation.id, vals, context)
        return result

    def write(self, cr, uid, ids, vals, context=None):
        simulation_cost_obj = self.pool['simulation.cost']
        project_financing_obj = self.pool['project.financing']
        result = super(SimulationCostLine, self).write(cr, uid, ids, vals,
                                                       context)
        if ids:
            if not isinstance(ids, list):
                ids = [ids]
            for line in self.browse(cr, uid, ids, context):
                if line.project_financing_id:
                    my_vals = {'simulation_cost_id': False,
                               'simulation_cost_line_id': line.id,
                               'expense_area_id': line.expense_area_id.id,
                               'project_percent': 100}
                    project_financing_obj.write(
                        cr, uid, [line.project_financing_id.id], my_vals,
                        context)
                simulation = simulation_cost_obj.browse(
                    cr, uid, line.simulation_cost_id.id, context)
                categories = []
                if simulation.simulation_category_ids:
                    for category_simu in simulation.simulation_category_ids:
                        categories.append(category_simu.id)
                if line.expense_area_id.category_ids:
                    for category in line.expense_area_id.category_ids:
                        if category.id not in categories:
                            categories.append(category.id)
                            my_vals = {'category_ids': [(6, 0, categories)]}
                simulation_cost_obj.write(
                    cr, uid, simulation.id, my_vals, context)
        return result

    def unlink(self, cr, uid, ids, context=None):
        project_financing_obj = self.pool['project.financing']
        analytic_simuline_obj = self.pool['account.analytic.simulation.line']
        analytic_line_obj = self.pool['account.analytic.line']
        for line in self.browse(cr, uid, ids, context):
            if line.sale_order_line_id:
                raise orm.except_orm(_('Line Delete Error'),
                                     _('The line is associated with the sale'
                                       ' order: %s, in line with product:'
                                       ' %s') %
                                     (line.sale_order_line_id.order_id.name,
                                      line.sale_order_line_id.product_id.name))
            else:
                cond = [('simulation_cost_id', '=',
                         line.simulation_cost_id.id),
                        ('simulation_cost_line_id', '=', line.id),
                        ('expense_area_id', '=', line.expense_area_id.id)]
                analytic_simuline_ids = analytic_simuline_obj.search(
                    cr, uid, cond, context=context)
                if analytic_simuline_ids:
                    simulation_analytic_line = analytic_simuline_obj.browse(
                        cr, uid, analytic_simuline_ids[0], context)
                    analytic_line = analytic_line_obj.browse(
                        cr, uid,
                        simulation_analytic_line.account_analytic_line_id.id,
                        context)
                    raise orm.except_orm(_('Line Delete Error'),
                                         _('The line is associated with '
                                           ' analytic line: %s, type: %s') %
                                         (analytic_line.name,
                                          str(analytic_line.type)))
                else:
                    if line.project_financing_id:
                        project_financing_obj.unlink(
                            cr, uid, line.project_financing_id.id, context)
        # Llamo al metodo super
        return super(SimulationCostLine, self).unlink(cr, uid, ids)

    def onchange_rates(self, cr, uid, ids, type_cost, amortization_rate,
                       indirect_rate, purchase_price, amount,
                       subtotal_purchase, sale_price, subtotal_sale,
                       estimated_margin, benefit, purchase_insale,
                       context=None):
        if ids:
            for simulation_cost_line in self.browse(cr, uid, ids, context):
                if simulation_cost_line.sale_order_line_id.id:
                    return {'value': {'amortization_rate':
                                      simulation_cost_line.amortization_rate,
                                      'indirect_cost_rate':
                                      simulation_cost_line.indirect_cost_rate},
                            'warning': {'title': _('Rates Error'),
                                        'message': _('You can not modify the '
                                                     'rates, this line belongs'
                                                     ' to a line of sale '
                                                     'order'),
                                        }
                            }
        res = self.onchange_purchase_price_amount(
            cr, uid, ids, type_cost, amortization_rate, indirect_rate,
            purchase_price, amount, subtotal_purchase, sale_price,
            subtotal_sale, estimated_margin, benefit, purchase_insale,
            context)['value']
        res.update({'amortization_cost': amount * amortization_rate,
                    'indirect_cost': amount * indirect_rate
                    })
        return {'value': res}

    def onchange_product(self, cr, uid, ids, simulation_cost_id, product_id,
                         type, amount, sale_amount, subtotal_purchase,
                         estimated_date_purchase_completion, sale_subtotal,
                         context=None):
        print '*** ESTOY EN ONCHANGE_PRODUCT, simulation_cost_id: ' + str(simulation_cost_id)
        simulation_cost_obj = self.pool['simulation.cost']
        product_obj = self.pool['product.product']
        supplierinfo_obj = self.pool['product.supplierinfo']
        partner_obj = self.pool['res.partner']
        for simulation_cost_line in self.browse(cr, uid, ids, context):
            if simulation_cost_line.sale_order_line_id.id:
                return {'value': {'product_id':
                                  simulation_cost_line.product_id.id},
                        'warning': {'title': _('Product Error'),
                                    'message': _('You can not modify the '
                                                 'product, this line belongs '
                                                 'to a line of sale order')
                                    }
                        }
        res = {}
        estimated_margin = 0
        if not amount:
            amount = 1.0
        if product_id:
            if type:
                product = product_obj.browse(cr, uid, product_id, context)
#                if not simulation_cost_id:
#                    raise orm.except_orm(_('Error'),
#                                         _('You should save before the '
#                                           'simulation'))
#                simulation = simulation_cost_obj.browse(
#                    cr, uid, simulation_cost_id, context)
#                if simulation.simulation_category_ids:
#                    found = 0
#                    for category in simulation.simulation_category_ids:
#                        if category.category_id.id == product.categ_id.id:
#                            found = 1
#                    if found == 0:
#                        raise orm.except_orm(_('Product Error'),
#                                             _('Product with category '
#                                               'restricted'))
                if type == 'Amortization':
                    if not product.purchase_ok:
                        raise orm.except_orm(_('Product Error'),
                                             _('Product must be kind to buy'))
                    else:
                        if (product.type != 'product' and
                                product.type != 'consu'):
                            raise orm.except_orm(_('Product Error'),
                                                 _('Product must be product or'
                                                   ' consumable'))
                # COJO EL PRIMER PROVEEDOR PARA EL PRODUCTO
                cond = [('product_tmpl_id', '=', product.product_tmpl_id.id)]
                supplierinfo_ids = supplierinfo_obj.search(
                    cr, uid, cond, context, order='sequence')
                if supplierinfo_ids:
                    supplierinfo_id = supplierinfo_obj.browse(
                        cr, uid, supplierinfo_ids[0], context)
                    lang = partner_obj.browse(
                        cr, uid, supplierinfo_id.name.id, context).lang
                    # Accedo a datos del producto.
                    context_partner = {'lang': lang,
                                       'partner_id': supplierinfo_id.name.id}
                    product = product_obj.browse(
                        cr, uid, product_id, context=context_partner)
                    # Si no tiene fecha de realización, le pongo la fecha del
                    # sistema
                    if not estimated_date_purchase_completion:
                        fd = fields.date
                        estimated_date_purchase_completion = fd.context_today
                    # Cojo el precio de compra según tablas.
                    price = 0
                    for pricelist in supplierinfo_id.pricelist_ids:
                        if (pricelist.min_quantity < amount or
                                pricelist.min_quantity == amount):
                            price = pricelist.price
                    if price == 0:
                        price = product.standard_price
                    # Calculo el total compra
                    subtotal_purchase = amount * price
                    amortization_cost = 0.0
                    indirect_cost = 0.0
                    # Miro si tengo que calcular la amortizacion y los costes
                    # indirectos
                    if type == 'Others':
                        # Calculo la amortizacion
                        amortization_cost = 0.0
                        if product.amortization_rate:
                            amortization_cost = (amount *
                                                 product.amortization_rate)
                        # Calculo los costes indirectos
                        indirect_cost = 0.0
                        if product.indirect_cost_rate:
                            indirect_cost = amount * product.indirect_cost_rate
                    benefit = (sale_subtotal - subtotal_purchase -
                               amortization_cost - indirect_cost)
                    if type == 'Others':
                        # Si es una linea que viene de la pestaña TASK
                        # (Internal task) cargo datos con proveedor
                        res = {'name': (product.name or ''),
                               'description': (product.description or ''),
                               'purchase_price': price,
                               'uom_id': product.uom_id.id,
                               'amount': amount,
                               'supplier_id': supplierinfo_id.name.id,
                               'subtotal_purchase': subtotal_purchase,
                               'amortization_rate': product.amortization_rate,
                               'amortization_cost': amortization_cost,
                               'indirect_cost_rate':
                               product.indirect_cost_rate,
                               'indirect_cost': indirect_cost,
                               'benefit': benefit
                               }
                    else:
                        res = {'name': (product.name or ''),
                               'description': (product.description or ''),
                               'purchase_price': price,
                               'uom_id': product.uom_id.id,
                               'amount': amount,
                               'supplier_id': supplierinfo_id.name.id,
                               'subtotal_purchase': subtotal_purchase,
                               'amortization_rate': 0,
                               'amortization_cost': 0,
                               'indirect_cost_rate': 0,
                               'indirect_cost': 0,
                               'benefit': benefit,
                               }
                else:
                    if product.standard_price:
                        subtotal_purchase = amount * product.standard_price
                    else:
                        subtotal_purchase = 0
                    amortization_cost = 0.0
                    indirect_cost = 0.0
                    if type == 'Others':
                        # Calculo la amortizacion
                        amortization_cost = 0.0
                        if product.amortization_rate:
                            amortization_cost = (amount *
                                                 product.amortization_rate)
                        # Calculo los costes indirectos
                        indirect_cost = 0.0
                        if product.indirect_cost_rate:
                                indirect_cost = (amount *
                                                 product.indirect_cost_rate)
                        benefit = (sale_subtotal - subtotal_purchase -
                                   amortization_cost - indirect_cost)
                        res = {'name': (product.name or ''),
                               'description': (product.description or ''),
                               'purchase_price':
                               (product.standard_price or ''),
                               'uom_id': product.uom_id.id,
                               'amount': amount,
                               'supplier_id': None,
                               'subtotal_purchase': subtotal_purchase,
                               'amortization_rate': product.amortization_rate,
                               'amortization_cost': amortization_cost,
                               'indirect_cost_rate':
                               product.indirect_cost_rate,
                               'indirect_cost': indirect_cost,
                               'benefit': benefit,
                               }
                    else:
                        benefit = (sale_subtotal - subtotal_purchase -
                                   amortization_cost - indirect_cost)
                        res = {'name': (product.name or ''),
                               'description': (product.description or ''),
                               'purchase_price':
                               (product.standard_price or ''),
                               'uom_id': product.uom_id.id,
                               'amount': amount,
                               'supplier_id': None,
                               'subtotal_purchase': subtotal_purchase,
                               'amortization_rate': 0,
                               'amortization_cost': 0,
                               'indirect_cost_rate': 0,
                               'indirect_cost': 0,
                               'benefit': benefit,
                               }
            if not sale_amount:
                sale_amount = amount
            res.update({'sale_amount': sale_amount,
                        'product_sale_id': product_id,
                        'sale_price': product.list_price,
                        'subtotal_sale': product.list_price * sale_amount})
            cost = (res['subtotal_purchase'] + res['amortization_cost'] +
                    res['indirect_cost'])
            benefit = res['subtotal_sale'] - cost
            if cost > 0:
                estimated_margin = (res['subtotal_sale'] / cost) - 1
            else:
                estimated_margin = 0
            margin_percent = estimated_margin * 100
            res.update({'benefit': benefit,
                        'estimated_margin': estimated_margin,
                        'margin_percent': margin_percent})
        return {'value': res}

    def onchange_supplier(self, cr, uid, ids, supplier_id, type_cost,
                          product_id, amount, sale_amount, uom_id,
                          estimated_date_purchase_completion,
                          subtotal_purchase, sale_price, subtotal_sale,
                          estimated_margin, benefit, context=None):
        partner_obj = self.pool['res.partner']
        product_obj = self.pool['product.product']
        pricelist_obj = self.pool['product.pricelist']
        for simulation_cost_line in self.browse(cr, uid, ids, context):
            if simulation_cost_line.sale_order_line_id.id:
                return {'value': {'supplier_id':
                                  simulation_cost_line.supplier_id.id},
                        'warning': {'title': _('Supplier Error'),
                                    'message': _('You can not modify the '
                                                 'supplier, this line belongs'
                                                 ' to a line of sale order')
                                    }
                        }
        res = {}
        estimated_margin = 0
        if not amount:
            amount = 1.0
        if not sale_amount:
            sale_amount = amount
        if supplier_id:
            if not product_id:
                raise orm.except_orm(_('Supplier Error'),
                                     _('You must select a product'))
            else:
                # Accedo a datos del proveedor
                supplier = partner_obj.browse(cr, uid, supplier_id, context)
                lang = partner_obj.browse(cr, uid, supplier_id, context).lang
                pricelist_id = supplier.property_product_pricelist_purchase.id
                # Accedo a datos del producto.
                context_partner = {'lang': lang, 'partner_id': supplier_id}
                product = product_obj.browse(cr, uid, product_id,
                                             context=context_partner)
                # Si no tiene fecha de realización, le pongo la fecha del
                # sistema
                if not estimated_date_purchase_completion:
                    fd = fields.date
                    estimated_date_purchase_completion = fd.context_today
                # Cojo el precio de compra según tablas.
                price = pricelist_obj.price_get(
                    cr, uid, [pricelist_id], product.id, amount, supplier_id,
                    {'uom': uom_id, 'date':
                     estimated_date_purchase_completion})[pricelist_id]
                # Calculo el total compra
                subtotal_purchase = amount * price
                # Calculo el total venta
                if sale_price > 0:
                    subtotal_sale = sale_amount * sale_price
                else:
                    subtotal_sale = 0
                # Calculo el margen estimado
                if price > 0 and sale_price > 0:
                    estimated_margin = (sale_price / price) - 1
                else:
                    estimated_margin = 0
                # Calculo el beneficio
                benefit = subtotal_sale - subtotal_purchase
                # Miro si tengo que calcular la amortizacion y los costes
                # indirectos
                if type_cost == 'Others':
                    # Calculo la amortizacion
                    amortization_cost = 0.0
                    if product.amortization_rate:
                        amortization_cost = amount * product.amortization_rate
                    # Calculo los costes indirectos
                    indirect_cost = 0.0
                    if product.indirect_cost_rate:
                        indirect_cost = amount * product.indirect_cost_rate
                    # Cargo campos de pantalla
                    benefit = (subtotal_sale - subtotal_purchase -
                               amortization_cost - indirect_cost)
                    res.update({'purchase_price': price,
                                'amount': amount,
                                'estimated_date_purchase_completion':
                                estimated_date_purchase_completion,
                                'subtotal_purchase': subtotal_purchase,
                                'subtotal_sale': subtotal_sale,
                                'estimated_margin': estimated_margin,
                                'benefit': benefit,
                                'estimated_date_purchase_completion':
                                estimated_date_purchase_completion,
                                'amortization_rate': product.amortization_rate,
                                'amortization_cost': amortization_cost,
                                'indirect_cost_rate':
                                product.indirect_cost_rate,
                                'indirect_cost': indirect_cost,
                                })
                else:
                    # Cargo campos de pantalla
                    res.update({'purchase_price': price,
                                'amount': amount,
                                'estimated_date_purchase_completion':
                                estimated_date_purchase_completion,
                                'subtotal_purchase': subtotal_purchase,
                                'subtotal_sale': subtotal_sale,
                                'estimated_margin': estimated_margin,
                                'benefit': benefit,
                                'estimated_date_purchase_completion':
                                estimated_date_purchase_completion,
                                'amortization_rate': 0,
                                'amortization_cost': 0,
                                'indirect_cost_rate': 0,
                                'indirect_cost': 0,
                                })
            cost = (res['subtotal_purchase'] + res['amortization_cost'] +
                    res['indirect_cost'])
            benefit = res['subtotal_sale'] - cost
            estimated_margin = 0.0
            if cost:
                estimated_margin = (res['subtotal_sale'] / cost) - 1
            margin_percent = estimated_margin * 100
            res.update({'margin_percent': margin_percent,
                        'estimated_margin': estimated_margin,
                        'benefit': benefit,
                        'sale_amount': sale_amount})
        return {'value': res}

    def onchange_purchase_price_amount(self, cr, uid, ids, type_cost,
                                       amortization_rate, indirect_cost_rate,
                                       purchase_price, amount, sale_amount,
                                       subtotal_purchase, sale_price,
                                       subtotal_sale, estimated_margin,
                                       benefit, purchase_insale, context=None):
        for simulation_cost_line in self.browse(cr, uid, ids, context):
            if simulation_cost_line.sale_order_line_id.id:
                return {'value': {'purchase_price':
                                  simulation_cost_line.purchase_price,
                                  'amount': simulation_cost_line.amount},
                        'warning': {'title': _('Price/Amount Error'),
                                    'message': _('You can not modify the '
                                                 'price/amount, this line '
                                                 'belongs to a line of '
                                                 'sale order')
                                    }
                        }
        res = {}
        estimated_margin = 0
        if not amount:
            amount = 0
        if not sale_amount:
            sale_amount = 0
        # Calculo el total de la compra
        if purchase_price > 0 and amount > 0:
            subtotal_purchase = amount * purchase_price
        else:
            subtotal_purchase = 0
        # Si hay que copiar la información del producto de compra, en la
        # información del producto de venta
        if purchase_insale:
            sale_price = purchase_price
            sale_amount = amount
        # Calculo el total de la venta
        if sale_price > 0 and sale_amount > 0:
            subtotal_sale = sale_amount * sale_price
        else:
            subtotal_sale = 0
        # Calculo el margen estimado
        if sale_price > 0 and purchase_price > 0:
            if amount > 0:
                estimated_margin = ((subtotal_sale /
                                     ((purchase_price * amount) +
                                      (amortization_rate * amount) +
                                      (indirect_cost_rate * amount))) - 1)
            else:
                estimated_margin = 0
        else:
            estimated_margin = 0
        # Calculo el beneficio
        benefit = subtotal_sale - subtotal_purchase
        # Calculo la amortizacion y los costes indirectos
        if type_cost == 'Others':
            # Calculo la amortizacion
            amortization_cost = 0.0
            if amortization_rate:
                amortization_cost = amount * amortization_rate
            # Calculo los costes indirectos
            indirect_cost = 0.0
            if indirect_cost_rate:
                indirect_cost = amount * indirect_cost_rate
            # Cargo campos de pantalla
            benefit = (subtotal_sale - subtotal_purchase - amortization_cost -
                       indirect_cost)
            margin_percent = estimated_margin * 100
            res.update({'subtotal_purchase': subtotal_purchase,
                        'estimated_margin': estimated_margin,
                        'subtotal_sale': subtotal_sale,
                        'benefit': benefit,
                        'amortization_cost': amortization_cost,
                        'indirect_cost': indirect_cost,
                        'amount': amount,
                        'sale_amount': sale_amount,
                        'margin_percent': margin_percent,
                        'sale_price': sale_price,
                        'sale_amount': sale_amount
                        })
        else:
            # Cargo campos de pantalla
            res.update({'subtotal_purchase': subtotal_purchase,
                        'estimated_margin': estimated_margin,
                        'subtotal_sale': subtotal_sale,
                        'benefit': benefit,
                        'amortization_rate': 0,
                        'amortization_cost': 0,
                        'indirect_cost_rate': 0,
                        'indirect_cost': 0,
                        'amount': amount,
                        'sale_amount': sale_amount,
                        'sale_price': sale_price
                        })
            cost = (res['subtotal_purchase'] + res['amortization_cost'] +
                    res['indirect_cost'])
            benefit = res['subtotal_sale'] - cost
            estimated_margin = 0.0
            if cost != 0:
                estimated_margin = (res['subtotal_sale'] / cost) - 1
            margin_percent = estimated_margin * 100
            res.update({'margin_percent': margin_percent,
                        'estimated_margin': estimated_margin,
                        'benefit': benefit,
                        'sale_amount': sale_amount})
        return {'value': res}

    def onchange_type_cost(self, cr, uid, ids, type, context=None):
        res = {'product_id': '',
               'name': '',
               'description': '',
               'uom_id': '',
               'supplier_id': '',
               'purchase_price': 0,
               'amount': 0,
               'subtotal_purchase': 0,
               'product_sale_id': '',
               'sale_price': 0,
               'estimated_margin': 0,
               'subtotal_sale': 0,
               'benefit': 0,
               'amortization_rate': 0,
               'amortization_cost': 0,
               'indirect_cost_rate': 0,
               'indirect_cost': 0
               }
        return {'value': res}

    def onchange_sale_product(self, cr, uid, ids, product_sale_id, product_id,
                              purchase_price, amount, sale_amount,
                              subtotal_sale, estimated_margin,
                              subtotal_purchase, benefit, amortization_cost,
                              indirect_cost, context=None):
        product_obj = self.pool['product.product']
        for simulation_cost_line in self.browse(cr, uid, ids, context):
            if simulation_cost_line.sale_order_line_id.id:
                return {'value': {'product_sale_id':
                                  simulation_cost_line.product_sale_id.id},
                        'warning': {'title': _('Sale Product Error'),
                                    'message': _('You can not modify the sale '
                                                 'product, this line belongs '
                                                 'to a line of sale order')
                                    }
                        }
        res = {}
        estimated_margin = 0
        if not amount:
            amount = 0
        if not sale_amount:
            sale_amount = 0
        if product_sale_id and product_id:
            product = product_obj.browse(cr, uid, product_sale_id, context)
            if product_sale_id != product_id:
                if not product.sale_ok:
                    raise orm.except_orm(_('Sale Product Error'),
                                         _('Product must be to sale OR the '
                                           'same product of purchase'))
            # Calculo el total de la venta
            if product.list_price > 0 and sale_amount > 0:
                subtotal_sale = sale_amount * product.list_price
            else:
                subtotal_sale = 0
            # Calculo el margen estimado
            if purchase_price > 0 and product.standard_price > 0:
                estimated_margin = (product.list_price/purchase_price)-1
            else:
                estimated_margin = 0
            # Calculo el beneficio
            benefit = (subtotal_sale - subtotal_purchase - amortization_cost -
                       indirect_cost)
            # Cargo campos de pantalla
            cost = subtotal_purchase + amortization_cost + indirect_cost
            benefit = subtotal_sale - cost
            if cost != 0:
                estimated_margin = (subtotal_sale / cost) - 1
            else:
                estimated_margin = 0
            margin_percent = estimated_margin * 100
            res.update({'sale_price': product.list_price or '',
                        'estimated_margin': estimated_margin,
                        'margin_percent': margin_percent,
                        'subtotal_sale': subtotal_sale,
                        'benefit': benefit,
                        'amount': amount,
                        'sale_amount': sale_amount
                        })
        return {'value': res}

    def onchange_sale_amount(self, cr, uid, ids, purchase_price, amount,
                             sale_price, sale_amount, subtotal_sale,
                             estimated_margin, subtotal_purchase, benefit,
                             amortization_cost, indirect_cost, context=None):
        for simulation_cost_line in self.browse(cr, uid, ids, context):
            if simulation_cost_line.sale_order_line_id.id:
                return {'value': {'sale_amount':
                                  simulation_cost_line.sale_amount},
                        'warning': {'title': _('Sale Amount Error'),
                                    'message': _('You can not modify the sale'
                                                 ' amount, this line belongs '
                                                 'to a line of sale order')
                                    }
                        }
        res = {}
        estimated_margin = 0
        if not amount:
            amount = 0
        if not sale_amount:
            sale_amount = 0
        if sale_price > 0 and sale_amount > 0:
            subtotal_sale = sale_price * sale_amount
        else:
            subtotal_sale = 0
        if purchase_price > 0 and sale_price > 0:
            estimated_margin = (sale_price/purchase_price)-1
        else:
            estimated_margin = 0
        benefit = (subtotal_sale - subtotal_purchase - amortization_cost -
                   indirect_cost)
        cost = subtotal_purchase + amortization_cost + indirect_cost
        benefit = subtotal_sale - cost
        if subtotal_sale > 0 and cost > 0:
            estimated_margin = (subtotal_sale / cost) - 1
        else:
            estimated_margin = 0
        margin_percent = estimated_margin * 100
        res.update({'estimated_margin': estimated_margin,
                    'margin_percent': margin_percent,
                    'subtotal_sale': subtotal_sale,
                    'benefit': benefit
                    })
        return {'value': res}

    def onchange_sale_price(self, cr, uid, ids, purchase_price, amount,
                            sale_amount, sale_price, subtotal_sale,
                            estimated_margin, subtotal_purchase, benefit,
                            amortization_cost, indirect_cost, context=None):
        for simulation_cost_line in self.browse(cr, uid, ids, context):
            if simulation_cost_line.sale_order_line_id.id:
                return {'value': {'sale_price':
                                  simulation_cost_line.sale_price},
                        'warning': {'title': _('Sale Price Error'),
                                    'message': _('You can not modify the sale'
                                                 ' price, this line belongs to'
                                                 ' a line of sale order')
                                    }
                        }
        estimated_margin = 0
        res = {}
        if not amount:
            amount = 1.0
        if not sale_amount:
            sale_amount = amount
        # Calculo el total de la venta
        if sale_price > 0 and sale_amount > 0:
            subtotal_sale = sale_amount * sale_price
        else:
            subtotal_sale = 0
        # Calculo el margen estimado
        if purchase_price > 0 and sale_price > 0:
            if (subtotal_purchase > 0 or amortization_cost > 0 or
                    indirect_cost > 0):
                estimated_margin = ((subtotal_sale /
                                     (subtotal_purchase + amortization_cost +
                                      indirect_cost))-1)
            else:
                estimated_margin = 0
        else:
            estimated_margin = 0
        # Calculo el beneficio
        benefit = (subtotal_sale - subtotal_purchase - amortization_cost -
                   indirect_cost)
        # Cargo campos de pantalla
        margin_percent = estimated_margin * 100
        res.update({'estimated_margin': estimated_margin,
                    'margin_percent': margin_percent,
                    'subtotal_sale': subtotal_sale,
                    'benefit': benefit,
                    'sale_price': sale_price
                    })
        return {'value': res}

    def onchange_margin_percent(self, cr, uid, ids, margin_percent,
                                estimated_margin, purchase_price, sale_price,
                                amount, sale_amount, subtotal_sale,
                                subtotal_purchase, benefit, amortization_cost,
                                indirect_cost, context=None):
        for simulation_cost_line in self.browse(cr, uid, ids, context):
            if simulation_cost_line.sale_order_line_id.id:
                return {'value': {'margin_percent':
                                  simulation_cost_line.margin_percent},
                        'warning': {'title': _('Margin Percent Error'),
                                    'message': _('You can not modify the '
                                                 'margin percent, this line '
                                                 'belongs to a line of sale '
                                                 'order')
                                    }
                        }
        res = {}
        if margin_percent:
            estimated = margin_percent / 100
            estimated_margin = estimated
        else:
            estimated = 0
            estimated_margin = 0
        res = self.onchange_estimated_margin(
            cr, uid, ids, estimated_margin, purchase_price, sale_price, amount,
            sale_amount, subtotal_sale, subtotal_purchase, benefit,
            amortization_cost, indirect_cost, context)['value']
        res.update({'estimated_margin': estimated})
        return {'value': res}

    def onchange_estimated_margin(self, cr, uid, ids, estimated_margin,
                                  purchase_price, sale_price, amount,
                                  sale_amount, subtotal_sale,
                                  subtotal_purchase, benefit,
                                  amortization_cost, indirect_cost,
                                  context=None):
        for simulation_cost_line in self.browse(cr, uid, ids, context):
            if simulation_cost_line.sale_order_line_id.id:
                return {'value': {'estimated_margin':
                                  simulation_cost_line.estimated_margin},
                        'warning': {'title': _('Estimated Margin Error'),
                                    'message': _('You can not modify the '
                                                 'estimated margin, this line '
                                                 'belongs to a line of sale '
                                                 'order')
                                    }
                        }
        res = {}
        if estimated_margin:
            if estimated_margin > 0:
                # Calculo el precio de venta
                if purchase_price > 0 and estimated_margin > 0:
                    sale_price = (((1 + estimated_margin) *
                                   (subtotal_purchase + amortization_cost +
                                    indirect_cost)) / sale_amount)
                else:
                    sale_price = 0
                # Calculo el total de la venta
                if sale_price > 0 and sale_amount > 0:
                    subtotal_sale = sale_amount * sale_price
                else:
                    subtotal_sale = 0
                # Calculo el beneficio
                benefit = (subtotal_sale - subtotal_purchase -
                           amortization_cost - indirect_cost)
            else:
                if purchase_price > 0 and amount > 0:
                    if sale_amount > 0:
                        sale_price = (((1 + estimated_margin) *
                                       (subtotal_purchase + amortization_cost +
                                        indirect_cost)) / sale_amount)
                        subtotal_sale = sale_price * sale_amount
                        benefit = 0
                    else:
                        subtotal_sale = 0
                        benefit = purchase_price * amount
                else:
                    sale_price = 0
                    subtotal_sale = 0
                    benefit = 0
        else:
            if purchase_price > 0 and amount > 0:
                if sale_amount > 0:
                    sale_price = (((1 + estimated_margin) *
                                   (subtotal_purchase + amortization_cost +
                                    indirect_cost)) / sale_amount)
                    subtotal_sale = sale_price * sale_amount
                    benefit = 0
                else:
                    subtotal_sale = 0
                    benefit = purchase_price * amount
            else:
                sale_price = 0
                subtotal_sale = 0
                benefit = 0
        # Cargo campos de pantalla
        res.update({'sale_price': sale_price,
                    'subtotal_sale': subtotal_sale,
                    'benefit': benefit
                    })
        return {'value': res}

    def onchange_project_financing_id(self, cr, uid, ids, project_financing_id,
                                      context=None):
        for simu_line in self.browse(cr, uid, ids, context):
            if simu_line.sale_order_line_id.id:
                return {'value': {'project_financing_id':
                                  simu_line.project_financing_id.id},
                        'warning': {'title': _('Project Financing Error'),
                                    'message': _('You can not modify the '
                                                 'project financing, this line'
                                                 ' belongs to a line of sale '
                                                 'order')
                                    }
                        }
        res = {}
        warning = {}
        return {'value': res,
                'warning': warning}

    def onchange_expense_area_id(self, cr, uid, ids, expense_area_id,
                                 simulation_cost_state, project_id,
                                 simulation_cost_id, context=None):
        for simulation_cost_line in self.browse(cr, uid, ids):
            if simulation_cost_line.sale_order_line_id.id:
                return {'value': {'expense_area_id':
                                  simulation_cost_line.expense_area_id.id},
                        'warning': {'title': _('Expense Area Error'),
                                    'message': _('You can not modify the '
                                                 'expense area, this line '
                                                 'belongs to a line of sale '
                                                 'order')
                                    }
                        }
        res = {}
        domain = {}
        warning = {}
        simulation_cost_obj = self.pool['simulation.cost']
        analytic_line_obj = self.pool['account.analytic.line']
        expense_area_obj = self.pool['expense.area']
        project_obj = self.pool['project.project']
        analytic_journal_obj = self.pool['account.analytic.journal']
        account_obj = self.pool['account.account']
        # Accedo a los datos de la simulacion
        simulation_cost = simulation_cost_obj.browse(
            cr, uid, simulation_cost_id, context)
        # Cojo el diario analítico
        cond = [('name', 'like', 'Presupuestarias')]
        account_journal_ids = analytic_journal_obj.search(cr, uid, cond,
                                                          context)
        if not account_journal_ids:
            raise orm.except_orm(_('Sale Order Creation Error'),
                                 _('Journal with Presupuestarias literal '
                                   'NOT FOUND'))
        # Cojo la cuenta general
        cond = [('name', 'like', 'Your Company')]
        account_account_ids = account_obj.search(cr, uid, cond, context)
        if not account_account_ids:
            raise orm.except_orm(_('Sale Order Creation Error'),
                                 _('General Account YOUR COMPANY not found'))
        if expense_area_id and project_id:
            if simulation_cost_state:
                if (simulation_cost_state == 'inmodif_budgetary' and
                        not simulation_cost.generate_by_lines):
                    expense_area = expense_area_obj.browse(
                        cr, uid, expense_area_id, context)
                    project = project_obj.browse(cr, uid, project_id, context)
                    cond = [('name', 'like', ('Budgetary - ' +
                                              expense_area.name)),
                            ('type', '=', 'budgetary'),
                            ('expense_area_id', '=', expense_area.id),
                            ('account_id', '=',
                            project.analytic_account_id.id),
                            ('journal_id', '=', account_journal_ids[0]),
                            ('general_account_id', '=',
                             account_account_ids[0])]
                    account_line_ids = analytic_line_obj.search(
                        cr, uid, cond, context)
                    if not account_line_ids:
                        res.update({'expense_area_id': False
                                    })
                        warning.update({'title': _('Expense Area Error'),
                                        'message': _('Budgetary not found in '
                                                     'analytic lines for '
                                                     'expense area %s') %
                                        expense_area.name
                                        })
        category_ids = []
        if expense_area_id:
            for simcategory in simulation_cost.simulation_category_ids:
                if expense_area_id == simcategory.expense_area_id.id:
                    if not simcategory.restricted_category:
                        category_ids.append(simcategory.category_id.id)
        domain = [('categ_id', 'in', category_ids)]
        res.update({'product_id': False})
        return {'value': res,
#                'domain': {'product_id': domain
#                           },
                'warning': warning}
