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
# from mail.mail_message import truncate_text


class CrmAddNote(orm.TransientModel):
    _name = 'strategy.add.note'
    _description = "Add Internal Note"
    _columns = {
        'body': fields.text('Note Body', required=True),
    }

    def action_add(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if 'model' in context:
            model = context['model']
            case_pool = self.pool.get(model)
            for obj in self.browse(cr, uid, ids, context=context):
                case_list = case_pool.browse(cr, uid, context['active_ids'],
                                             context=context)
                case = case_list[0]
#                case_pool.message_append(cr, uid, [case],
#                                         truncate_text(obj.body),
#                                         body_text=obj.body)
        return {'type': 'ir.actions.act_window_close'}
