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


class FinancingSource(orm.Model):
    _inherit = 'financing.source'

    _columns = {
        # Líneas de Analítica asociadas a la fuente de financiación
        'account_analytic_line_ids':
            fields.one2many('account.analytic.line', 'financing_source_id',
                            'Analytic Lines',
                            domain=[('type', 'not in',
                                     ('budgetary', 'financing_source'))]),
    }
