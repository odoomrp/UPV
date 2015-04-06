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
{
    "name": "OngLIbre Budgetary",
    "version": "1.0",
    "author": "Radmas Technologies S.L. & AvanzOSC S.L",
    "category": "Custom Modules",
    "website": "www.avanzosc.es",
    "description": """
        Avanzosc Custom Modules
    """,
    "depends": [
        'base',
        'product',
        'costs_simulator',
        'costs_simulator_purchase_types',
        'crm',
        'project',
        'hr',
        'sale',
        'account',
        'avanzosc_employee_learning',
        'avanzosc_calendar',
        'hr_contract',
        'onglibre_financial_source',
        'analytic',
        'onglibre_project_financer',
        'purchase_type',
    ],
    'data': [
        'data/simulation_cost_workflow_ext.xml',
        'data/purchase_types_workflow.xml',
        'data/res_partner_workflow.xml',
        'wizard/simulation_select_template_view.xml',
        'wizard/estrategy_add_note_view.xml',
        'views/project_activity_view.xml',
        'views/project_type_view.xml',
        'views/subsector_view.xml',
        'views/administration_view.xml',
        'views/type_program_view.xml',
        'views/project_location_view.xml',
        'views/crm_strategy_view.xml',
        'views/crm_tracking_campaign_ext_view.xml',
        'views/crm_lead_ext_view.xml',
        'views/res_partner_view.xml',
        'views/project_project_view.xml',
        'views/project_subactivity_view.xml',
        'views/project_research_line_view.xml',
        'views/project_research_subline_view.xml',
        'views/project_pyramid_test_view.xml',
        'views/project_aeronautical_program_view.xml',
        'views/project_publication_type_view.xml',
        'views/project_publication_view.xml',
        'views/simulation_cost_ext_view.xml',
        'views/simulation_cost_line_ext_view.xml',
        'views/simulation_template_line_view.xml',
        'views/account_invoice_ext_view.xml',
        'views/purchase_order_line_view.xml',
        'views/sector_view.xml',
        'views/simulation_template_view_ext.xml',
        # views/project_task_type_view.xml',
        'views/project_justification_view.xml',
        'views/hr_employee_ext_view.xml',
        'views/hr_contract_ext_view.xml',
        'views/project_financing_ext_view.xml',
        'views/sale_order_line_view_ext.xml',
        'views/account_analytic_line_ext_view.xml',
        'views/expense_area_ext_view.xml',
        'views/simulation_category_view.xml',
        'views/simulation_template_category_view.xml',
        'views/financing_source_ext_view.xml',
    ],
    'installable': True,
}
