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
import time


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def action_wait(self, cr, uid, ids, context=None):
        # Accedo al PEDIDO DE VENTA
        simulation_cost_obj = self.pool['simulation.cost']
        sale_order2 = self.browse(cr, uid, ids[0], context)
        # SI EL PEDIDO DE VENTA VIENE DE UNA SIMULACION, COJO LA ÚLTIMA
        # SIMULACIÓ ACTIVA QUE NO ESTE CANCELADA, O LA ÚLTIMA HITORIFICADA
        w_found = 0
        w_simulation_cost_id = False
        w_maxid = 0
        if sale_order2.simulation_cost_ids:
            # Recorro todas las simulaciones asociadas al pedido de venta
            for simulation_cost in sale_order2.simulation_cost_ids:
                if ((not simulation_cost.historical_ok) and
                        simulation_cost.state not in ('canceled')):
                    # Si es una simulación activa, me quedo con este id
                    w_found = 1
                    w_simulation_cost_id = simulation_cost.id
                else:
                    # Si no ha encontrado la activa me quedo con la última
                    # simulación de coste historificada (la mas nueva, la
                    # de mayor id)
                    if w_found == 0:
                        if simulation_cost.id > w_maxid:
                            w_maxid = simulation_cost.id
            if w_simulation_cost_id == 0:
                # Si no he encontrado una simulación de coste activa para ese
                # pedido de venta
                if w_maxid == 0:
                    # Si no he encontrado una simulación de coste historificada
                    # para ese pedido de venta
                    raise orm.except_orm(_('Project Creation Error'),
                                         _('Simulation Cost not found'))
                else:
                    # Si no he encontrado una simulación de coste activa para
                    # ese pedido de venta, me quedo con el id de la simulación
                    # de coste historificada mas nueva
                    w_simulation_cost_id = w_maxid
        # ACTUALIZO LA FECHA REAL DE FIRMA DE SIMULACION DE COSTE, CON LA
        # FECHA DE ACEPTACION DEL PEDIDO DE VENTA
        if w_simulation_cost_id:
            vals = {'real_date_of_signature': time.strftime('%Y-%m-%d')}
            simulation_cost_obj.write(cr, uid, [w_simulation_cost_id], vals,
                                      context)
        super(SaleOrder, self).action_wait(cr, uid, ids, context)
        return True
