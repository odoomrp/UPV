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


class FestiveTemplateLine(orm.Model):

    _name = 'festive.template.line'
    _description = 'Festive Template Line'
    _order = 'date'

    _columns = {
        # ID Plantilla Festivo
        'festive_template_id':
            fields.many2one('festive.template', 'Festive Template',
                            ondelete='cascade'),
        # Fecha Inicio
        'date': fields.date('Date', required=True),
        # Descripción
        'name': fields.char('Description', size=64, required=True),
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
