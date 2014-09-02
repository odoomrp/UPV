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
    "name": "Avanzosc Calendar",
    "version": "1.0",
    "author": "AvanzOSC S.L",
    "category": "Custom Modules",
    "website": "www.avanzosc.es",
    "description": """
        Avanzosc Custom Modules, to generate schedules for employees
    """,
    "depends": ['base', 'hr'
                ],
    'data': ['wizard/generate_holiday_view.xml',
             'wizard/import_template_view.xml',
             'wizard/make_hours_to_work_view.xml',
             'wizard/import_template_employes_view.xml',
             'wizard/import_template_employes_line_view.xml',
             'wizard/make_hours_to_work_employes_view.xml',
             'wizard/make_hours_to_work_employes_line_view.xml',
             'wizard/show_calendar_pdf_view.xml',
             'views/festive_template_view.xml',
             'views/festive_template_line_view.xml',
             'views/hr_employee_ext_view.xml',
             'views/hr_employee_calendar_view.xml',
             ],
    'installable': True,
}
