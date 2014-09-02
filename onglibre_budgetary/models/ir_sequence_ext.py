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
from openerp.osv import orm
import openerp


class IrSequence(orm.Model):

    _inherit = 'ir.sequence'

    def _code_get2(self, cr, uid, context=None):
        if 'type_code' not in context:
            cr.execute('select code, name from ir_sequence_type')
        else:
            cr.execute("select code, name from ir_sequence_type where code = "
                       "'sale.order'")
        return cr.fetchall()

    _columns = {'code': openerp.osv.fields.selection(_code_get2, 'Code',
                                                     size=64),
                }
