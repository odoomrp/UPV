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


class ImportTemplate(orm.TransientModel):
    _name = 'import.template'
    _description = "Import Template"

    _columns = {
        # Fecha Comienzo
        'start_date': fields.date('Start Date', required=True),
        # Fecha Fin
        'end_date': fields.date('End Date', required=True),
        # Plantilla
        'festive_template_id':
            fields.many2one('festive.template', 'Template', required=True),
    }

    def action_import_template(self, cr, uid, ids, context=None):
        festive_tline_obj = self.pool['festive.template.line']
        resources_obj = self.pool['estimated.calendar.resources']
        employ_calendar_obj = self.pool['hr.employee.calendar']
        employee_id = context.get('active_id')
        for wiz in self.browse(cr, uid, ids, context):
            start_date = wiz.start_date
            start_year = int(str(start_date[0:4]))
            end_date = wiz.end_date
            end_year = int(str(end_date[0:4]))
            src_temp = wiz.festive_template_id
            if start_year != end_year:
                raise orm.except_orm(_('Import Template Error'),
                                     _('Start and End Year are differents'))
            if end_date < start_date:
                raise orm.except_orm(_('Import Template Error'),
                                     _('End Date < Start Date'))
            fec_ini = start_date
            fec_ini = datetime.strptime(fec_ini, '%Y-%m-%d')
            fec_fin = end_date
            fec_fin = datetime.strptime(fec_fin, '%Y-%m-%d')
            while fec_ini <= fec_fin:
                my_date_alpha = str(fec_ini)
                my_date = my_date_alpha[0:10]
                my_date_year = my_date[0:4]
                # Miro que exista el calendario para el trabajador.
                cond = [('employee_id', '=', employee_id),
                        ('year', '=', my_date_year)]
                employ_calendar_ids = employ_calendar_obj.search(
                    cr, uid, cond, context=context)
                if not employ_calendar_ids:
                    line_vals = {'employee_id': employee_id,
                                 'year': my_date_year,
                                 'name': 'Calendar ' + str(my_date_year),
                                 }
                    employ_calendar_id = employ_calendar_obj.create(
                        cr, uid, line_vals, context=context)
                else:
                    employ_calendar_id = employ_calendar_ids[0]
                cond = [('festive_template_id', '=', src_temp.id),
                        ('date', '=', my_date)]
                festive_tline_ids = festive_tline_obj.search(
                    cr, uid, cond, context=context)
                if not festive_tline_ids:
                    cond = [('hr_employee_calendar_id', '=',
                             employ_calendar_id),
                            ('date', '=', my_date)]
                    resources_ids = resources_obj.search(
                        cr, uid, cond, context=context)
                    if not resources_ids:
                        line_vals = {'hr_employee_calendar_id':
                                     employ_calendar_id,
                                     'date': my_date,
                                     'hours': 8,
                                     }
                        resources_obj.create(cr, uid, line_vals,
                                             context=context)
                    else:
                        line_vals = {'name': False,
                                     'hours': 8
                                     }
                        resources_obj.write(cr, uid, resources_ids, line_vals,
                                            context=context)
                else:
                    festive_template = festive_tline_obj.browse(
                        cr, uid, festive_tline_ids[0], context=context)
                    cond = [('hr_employee_calendar_id', '=',
                             employ_calendar_id),
                            ('date', '=', my_date)
                            ]
                    resources_ids = resources_obj.search(cr, uid, cond,
                                                         context=context)
                    color = festive_template.background_color
                    if not resources_ids:
                        line_vals = {'hr_employee_calendar_id':
                                     employ_calendar_id,
                                     'date': my_date,
                                     'name': festive_template.name,
                                     'hours': 0,
                                     'background_color': color,
                                     }
                        resources_obj.create(cr, uid, line_vals,
                                             context=context)
                    else:
                        line_vals = {'name': festive_template.name,
                                     'hours': 0,
                                     'background_color': color
                                     }
                        resources_obj.write(cr, uid, resources_ids,
                                            line_vals, context=context)
                # Sumo 1 día a la fecha
                fec_ini = fec_ini + timedelta(days=1)
                fec_ini.strftime('%Y-%m-%d')
        return {'type': 'ir.actions.act_window_close'}
