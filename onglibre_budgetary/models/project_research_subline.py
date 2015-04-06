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


class ProjectResearchSubline(orm.Model):
    _name = 'project.research.subline'
    _description = 'Project Research Subline'

    _columns = {
        # Nombre de la sublinea
        'code': fields.char('Code', size=64, required=True),
        'name': fields.char('Name', size=64, required=True, select=1),
        # Campo para saber con que lineas esta relacionado
        'project_research_line_id':
            fields.many2one('project.research.line', 'Project Line',
                            required="True", select=1),
        # Campo para saber con que proyectos esta relacionado la subactividad
        'project_ids':
            fields.one2many('project.project', 'project_research_subline_id',
                            "Projects"),
    }
