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
    "name": "OngLibre Project Financer",
    "version": "1.0",
    "author": "Radmas Technologies S.L. & AvanzOSC S.L",
    "category": "Custom Modules",
    "website": "www.avanzosc.es",
    "description": """
    """,
    "depends": ['base', 'account', 'analytic', 'project', 'costs_simulator',
                'hr_timesheet_invoice'],
    'data': [
        'views/project_type_view.xml',
        'views/project_center_view.xml',
        'views/project_ambit_view.xml',
        'views/project_role_view.xml',
        'views/account_analytic_account_ext_view.xml',
        'views/project_project_view.xml',
        'views/account_analytic_line_ext_view.xml',
        'views/users_role_view.xml',
        'views/account_analytic_char_ext_view.xml',
    ],
    'installable': True,
}
