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
#    MERCHANT ABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp.osv import fields, orm
from openerp.tools.translate import _
from datetime import datetime, timedelta


class MakeHoursToWork(orm.TransientModel):
    _name = 'make.hours.to.work'
    _description = "Make Hours To Work"

    _columns = {
        # Fecha Comienzo
        'start_date': fields.date('Start Date', required=True),
        # Fecha Fin
        'end_date': fields.date('End Date', required=True),
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
                                             string="background color",
                                             required=True),
        # Motivo.
        'name': fields.char('Reason', size=64),
        # Horas
        'hours': fields.float('Hours', required=True),
        # Lunes
        'monday': fields.boolean('Monday'),
        # Martes
        'tuesday': fields.boolean('Tuesday'),
        # Miercoles
        'wednesday': fields.boolean('Wednesday'),
        # Jueves
        'thursday': fields.boolean('Thursday'),
        # Viernes
        'friday': fields.boolean('Friday'),
        # Sabado
        'saturday': fields.boolean('Saturday'),
        # Domingo
        'sunday': fields.boolean('Sunday'),
    }
    _defaults = {'background_color': lambda *a: 'None'
                 }

    def generate_hours_to_work(self, cr, uid, ids, context=None):
        employee_id = context.get('active_id')
        for wiz in self.browse(cr, uid, ids, context):
            start_date = wiz.start_date
            start_year = int(str(start_date[0:4]))
            end_date = wiz.end_date
            end_year = int(str(end_date[0:4]))
            background_color = wiz.background_color
            name = wiz.name
            hours = wiz.hours
            monday = wiz.monday
            tuesday = wiz.tuesday
            wednesday = wiz.wednesday
            thursday = wiz.thursday
            friday = wiz.friday
            saturday = wiz.saturday
            sunday = wiz.sunday
            if start_year != end_year:
                raise orm.except_orm(_('Holidays Generation Error'),
                                     _('Start and End Year are differents'))
            if end_date < start_date:
                raise orm.except_orm(_('Holidays Generation Error'),
                                     _('End Date < Start Date'))
            fec_ini = start_date
            fec_ini = datetime.strptime(fec_ini, '%Y-%m-%d')
            fec_fin = end_date
            fec_fin = datetime.strptime(fec_fin, '%Y-%m-%d')
            while fec_ini <= fec_fin:
                if (monday or tuesday or wednesday or thursday or friday or
                        saturday or sunday):
                    dia = self._calculate_day(cr, uid, fec_ini)
                    if monday and dia == 'Lunes':
                        self._write_hours_to_work(
                            cr, uid, employee_id, fec_ini, name, hours,
                            background_color)
                    if tuesday and dia == 'Martes':
                        self._write_hours_to_work(
                            cr, uid, employee_id, fec_ini, name, hours,
                            background_color)
                    if wednesday and dia == 'Miercoles':
                        self._write_hours_to_work(
                            cr, uid, employee_id, fec_ini, name, hours,
                            background_color)
                    if thursday and dia == 'Jueves':
                        self._write_hours_to_work(
                            cr, uid, employee_id, fec_ini, name, hours,
                            background_color)
                    if friday and dia == 'Viernes':
                        self._write_hours_to_work(
                            cr, uid, employee_id, fec_ini, name, hours,
                            background_color)
                    if saturday and dia == 'Sabado':
                        self._write_hours_to_work(
                            cr, uid, employee_id, fec_ini, name, hours,
                            background_color)
                    if sunday and dia == 'Domingo':
                        self._write_hours_to_work(
                            cr, uid, employee_id, fec_ini, name, hours,
                            background_color)
                else:
                    self._write_hours_to_work(
                        cr, uid, employee_id, fec_ini, name, hours,
                        background_color)
                # Sumo 1 día a la fecha
                fec_ini = fec_ini + timedelta(days=1)
                fec_ini.strftime('%Y-%m-%d')
        return {'type': 'ir.actions.act_window_close'}

    def _calculate_day(self, cr, uid, my_date):
        actual_date = str(my_date)
        actual_date = actual_date[0:10]
        from datetime import date
        dia = ['Sabado', 'Domingo', 'Lunes', 'Martes', 'Miercoles', 'Jueves',
               'Viernes']
        arrayfNac = actual_date.split('-')
        dfNac = date(int(arrayfNac[0]), int(arrayfNac[1]), int(arrayfNac[2]))
        val1 = dfNac.month
        val2 = dfNac.year
        if(dfNac.month == 1):
            val1 = 13
            val2 = val2 - 1
        if(dfNac.month == 2):
            val1 = 14
            val2 = val2-1
        val3 = ((val1+1)*3)/5
        val4 = val2/4
        val5 = val2/100
        val6 = val2/400
        val7 = dfNac.day+(val1*2)+val3+val2+val4-val5+val6+2
        val8 = val7/7
        val0 = val7-(val8*7)
        return (dia[val0])

    def _write_hours_to_work(self, cr, uid, employee_id, my_date, name, hours,
                             background_color):
        employ_calendar_obj = self.pool['hr.employee.calendar']
        resources_obj = self.pool['estimated.calendar.resources']
        actual_date = str(my_date)
        actual_date = actual_date[0:10]
        my_date_year = actual_date[0:4]
        # Miro que exista el calendario para el trabajador.
        cond = [('employee_id', '=', employee_id),
                ('year', '=', my_date_year)]
        employ_calendar_ids = employ_calendar_obj.search(cr, uid, cond)
        if not employ_calendar_ids:
            line_vals = {'employee_id': employee_id,
                         'year': my_date_year,
                         'name': 'Calendar ' + str(my_date_year)
                         }
            employ_calendar_id = employ_calendar_obj.create(cr, uid, line_vals)
        else:
            employ_calendar_id = employ_calendar_ids[0]
        cond = [('hr_employee_calendar_id', '=', employ_calendar_id),
                ('date', '=', actual_date)]
        resources_ids = resources_obj.search(cr, uid, cond)
        if not resources_ids:
            line_vals = {'hr_employee_calendar_id': employ_calendar_id,
                         'name': name,
                         'date': my_date,
                         'hours': hours,
                         'background_color': background_color
                         }
            resources_obj.create(cr, uid, line_vals)
        else:
            estimated_calendar_resources = resources_obj.browse(
                cr, uid, resources_ids[0])
            if estimated_calendar_resources.hours > 0:
                vals = {'name': name,
                        'hours': hours,
                        'background_color': background_color
                        }
                resources_obj.write(cr, uid, resources_ids, vals)
        return True
