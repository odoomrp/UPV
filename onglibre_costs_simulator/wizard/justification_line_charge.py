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
from openerp.osv import fields, orm


class StartParJust(orm.TransientModel):
    _name = 'start.par.just'

    _columns = {
        'inv_date_from': fields.date('Invoice Date'),
        'inv_date_to': fields.date('Invoice Date'),
        'project_id': fields.many2one('project.project', 'Project'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'purchase_type': fields.many2one('purchase.type', 'Purchase Type'),
        'name': fields.char('Concept', size=64),
        'price_subtotal_from': fields.float('Subtotal', digits=(10, 3)),
        'price_subtotal_to': fields.float('Subtotal', digits=(10, 3)),
    }

    def fill_fields(self, cr, uid, ids, context):
        empty_search = True
        if 'purchase_type' in context:
            if context.get('purchase_type'):
                empty_search = False
        if 'inv_date_from' in context:
            if context.get('inv_date_from'):
                empty_search = False
        if 'inv_date_to' in context:
            if context.get('inv_date_to'):
                empty_search = False
        if 'project_id' in context:
            if context.get('project_id'):
                empty_search = False
        if 'partner_id' in context:
            if context.get('partner_id'):
                empty_search = False
        if 'name' in context:
            if context.get('name'):
                empty_search = False
        if 'price_subtotal_from' in context:
            if context.get('price_subtotal_from'):
                empty_search = False
        if 'price_subtotal_to' in context:
            if context.get('price_subtotal_to'):
                empty_search = False
        context.update({'empty_search': empty_search})
        res = {
            'type': 'ir.actions.act_window',
            'res_model': 'par.just',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': context
            }
        return res


class ParJust(orm.TransientModel):
    _name = 'par.just'

    def _get_total_import(self, cr, uid, ids, name, args, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            sum = 0.0
            for line in obj.invoice_line_ids:
                if line.check_justification:
                    sum = sum + line.to_justified_import
            res[obj.id] = sum
        return res

    _columns = {
        'inv_date_from': fields.date('Invoice Date'),
        'inv_date_to': fields.date('Invoice Date'),
        'project_id': fields.many2one('project.project', 'Project'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'purchase_type': fields.many2one('purchase.type', 'Purchase Type'),
        'name': fields.char('Concept', size=64),
        'price_subtotal_from': fields.float('Subtotal', digits=(10, 3)),
        'price_subtotal_to': fields.float('Subtotal', digits=(10, 3)),
        'total_to_import':
            fields.function(_get_total_import, method=True, type='float',
                            digits=(10, 3), store=False,
                            string="Total to import"),
        'invoice_line_ids': fields.one2many('account.invoice.line.wiz',
                                            'wiz_id', 'Invoice Lines')
    }

    def onchange_lines(self, cr, uid, ids, lines, context=None):
        sum = 0.0
        for line in lines:
            if line[2]['check_justification']:
                sum = sum + line[2]['to_justified_import']
        return {'value': {'total_to_import': sum}}

    def browse2dict(self, cr, uid, list, context):
        dict = []
        for reg in list:
            val = {
                "purchase_type": reg.purchase_type.id or False,
                "invoice_type": reg.invoice_type,
                "account_analytic_id": reg.account_analytic_id.id,
                'project_id': reg.project_id,
                "partner_id": reg.partner_id.id,
                "vat": reg.vat,
                "invoice_id": reg.invoice_id.id,
                "price_subtotal": reg.price_subtotal,
                "inv_date": reg.inv_date,
                "last_pay_date": reg.last_pay_date,
                "paid_import": reg.paid_import,
                "move_id": reg.move_id.id,
                "justified_percent": reg.justified_percent,
                "justified_import": reg.justified_import,
                "project_text_list": reg.project_text_list,
                "to_justified_import": 0.0,
                "to_justified_percent": 0.0,
                "check_justification": False,
                "invoice_line_id": reg.id,
                "account_id": reg.account_id.id,
                "name": reg.name
                }
            dict.append(val)
        return dict

    def default_get(self, cr, uid, fields, context=None):
        project_justification_obj = self.pool['project.justification']
        project_obj = self.pool['project.project']
        account_obj = self.pool['account.analytic.account']
        invoice_line_obj = self.pool['account.invoice.line']
        values = {}
        domain = []
        just_id = context.get('active_id')
        just_o = project_justification_obj.browse(cr, uid, just_id, context)
        line_list = []
        for line in just_o.justification_line_ids:
            line_list.append(line.id)
        val = ('id', 'not in', line_list)
        domain.append(val)
        val = ('state', 'not in', ('draft', 'cancel'))
        domain.append(val)
        if 'purchase_type' in context:
            if context.get('purchase_type'):
                val = ('purchase_type', 'in', [context.get('purchase_type')])
                values.update({'purchase_type': context.get('purchase_type')})
                domain.append(val)
        if 'inv_date_from' in context:
            if context.get('inv_date_from'):
                val = ('inv_date', '>=', context.get('inv_date_from'))
                values.update({'inv_date_from': context.get('inv_date_from')})
                domain.append(val)
        if 'inv_date_to' in context:
            if context.get('inv_date_to'):
                val = ('inv_date', '<=', context.get('inv_date_to'))
                values.update({'inv_date_to': context.get('inv_date_to')})
                domain.append(val)
        if 'project_id' in context:
            if context.get('project_id'):
                project = project_obj.browse(
                    cr, uid, context.get('project_id'), context)
                analytic_ids = account_obj.search(
                    cr, uid, [('name', 'like', project.name)], context)
                val = ('account_analytic_id', 'in', analytic_ids)
                values.update({'project_id': context.get('project_id')})
                domain.append(val)
        if 'partner_id' in context:
            if context.get('partner_id'):
                val = ('partner_id', 'in', [context.get('partner_id')])
                values.update({'partner_id': context.get('partner_id')})
                domain.append(val)
        if 'name' in context:
            if context.get('name'):
                val = ('name', 'like', context.get('name'))
                values.update({'name': context.get('name')})
                domain.append(val)
        if 'price_subtotal_from' in context:
            if context.get('price_subtotal_from'):
                val = ('price_subtotal', '>=',
                       context.get('price_subtotal_from'))
                values.update({'price_subtotal_from':
                               context.get('price_subtotal_from')})
                domain.append(val)
        if 'price_subtotal_to' in context:
            if context.get('price_subtotal_to'):
                val = ('price_subtotal', '<=',
                       context.get('price_subtotal_to'))
                values.update({'price_subtotal_to':
                               context.get('price_subtotal_to')})
                domain.append(val)
        if 'empty_search' in context:
            if context.get('empty_search'):
                values.update({'invoice_line_ids': {}})
                return values
        invoice_line_ids = invoice_line_obj.search(cr, uid, domain, context)
        if invoice_line_ids:
            invoice_lines = invoice_line_obj.browse(cr, uid, invoice_line_ids,
                                                    context)
            dict = self.browse2dict(cr, uid, invoice_lines, context)
            values.update({'invoice_line_ids': dict})
        return values

    def select_lines(self, cr, uid, ids, context):
        project_justification_obj = self.pool['project.justification']
        invoice_line_obj = self.pool['account.invoice.line']
        just_id = context.get('active_id')
        just_list_o = project_justification_obj.browse(
            cr, uid, just_id, context).justification_line_ids
        just_list = []
        for just_o in just_list_o:
            just_list.append(just_o.id)
        for line in self.browse(cr, uid, ids[0], context).invoice_line_ids:
            if line.check_justification:
                vals = {'to_justified_import': line.to_justified_import,
                        'to_justified_percent': line.to_justified_percent}
                invoice_line_obj.write(
                    cr, uid, [line.invoice_line_id.id], vals, context)
                just_list.append(line.invoice_line_id.id)
        vals = {'justification_line_ids': [(6, 0, just_list)]}
        project_justification_obj.write(cr, uid, [just_id], vals, context)
        return {'type': 'ir.actions.act_close_window'}

    def fill_fields(self, cr, uid, ids, context):
        context.update({'empty_search': False})
        res = {
            'type': 'ir.actions.act_window',
            'res_model': 'par.just',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': context
            }
        return res


class AccountInvoiceLineWiz(orm.TransientModel):
    _inherit = 'account.invoice.line'
    _name = 'account.invoice.line.wiz'

    _columns = {
        'wiz_id': fields.many2one('par.just', 'Wizard'),
        'invoice_line_id': fields.many2one('account.invoice.line',
                                           'Invoice Line'),
        'check_justification': fields.boolean('Chose')
    }
