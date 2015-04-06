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


class RightRecognition(orm.Model):

    _name = 'right.recognition'
    _description = 'Right Recognition'
    _rec_name = 'date'

    _columns = {
        # Fecha de reconocimiento de derecho
        'date': fields.date('Date', required=True),
        # Importe de reconocimiento de derecho
        'amount': fields.float('Amount', digits=(2, 1)),
        # FActura
        'invoice': fields.boolean('Invoice'),
        # Fuente de Financiación
        'financing_source_id': fields.many2one('financing.source',
                                               'Financing Source')
    }
