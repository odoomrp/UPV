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


class EstimatedCalendarResources(orm.Model):

    _name = 'estimated.calendar.resources'
    _description = 'Estimated Calendar Resources'
    _date_name = 'date'
    _order = 'date'

    _columns = {
        # Calendario del empleado
        'hr_employee_calendar_id':
            fields.many2one('hr.employee.calendar', 'Employee Calendar',
                            ondelete='cascade'),
        # Empleado
        'employee_id':
            fields.related('hr_employee_calendar_id', 'employee_id',
                           type='many2one', relation='hr.employee',
                           string='Employee', store=True),
        # Fecha
        'date': fields.date('Date', required=True),
        # Motivo Festivo
        'name': fields.char('Reason', size=64),
        # Horas
        'hours': fields.float('Hours'),
        # Color del Fondo
        'background_color': fields.selection([('None', ''),
                                              ('Blue', 'Blue'),
                                              ('LightBlue', 'Light Blue'),
                                              ('Red', 'Red'),
                                              ('Green', 'Green'),
                                              ('LightGreen', 'Light Green'),
                                              ('Yellow', 'Yellow'),
                                              ('Orange', 'Orange'),
                                              ('DarkOrange', 'Dark Orange'),
                                              ('Maroon', 'Maroon'),
                                              ('Aqua', 'Aqua'),
                                              ('Fuchsia', 'Fuchsia'),
                                              ('LightGrey', 'LightGrey')],
                                             string="background color"),
        }
