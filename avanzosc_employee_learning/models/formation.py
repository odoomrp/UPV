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


class Formation(orm.Model):
    _name = 'formation'
    _description = 'Formation'

    _columns = {
        # Descripción
        'name': fields.char('Name', size=64, required=True),
        # Codigo
        'code': fields.char('Code', size=64, required=True),
        # Tipo de Curso (Externo/Interno)
        'type': fields.selection([('Internal', 'Internal'),
                                  ('External', 'External')],
                                 'Type', required=True),
        # Fecha Inicio
        'start_date': fields.date('Start Date'),
        # Fecha Inicio
        'end_date': fields.date('End Date'),
        # Realizado
        'realized': fields.boolean('Realized'),
    }
