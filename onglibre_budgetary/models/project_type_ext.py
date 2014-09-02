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


class ProjectType(orm.Model):
    _inherit = 'project.type'

    _columns = {
        # Descripcion del tipo de proyecto
        'description': fields.text('Description'),
        # Diario de ventas
        'sale_journal_id':
            fields.many2one('account.journal', 'Sale Journal',
                            domain=[('type', '=', 'sale')]),
        # Secuencia
        'project_type_sequence_id': fields.many2one('ir.sequence', 'Sequence',
                                                    required=True),
        # Campo para saber si hay que generar estructura analitica por lineas
        'generate_by_lines': fields.boolean('Generate By Lines'),
        # Adicionando un check para identificar si es un proyecto
        # administrativo o no.
        'administrative': fields.boolean('Administrative')
    }
