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


class CrmTrackingCampaign(orm.Model):
    _inherit = ['crm.tracking.campaign']

    _columns = {
        # Campo para saber la campaña a que estrategia pertenece
        'strategy_id': fields.many2one('mail.thread', 'Strategy', select=1),
        # Campo para saber que iniciativas estan relacionadas con la campaña
        'crm_iniciatives_ids':
            fields.one2many('crm.lead', 'campaign_id', 'Iniciatives',
                            domain=[('type', '=', 'lead')]),
        # Campo para saber que iniciativas estan relacionadas con la campaña
        'crm_opportunities_ids':
            fields.one2many('crm.lead', 'campaign_id', 'Opportunities',
                            domain=[('type', '=', 'opportunity')]),
        'date_create': fields.date('Create Date'),
        'active': fields.boolean('Active'),
        'message_ids':
            fields.one2many('mail.message', 'res_id', 'Messages',
                            domain=[('model', '=', 'crm.tracking.campaign')]),
    }

    _defaults = {'date_create': fields.date.context_today,
                 'active': lambda *a: 1
                 }

    def unlink(self, cr, uid, ids, context=None):
        lead_list = False
        res = {}
        for case in self.browse(cr, uid, ids, context):
            if (len(case.crm_iniciatives_ids) > 0 or
                    len(case.crm_opportunities_ids) > 0):
                lead_list = True
        if lead_list:
            res = {}
        else:
            res = super(CrmCaseResourceType, self).unlink(cr, uid, ids,
                                                          context)
        return res
