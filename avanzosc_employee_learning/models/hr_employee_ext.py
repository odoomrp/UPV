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


class HrEmployee(orm.Model):
    _inherit = 'hr.employee'

    _columns = {
        # Titulos del Empleado
        'title_ids':
            fields.many2many('hr.employee.title', 'employee_title_rel',
                             'title_id', 'employee_id', 'Titles'),
        # Cursos de Tipo Externo
        'external_formation_ids':
            fields.one2many('hr.employee.formation', 'employee_id',
                            'External_formation', domain=[('type', '=',
                                                           'External')]),
        # Cursos de Tipo Interno
        'internal_formation_ids':
            fields.one2many('hr.employee.formation', 'employee_id',
                            'Internal_formation', domain=[('type', '=',
                                                           'Internal')]),
    }
