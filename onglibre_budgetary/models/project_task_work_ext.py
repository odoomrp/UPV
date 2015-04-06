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
from openerp import tools


class ProjectTaskWork(orm.Model):

    _inherit = 'project.task.work'

    def create(self, cr, uid, vals, *args, **kwargs):
        obj_timesheet = self.pool['hr.analytic.timesheet']
        task_obj = self.pool['project.task']
        uom_obj = self.pool['product.uom']
        user_obj = self.pool['res.users']
        vals_line = {}
        context = kwargs.get('context', {})
        if 'hours' in vals and (not vals['hours']):
            vals['hours'] = 0.00
        if 'task_id' in vals:
            cr.execute('update project_task set remaining_hours='
                       'remaining_hours - %s where id=%s',
                       (vals.get('hours', 0.0), vals['task_id']))
        if 'no_analytic_entry' not in context:
            obj_task = task_obj.browse(cr, uid, vals['task_id'], context)
            result = self.get_user_related_details(
                cr, uid, vals.get('user_id', uid))
            vals_line['name'] = '%s: %s' % (tools.ustr(obj_task.name),
                                            tools.ustr(vals['name']) or '/')
            vals_line['user_id'] = vals['user_id']
            vals_line['product_id'] = result['product_id']
            vals_line['date'] = vals['date'][:10]
            # calculate quantity based on employee's product's uom
            vals_line['unit_amount'] = vals['hours']
            default_uom = user_obj.browse(
                cr, uid, uid, context).company_id.project_time_mode_id.id
            if result['product_uom_id'] != default_uom:
                vals_line['unit_amount'] = uom_obj._compute_qty(
                    cr, uid, default_uom, vals['hours'],
                    result['product_uom_id'])
            if obj_task.account_analytic_account_id:
                acc_id = (obj_task.project_id and
                          obj_task.account_analytic_account_id.id or False)
            else:
                acc_id = (obj_task.project_id and
                          obj_task.project_id.analytic_account_id.id or False)
            if acc_id:
                vals_line['account_id'] = acc_id
                res = obj_timesheet.on_change_account_id(
                    cr, uid, False, acc_id)
                if res.get('value'):
                    vals_line.update(res['value'])
                vals_line['general_account_id'] = result['general_account_id']
                vals_line['journal_id'] = result['journal_id']
                vals_line['amount'] = 0.0
                vals_line['product_uom_id'] = result['product_uom_id']
                amount = vals_line['unit_amount']
                prod_id = vals_line['product_id']
                unit = False
                timeline_id = obj_timesheet.create(
                    cr, uid, vals=vals_line, context=context)
                # Compute based on pricetype
                amount_unit = obj_timesheet.on_change_unit_amount(
                    cr, uid, timeline_id, prod_id, amount, False, unit,
                    vals_line['journal_id'], context=context)
                if amount_unit and 'amount' in amount_unit.get('value', {}):
                    updv = {'amount': amount_unit['value']['amount']}
                    obj_timesheet.write(
                        cr, uid, [timeline_id], updv, context=context)
                vals['hr_analytic_timesheet_id'] = timeline_id
        return super(orm.osv, self).create(cr, uid, vals, *args, **kwargs)
