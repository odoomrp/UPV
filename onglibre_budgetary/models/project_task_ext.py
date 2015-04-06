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
from openerp import tools


class ProjectTask(orm.Model):
    _inherit = 'project.task'

    _columns = {
        'account_analytic_account_id':
            fields.many2one('account.analytic.account', 'Account'),
    }

    def write(self, cr, uid, ids, vals, context=None):
        timesheet_obj = self.pool['hr.analytic.timesheet']
        if context is None:
            context = {}
        if 'project_id' in vals or 'name' in vals:
            vals_line = {}
            task_obj_l = self.browse(cr, uid, ids, context=context)
            for task_obj in task_obj_l:
                acc_id = task_obj.phase_id.account_analytic_account_id.id
                if len(task_obj.work_ids):
                    for task_work in task_obj.work_ids:
                        if not task_work.hr_analytic_timesheet_id:
                            continue
                        line_id = task_work.hr_analytic_timesheet_id.id
                        if 'project_id' in vals:
                            vals_line['account_id'] = acc_id
                        if 'name' in vals:
                            n = '%s: %s' % (tools.ustr(vals['name']),
                                            tools.ustr(task_work.name) or '/')
                            vals_line['name'] = n
                        timesheet_obj.write(cr, uid, [line_id], vals_line,
                                            context)
        return super(orm.osv, self).write(cr, uid, ids, vals, context)
