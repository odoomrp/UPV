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


class CrmStrategy(orm.Model):
    _inherit = ['mail.thread']

    def _get_campaign_num(self, cr, uid, ids, name, args, context=None):
        res = {}
        for strategy in self.browse(cr, uid, ids, context=context):
            c_len = 0
            if strategy.campaign_ids:
                c_len = len(strategy.campaign_ids)
            res[strategy.id] = c_len
        return res

    _columns = {
        # Campo para el nombre de la estrategia
        'name': fields.char('Name', size=64, required="True", select=1),
        # Campo para saber que campañas estan asociadas a la estrategia
        'campaign_num':
            fields.function(_get_campaign_num, method=True, type='integer',
                            string="Num camp", store=True),
        'campaign_ids':
            fields.one2many('crm.tracking.campaign', 'strategy_id',
                            'Campaigns', select=1),
        'date_create': fields.date('Create Date'),
        'active': fields.boolean('Active'),
        'message_ids':
            fields.one2many('mail.message', 'res_id', 'Messages',
                            domain=[('model', '=', 'mail.thread')]),
    }

    _defaults = {'date_create': fields.date.context_today,
                 'active': lambda *a: 1
                 }
