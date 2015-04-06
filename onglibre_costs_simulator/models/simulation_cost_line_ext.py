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


class SimulationCostLine(orm.Model):
    _inherit = 'simulation.cost.line'

    _columns = {
        # Mes inicio Coste
        'month_start_cost': fields.integer('Month Start Cost'),
        # Mes fin Coste
        'month_end_cost': fields.integer('Month End Cost'),
        'month_duration': fields.integer('Duration'),
        # Delay Coste
        'delay_cost': fields.integer('Delay Cost'),
        # Mes inicio Venta
        'month_start_sale': fields.integer('Month Start Sale'),
        # Mes fin Venta
        'month_end_sale': fields.integer('Month End Sale'),
        # Delay Sale
        'delay_sale': fields.integer('Delay Sale'),
        #
        'sale_duration': fields.integer('Duration'),
    }
    _defaults = {
        'month_start_cost': lambda *a: 1,
        'month_duration': lambda *a: 1,
        'month_start_sale': lambda *a: 1,
        'sale_duration': lambda *a: 1
        }
