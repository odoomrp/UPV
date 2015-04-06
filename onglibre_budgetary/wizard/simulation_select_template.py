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
import time


class SimulationSelectTemplate(orm.TransientModel):
    _inherit = 'simulation.select.template'

    _columns = {'stage': fields.char('Stage', size=128)
                }

    def template_selected(self, cr, uid, ids, context=None):
        cost_line_obj = self.pool['simulation.cost.line']
        simulation_obj = self.pool['simulation.cost']
        product_obj = self.pool['product.product']
        simu_id = context.get('active_id')
        supplierinfo_obj = self.pool['product.supplierinfo']
        partner_obj = self.pool['res.partner']
        pricelist_obj = self.pool['product.pricelist']
        if not simu_id:
            raise orm.except_orm(_('Error'),
                                 _('You should save before the simulation'))
        simulation = simulation_obj.browse(cr, uid, simu_id, context)
        for wiz in self.browse(cr, uid, ids, context):
            src_temp = wiz.template_id
            data = {}
            expense_area_ids = []
            for expense_area in src_temp.expense_area_ids:
                # Cojo Áreas de Gasto
                expense_area_ids.append(expense_area.id)
            category_ids = []
            for category in src_temp.simulation_template_category_ids:
                # Cojo Áreas de Gasto
                category_ids.append((0, 0, {
                    'simulation_cost_id': simulation.id,
                    'name': category.name,
                    'expense_area_id': category.expense_area_id.id,
                    'category_id': category.category_id.id,
                    'restricted_category': category.restricted_category,
                    'amount': category.amount,
                    'notes': category.notes
                    }))
                vals = {'expense_area_ids': [(6, 0, expense_area_ids)],
                        'simulation_category_ids': category_ids}
            simulation_obj.write(cr, uid, simulation.id, vals, context)
            for line in src_temp.others_template_lines_ids:
                # Cojo datos del producto
                product = product_obj.browse(cr, uid, line.product_id.id,
                                             context)
                restricted = False
                category_ids = []
                if simulation.simulation_category_ids:
                    for category in simulation.simulation_category_ids:
                        category_ids.append(category.category_id.id)
                        if (category.category_id.id == product.categ_id.id and
                                category.restricted_category):
                            restricted = True
                # Cojo el primer proveedor para el producto
                cond = [('product_tmpl_id', '=',
                         line.product_id.product_tmpl_id.id)]
                supplierinfo_ids = supplierinfo_obj.search(
                    cr, uid, cond, context=context, order='sequence')
                # Si no tiene cantidad, le pongo 1
                if not line.amount:
                    line.amount = 0
                # Diferencio si el producto tiene proveedores o no tiene
                if not restricted and product.categ_id.id in category_ids:
                    if supplierinfo_ids:
                        supplierinfo_id = supplierinfo_obj.browse(
                            cr, uid, supplierinfo_ids[0], context)
                        supplier = partner_obj.browse(
                            cr, uid, supplierinfo_id.name.id, context)
                        lang = partner_obj.browse(
                            cr, uid, supplierinfo_id.name.id, context).lang
                        pprice = supplier.property_product_pricelist_purchase
                        pricelist_id = pprice.id
                        # Accedo a datos del producto.
                        context_partner = {'lang': lang,
                                           'partner_id':
                                           supplierinfo_id.name.id}
                        product = product_obj.browse(
                            cr, uid, line.product_id.id,
                            context=context_partner)
                        # Le pongo la fecha del sistema
                        estim_dpurch_completion = time.strftime('%Y-%m-%d')
                        # Cojo el precio de compra según tablas.
                        price = pricelist_obj.price_get(
                            cr, uid, [pricelist_id], product.id, line.amount,
                            supplierinfo_id.name.id,
                            {'uom': product.uom_id.id,
                             'date': estim_dpurch_completion})[pricelist_id]
                        # Calculo el total compra
                        subtotal_purchase = line.amount * price
                        # Calculo la amortizacion y los costes indirectos
                        amortization_cost = 0
                        if line.amortization_rate:
                            if (line.amortization_rate > 0 and
                                    subtotal_purchase > 0):
                                amortization_cost = (line.amount *
                                                     line.amortization_rate)
                        indirect_cost = 0
                        if line.indirect_cost_rate:
                            if (line.indirect_cost_rate > 0 and
                                    subtotal_purchase > 0):
                                indirect_cost = (line.amount *
                                                 line.indirect_cost_rate)
                        subtotal_sale = (line.product_id.list_price *
                                         line.amount)
                        cost = (subtotal_purchase + amortization_cost +
                                indirect_cost)
                        estimated_margin = 0
                        if cost:
                            estimated_margin = (subtotal_sale / cost) - 1
                        margin_percent = estimated_margin * 100
                        data = {'simulation_cost_id': simu_id,
                                'product_id': line.product_id.id,
                                'product_sale_id': line.product_id.id,
                                'sale_price': line.product_id.list_price,
                                'subtotal_sale': subtotal_sale,
                                'estimated_margin': estimated_margin,
                                'margin_percent': margin_percent,
                                'name': line.name,
                                'description': line.description,
                                'supplier_id': supplierinfo_id.name.id,
                                'purchase_price': price,
                                'uom_id': line.uom_id.id,
                                'amount': line.amount,
                                'sale_amount': line.amount,
                                'subtotal_purchase': subtotal_purchase,
                                'type_cost': line.type_cost,
                                'type2': line.type2,
                                'type3': line.type3,
                                'expense_area_id': line.expense_area_id.id,
                                'amortization_rate': line.amortization_rate,
                                'amortization_cost': amortization_cost,
                                'indirect_cost_rate': line.indirect_cost_rate,
                                'indirect_cost': indirect_cost,
                                'template_id': src_temp.id,
                                'stage': wiz.stage,
                                'estim_dpurch_completion':
                                estim_dpurch_completion}
                        cost_line_obj.create(cr, uid, data, context)
                    else:
                        # Calculo el total de la venta
                        if product.standard_price:
                            subtotal_purchase = (line.amount *
                                                 product.standard_price)
                        else:
                            subtotal_purchase = 0
                        # Calculo la amortizacion y los costes indirectos
                        amortization_cost = 0
                        if line.amortization_rate:
                            if (line.amortization_rate > 0 and
                                    subtotal_purchase > 0):
                                amortization_cost = (line.amount *
                                                     line.amortization_rate)
                        indirect_cost = 0
                        if line.indirect_cost_rate:
                            if (line.indirect_cost_rate > 0 and
                                    subtotal_purchase > 0):
                                indirect_cost = (line.amount *
                                                 line.indirect_cost_rate)
                        subtotal_sale = (line.product_id.list_price *
                                         line.amount)
                        cost = (subtotal_purchase + amortization_cost +
                                indirect_cost)
                        estimated_margin = 0
                        if cost:
                            estimated_margin = (subtotal_sale / cost) - 1
                        margin_percent = estimated_margin * 100
                        data = {'simulation_cost_id': simu_id,
                                'product_id': line.product_id.id,
                                'product_sale_id': line.product_id.id,
                                'sale_price': line.product_id.list_price,
                                'subtotal_sale': subtotal_sale,
                                'estimated_margin': estimated_margin,
                                'margin_percent': margin_percent,
                                'name': line.name,
                                'description': line.description,
                                'purchase_price': product.standard_price,
                                'uom_id': line.uom_id.id,
                                'amount': line.amount,
                                'sale_amount': line.amount,
                                'subtotal_purchase': subtotal_purchase,
                                'type_cost': line.type_cost,
                                'type2': line.type2,
                                'type3': line.type3,
                                'expense_area_id': line.expense_area_id.id,
                                'amortization_rate': line.amortization_rate,
                                'amortization_cost': amortization_cost,
                                'indirect_cost_rate': line.indirect_cost_rate,
                                'indirect_cost': indirect_cost,
                                'template_id': src_temp.id,
                                'stage': wiz.stage, }
                        cost_line_obj.create(cr, uid, data, context)
        return {'type': 'ir.actions.act_window_close'}
