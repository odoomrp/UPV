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


class SimulationTemplateCategory(orm.Model):
    _name = 'simulation.template.category'
    _description = 'Simulation Template Category'

    _columns = {
        'simulation_template_id':
            fields.many2one('simulation.template', 'Simulation Template',
                            ondelete='cascade'),
        # Nombre del Subsector
        'name': fields.char('Name', size=64),
        # Area de gasto
        'expense_area_id': fields.many2one('expense.area', 'Expense Area',
                                           required=True),
        # Categoria
        'category_id': fields.many2one('product.category', 'Category',
                                       required=True),
        # Categoría restringida
        'restricted_category': fields.boolean('Restricted'),
        # Importe
        'amount': fields.float('Amount', digits=(7, 2)),
        # Observaciones
        'notes': fields.char('Notes', size=128),
    }

    def onchange_restricted_category(self, cr, uid, ids, category_id,
                                     restricted_category,
                                     others_cost_lines_ids, context=None):
        product_obj = self.pool['product.product']
        result = {}
        res = {}
        my_products = []
        if restricted_category:
            if others_cost_lines_ids:
                for line in others_cost_lines_ids:
                    cost = line[2]
                    product = product_obj.browse(
                        cr, uid, cost.get('product_id'), context)
                    if product.categ_id.id == category_id:
                        my_products.append(product.id)
        if my_products:
            res.update({'restricted_category': False})
            result = {'value': {'value': res}}
            texto = ""
            for product in my_products:
                producto = product_obj.browse(cr, uid, product, context)
                texto = texto + producto.name + ', '
                lite = _('Found products with this restricted category, '
                         'products: ')
            result.update({'warning': {'title': 'warning', 'message':
                                       lite + texto}})
        return result
