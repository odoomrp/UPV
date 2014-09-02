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


class SimulationCostPrevision(orm.Model):
    _name = 'simulation.cost.prevision'
    _description = 'Simulation Costs Previsions'

    _columns = {
        'simulation_cost_id': fields.many2one('simulation.cost',
                                              'Simulation Cost'),
        'period_date': fields.char('Year-Month', size=8),
        # mes
        'month': fields.integer('Period'),
        # Costes en el mes
        'costs_amount_month': fields.float('Costs amount by period',
                                           digits=(7, 2)),
        # Prevision pago en el mes
        'payment_prevision_month': fields.float('Payment prevision',
                                                digits=(7, 2)),
        # Porcentage a facturar
        'percentage_invoice': fields.float('Percentage by invoice',
                                           digits=(3, 2)),
        # Porcentage a cobrar
        'percentage_charge': fields.float('Percentage by charge',
                                          digits=(3, 2)),
        # Ventas en el mes
        'sales_amount_month': fields.float('Sales by period',
                                           digits=(7, 2)),
        # Prevision cobro en el mes
        'charge_prevision_month': fields.float('Charge prevision',
                                               digits=(7, 2)),
    }
