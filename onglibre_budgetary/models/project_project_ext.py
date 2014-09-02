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


class ProjectProject(orm.Model):
    _inherit = 'project.project'

    _columns = {
        # Campo para saber el proyecto con que cliente final esta relacionado
        'final_partner_id': fields.many2one('res.partner', 'Final Customer'),
        # Campo para relacionar la Simulación de Costes con departamentos
        'department_id': fields.many2one('hr.department', 'Department',
                                         select=1),
        # Campo para relacionar la Simulación de Costes con campañas
        'crm_case_resource_type_id': fields.many2one('crm.tracking.campaign',
                                                     'Campaign', select=1),
        # Campo para relacionar la Simulación de Costes con tipos de proyectos
        'project_type_id': fields.many2one('project.type', 'Project Type',
                                           select=1),
        # Campo para relacionar la Simulación de Costes con tipos de proyectos
        'subsector_id': fields.many2one('subsector', 'Subsector', select=1),
        # Campo para saber el proyecto con que actividad esta relacionado
        'project_activity_id': fields.many2one('project.activity', 'Activity',
                                               select=1),
        # Campo para saber el proyecto con que subactividad esta relacionado
        'project_subactivity_id':
            fields.many2one('project.subactivity', 'Subactivity', select=1),
        # Campo para saber el proyecto con que administracion esta realacionado
        'administration_id':
            fields.many2one('administration', 'Administration', select=1),
        # Campo para saber el proyecto con que tipo de programa esta
        # relacionado
        'type_program_id': fields.many2one('type.program', 'Call', select=1),
        # Campo para saber el proyecto con que línea de investigación esta
        # relacionado
        'project_research_line_id':
            fields.many2one('project.research.line', 'Project Line', select=1),
        # Campo para saber el proyecto con que línea de investigación esta
        # relacionado
        'project_research_subline_id':
            fields.many2one('project.research.subline', 'Project Subline',
                            select=1),
        # Campo para saber el proyecto con que sublínea de investigación esta
        # relacionado
        'project_research_subline_id':
            fields.many2one('project.research.subline', 'Project Subline',
                            select=1),
        # Campo para saber el proyecto con que pirámide de ensayo esta
        # relacionado
        'project_pyramid_test_id':
            fields.many2one('project.pyramid.test', 'Pyramid Test', select=1),
        # Campo para saber el proyecto con que programa aeronautico esta
        # relacionado
        'project_aeronautical_program_id':
            fields.many2one('project.aeronautical.program',
                            'Aeronautical Program', select=1, invisible=True),
        # Campo para saber la ubicación del proyecto
        'project_location_id':
            fields.many2one('project.location', 'Project Location', select=1),
        # Campo para saber el/los proyectos, con que producto/s esta/n
        # relacionado/s
        'product_ids':
            fields.many2many('product.product', 'project_product_rel',
                             'product_id', 'proyect_id', 'Produts'),
        # Campo para saber el/los proyectos, con que publicacion/es esta/n
        # relacionado/s
        'publication_ids':
            fields.many2many('project.publication', 'project_publication_rel',
                             'publication_id', 'proyect_id', 'Publications'),
        'resume': fields.text('Resume'),
        'sector_id': fields.many2one('sector', 'Sector', select=1),
        # Campo para saber el Año del proyecto
        'project_year': fields.integer('Project Year'),
    }
