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


class HrContract(orm.Model):
    _inherit = 'hr.contract'

    def _subtotal_variable_amount(self, cr, uid, ids, name, args,
                                  context=None):
        res = {}
        for hr_employee in self.browse(cr, uid, ids, context=context):
            if hr_employee.wage and hr_employee.variable_percentage:
                res[hr_employee.id] = (hr_employee.wage *
                                       hr_employee.variable_percentage) / 100
            else:
                res[hr_employee.id] = 0
        return res

    def _total(self, cr, uid, ids, name, args, context=None):
        res = {}
        for hr_employee in self.browse(cr, uid, ids, context=context):
            if hr_employee.wage and hr_employee.variable_percentage:
                importe = (hr_employee.wage *
                           hr_employee.variable_percentage) / 100
                res[hr_employee.id] = hr_employee.wage + importe
            else:
                res[hr_employee.id] = 0
        return res

    _columns = {
        # Porcentaje Variables
        'variable_percentage': fields.float('Variable %', digits=(3, 2)),
        # Importe Variable
        'variable_amount':
            fields.function(_subtotal_variable_amount, method=True,
                            digits=(8, 2), string='Variable Amount',
                            store=False),
        # Suma parte fija + parte variable
        'total':
            fields.function(_total, method=True, digits=(8, 2),
                            string='Variable Amount', store=False),
    }
