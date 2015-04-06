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


class ProjectFinancing(orm.Model):

    _name = 'project.financing'
    _description = 'Project Financing'
    _order = 'priority'

    _columns = {
        # Descripcion
        'name': fields.related('financing_source_id', 'name', string="Name",
                               type='char', size=128, store=True),
        # Proyecto
        'project_id': fields.many2one('project.project', 'Project'),
        # Fuente de Financiación
        'financing_source_id':
            fields.many2one('financing.source', 'Financing Source',
                            ondelete="cascade"),
        # Prioridad
        'priority': fields.integer('Priority'),
        # Porcentaje fondo financiador
        'project_percent': fields.float('Project %'),
        # Organismo Financiador
        'res_partner_id':
            fields.related('financing_source_id', 'res_partner_id',
                           type='many2one', relation='res.partner',
                           string='Financing Organism'),
        # Código Convocatoria
        'code_call_id':
            fields.related('financing_source_id', 'code_call_id',
                           type='many2one', relation='code.call',
                           string='Code Call'),
        # Código expediente organismo financiador
        'funder_record_code':
            fields.related('financing_source_id', 'funder_record_code',
                           type='char', size=64, string='Funder Record Code'),
        # Porcentaje Fuente de Financiacion
        'financial_source_percent': fields.float('Financial Source %'),
        # Concesión
        'grant': fields.integer('Grant'),
        # Concesión
        'amount_awarded': fields.integer('amount_awarded'),
        # Concesión
        'overheads': fields.integer('Overheads'),
        # Area de Gasto
        'expense_area_id': fields.many2one('expense.area', 'Expense Area'),
    }
    _defaults = {'priority': lambda *a: 1,
                 }
