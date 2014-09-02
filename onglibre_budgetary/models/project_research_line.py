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


class ProjectResearchLine(orm.Model):
    _name = 'project.research.line'
    _description = 'Line'

    _columns = {
        # Código de la línea de investigación
        'code': fields.char('Code', size=64, required="True", select=1),
        # Nombre de la línea de investigación
        'name': fields.char('Name', size=64, required="True", select=1),
        # Campo para saber las subactividades relacionadas con la actividad
        'project_sublines_ids':
            fields.one2many('project.research.subline',
                            'project_research_line_id', 'Sublines'),
        # Campo para saber con que proyectos esta relacionado la línea de
        # investigacion
        'project_ids':
            fields.one2many('project.project', 'project_research_line_id',
                            "Projects"),
    }
