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


class CrmLead(orm.Model):
    _inherit = 'crm.lead'

    _columns = {
        # Campo para relacionar la iniciativa/oportunidad con Campañas
        'campaign_id': fields.many2one('crm.tracking.campaign', 'Campaign'),
        # 1 Oportunidad puede tener N simulaciones de coste
        'simulation_cost_ids':
            fields.one2many('simulation.cost', 'crm_opportunity_id',
                            'Campaigns', select=1),
        'launch_date': fields.date('Launch Date'),
        'zip': fields.char('Zip', change_default=True, size=24),
        'mobile': fields.char('Mobile', size=64),
    }

    def onchange_partner_id(self, cr, uid, ids, partner_id, email_from,
                            context=None):
        partner_obj = self.pool['res.partner']
        res = {}
        if partner_id:
            partner_o = partner_obj.browse(cr, uid, partner_id, context)
            res.update({'partner_name': partner_o.name})
            addr = partner_obj.address_get(cr, uid, [partner_id], ['contact'])
            res.update({'partner_address_id': addr['contact']})
            res.update(self.onchange_partner_address_id(
                cr, uid, ids, addr['contact'], context)['value'])
        return{'value': res}

    def onchange_partner_address_id(self, cr, uid, ids, partner_address_id,
                                    email_from, context=None):
        partner_address_obj = self.pool['res.partner']
        value = super(CrmLead, self).onchange_partner_address_id(
            cr, uid, ids, partner_address_id, email_from)
        res = value['value']
        if partner_address_id:
            address_o = partner_address_obj.browse(
                cr, uid, partner_address_id, context=context)
            res.update({'fax': address_o.fax,
                        'mobile': address_o.mobile,
                        'city': address_o.city,
                        'zip': address_o.zip,
                        'street2': address_o.street2,
                        'street': address_o.street,
                        'function': address_o.function,
                        'title': address_o.title.id})
            if address_o.contact_id:
                contact_o = address_o.contact_id
                res.update({'contact_name': (contact_o.last_name + ', ' +
                                             contact_o.first_name)})
        return{'value': res}

    def convert_oppor(self, cr, uid, ids, context=None):
        nodes = True
        if 'active_model' in context:
            if context['active_model'] != 'ir.ui.menu':
                nodes = False
        else:
            nodes = False
        context.update({'active_ids': ids,
                        'active_id': ids[0],
                        'active_model': 'crm.lead'})
        res = {'type': 'ir.actions.act_window',
               'res_model': 'crm.lead2opportunity.partner',
               'view_type': 'form',
               'view_mode': 'form',
               'target': 'new',
               'nodestroy': nodes,
               'context': context
               }
        return res

    def _lead_create_partner_address(self, cr, uid, lead, partner_id,
                                     context=None):
        contact_obj = self.pool['res.partner.title']
        address_obj = self.pool['res.partner']
        if lead.contact_name:
            vals = {'last_name': lead.contact_name}
            contact_id = contact_obj.create(cr, uid, vals, context=context)
            vals = {'partner_id': partner_id,
                    'name': lead.contact_name,
                    'phone': lead.phone,
                    'mobile': lead.mobile,
                    'email': lead.email_from and (lead.email_from)[0],
                    'fax': lead.fax,
                    'title': lead.title and lead.title.id or False,
                    'function': lead.function,
                    'street': lead.street,
                    'street2': lead.street2,
                    'zip': lead.zip,
                    'city': lead.city,
                    'country_id': (lead.country_id and lead.country_id.id or
                                   False),
                    'state_id': lead.state_id and lead.state_id.id or False,
                    'contact_id': contact_id,
                    'title': lead.title.id,
                    'function': lead.function,
                    }
            address_id = address_obj.create(cr, uid, vals, context=context)
        else:
            vals = {'partner_id': partner_id,
                    'name': lead.contact_name,
                    'phone': lead.phone,
                    'mobile': lead.mobile,
                    'email': lead.email_from and (lead.email_from)[0],
                    'fax': lead.fax,
                    'title': lead.title and lead.title.id or False,
                    'function': lead.function,
                    'street': lead.street,
                    'street2': lead.street2,
                    'zip': lead.zip,
                    'city': lead.city,
                    'country_id': (lead.country_id and lead.country_id.id or
                                   False),
                    'state_id': lead.state_id and lead.state_id.id or False,
                    }
            address_id = address_obj.create(cr, uid, vals, context=context)
        return address_id
