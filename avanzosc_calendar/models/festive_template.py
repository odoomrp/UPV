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


class FestiveTemplate(orm.Model):

    _name = 'festive.template'
    _description = 'Festive Template'

    _columns = {
        # Descripción
        'name': fields.char('Name', size=64, required=True),
        # Codigo
        'year': fields.integer('Year', size=4, required=True),
        # Lineas de Plantilla de Festivos
        'festive_template_lines_ids':
            fields.one2many('festive.template.line', 'festive_template_id',
                            'Festive Template Lines'),
    }
