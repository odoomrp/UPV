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
    "name": "Costs Simulator Purchase Types",
    "version": "1.0",
    "author": "AvanzOSC",
    "category": "Custom Modules",
    "website": "www.avanzosc.es",
    "description": """
        Avanzosc Custom Modules.
        This module creates the type of purchase order: "OTHERS". 
        This module must be installed for the "Cost Simulator".
    """,
    "depends": ['purchase_type', ],
    'data': ['data/purchase_types.xml',
             ],
    'installable': True,
}
