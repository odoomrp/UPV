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
import datetime


class HistoricalExtension(orm.Model):

    _name = 'historical.extension'
    _description = 'historical.extension'

    _columns = {
        # Fecha de solicitud
        'request_date': fields.date('Request Date', readonly=True),
        # Fecha de concesion
        'grant_date': fields.date('Grant Date', readonly=True),
        # motivo de la prorroga
        'extension_reason': fields.text('Extension Reason', readonly=True),
        # fuente de financiacion
        'financing_source':
            fields.many2one('financing.source', 'Financing Source',
                            readonly=True),
        # Estado
        'state':
            fields.selection([('draft', 'Draft'),
                              ('in_progress', 'In Progress'),
                              ('granted', 'Granted'),
                              ('rejected', 'Rejected'),
                              ('completed', 'Completed')], 'State',
                             readonly=True),
       # Fecha de eligibilidad desde                     
        'eligibility_date_from': fields.date('Eligibility date from',
                                             readonly=True),
       # Fecha de eligibilidad hasta 
        'eligibility_date_to': fields.date('Eligibility date to',
                                           readonly=True),
         # Solicitud
        'historical_extension_id':
            fields.many2one('financing.source', 'Extension',
                            ondelete="cascade", readonly=True),
       # nueva Fecha de eligibilidad hasta 
        'eligibility_date_to_extension':
            fields.date('Eligibility date to extension', readonly=True)
    }
