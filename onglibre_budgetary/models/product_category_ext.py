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


class ProductCategory(orm.Model):
    _inherit = 'product.category'

    _columns = {
        # Nombre
        'name': fields.char('Name', size=128, required=True, translate=True,
                            select=True),
        # Lineas de simulacion con categorias permitidas
        'simulation_cost_line_ids':
            fields.many2many('simulation.cost.line',
                             'simucostline_category_rel', 'category_id',
                             'simulation_cost_line_id', 'Simulation Costs'),
    }
