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
    "name": "OngLibre Financial Source",
    "version": "1.0",
    "author": "Radmas Technologies S.L. & AvanzOSC S.L",
    "category": "Custom Modules",
    "website": "www.avanzosc.es",
    "description": """
    """,
    "depends": ['base', 'onglibre_project_financer', 'product'],
    'data': ['wizard/transfer_fund_view.xml',
             'data/justification_date_workflow.xml',
             'views/financing_source.xml',
             'views/expense_area.xml',
             'views/justification_date.xml',
             'views/legal_support.xml',
             'views/res_partner_view.xml',
             'views/right_recognition.xml',
             'views/account_analytic_account_ext_view.xml',
             'views/account_analytic_line_ext_view.xml',
             'views/project_project_ext_view.xml',
             'views/project_financing_view.xml',
             'views/code_call_view.xml',
             'views/financier_fund_view.xml',
             'views/financing_type.xml',
             'views/historical_extension_view.xml',
             'views/transfer_fund_view.xml'
             ],
    'installable': True,
}
