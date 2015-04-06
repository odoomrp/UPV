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


class ProjectActivity(orm.Model):
    _name = 'project.activity'
    _description = 'Activity'

    _columns = {
        # Campo para guardar el nombre de la actividad
        'name': fields.char('Name', size=64, required=True, select=1),
        # Campo para saber las subactividades relacionadas con la actividad
        'subactivity_ids':
            fields.one2many('project.subactivity', 'activity_id',
                            'Subactivitys'),
        # Campo para saber con que proyectos esta relacionado la actividad
        'project_activity_ids':
            fields.one2many('project.project', 'project_activity_id',
                            "Projects"),
    }
