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
    "name": "Costs Simulator",
    "version": "1.0",
    "author": "AvanzOSC",
    "category": "Custom Modules",
    "website": "www.avanzosc.es",
    "description": """
        You need install costs_simulator_purchase_types.
        Avanzosc Custom Modules
    """,
    "depends": [
        'product',
        'sale',
        'purchase',
        'project',
        'analytic',
        'account',
        'hr_expense',
        'purchase_requisition_ext',
        'sale_service',
        'purchase_type',
    ],
    'data': [
        'data/workflow.xml',
        'security/costs_simulator.xml',
        'security/ir.model.access.csv',
        'wizard/simulation_select_template_view.xml',
        'wizard/wiz_confirm_create_sale_order_view.xml',
        'views/product_product_ext_view.xml',
        'views/simulation_template_view.xml',
        'views/simulation_template_line_view.xml',
        'views/simulation_cost_view.xml',
        'views/simulation_cost_line_view.xml',
        'views/sale_order_ext_view.xml',
        'views/purchase_order_view_ext.xml',
        'views/project_task_ext_view.xml',
        'views/project_project_ext_view.xml',
        'views/account_analytic_account_ext_view.xml',
    ],
    'installable': True,
}
