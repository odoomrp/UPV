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


class ProjectPublication(orm.Model):
    _name = 'project.publication'
    _description = 'Project Publication'

    _columns = {
        # Nombre de publicación
        'name': fields.char('Name', size=64, required=True, select=1),
        # Campo para saber el tipo de publicación al que pertenece la
        # publicación
        'publication_type_id':
            fields.many2one('project.publication.type', 'Publication Type',
                            required=True, select=1),
        # Campo Fecha de Publicación
        'publication_date': fields.date('Publication Date'),
        # Campo Fecha de Presentacion
        'filing_date': fields.datetime('Filing Date'),
        # Titulo
        'title': fields.char('Title', size=64, required=True),
        # Autor Interno
        'employee_id': fields.many2one('hr.employee', 'Employee', select=1),
        # Contacto
        'contact_id': fields.many2one('res.partner.title', 'Contact',
                                      select=1),
        # Observaciones
        'comments': fields.text('Comments'),
        # Campo para saber el/los proyectos, con que publicacion/es esta/n
        # relacionado/s
        'project_ids':
            fields.many2many('project.project', 'project_publication_rel',
                             'publication_id', 'proyect_id', 'Projects'),
    }
