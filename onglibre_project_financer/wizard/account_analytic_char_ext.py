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


class AccountAnalyticChart(orm.TransientModel):
    _inherit = 'account.analytic.chart'

    _columns = {
        # Proyecto
        'project_id': fields.many2one('project.project', 'Project'),
        'father_id': fields.many2one('account.analytic.account', 'Father'),
        'check_father': fields.boolean('Check'),
        'grandfather_id': fields.many2one('account.analytic.account',
                                          'Grandfather'),
        'check_grandfather': fields.boolean('Check'),
        }

    def default_get(self, cr, uid, fields, context=None):
        project_obj = self.pool['project.project']
        res = {}
        if 'my_project_id' in context:
            project = project_obj.browse(cr, uid, context.get('my_project_id'),
                                         context)
            if not project.parent_project_id:
                res = {'project_id': context.get('my_project_id'),
                       'father_id': False,
                       'check_father': False,
                       'grandfather_id': False,
                       'check_grandfather': False,
                       }
            else:
                project = project_obj.browse(
                    cr, uid, project.parent_project_id.id, context)
                if not project.parent_project_id:
                    res = {'project_id': context.get('my_project_id'),
                           'father_id': project.analytic_account_id.id,
                           'check_father': False,
                           'grandfather_id': False,
                           'check_grandfather': False,
                           }
                else:
                    pproject = project.parent_project_id
                    res = {'project_id': context.get('my_project_id'),
                           'father_id': project.analytic_account_id.id,
                           'check_father': False,
                           'grandfather_id': pproject.analytic_account_id.id,
                           'check_grandfather': False,
                           }

        return res

    def onchange_project_id(self, cr, uid, ids, project_id, context=None):
        project_obj = self.pool['project.project']
        res = {}
        if not project_id:
            res = {'father_id': False,
                   'check_father': False,
                   'grandfather_id': False,
                   'check_grandfather': False,
                   }
        else:
            project = project_obj.browse(cr, uid, project_id, context)
            if not project.parent_project_id:
                res = {'father_id': False,
                       'check_father': False,
                       'grandfather_id': False,
                       'check_grandfather': False,
                       }
            else:
                project = project_obj.browse(
                    cr, uid, project.parent_project_id.id, context)
                if not project.parent_project_id:
                    res = {'father_id': project.analytic_account_id.id,
                           'check_father': False,
                           'grandfather_id': False,
                           'check_grandfather': False,
                           }
                else:
                    pproject = project.parent_project_id
                    res = {'father_id': project.analytic_account_id.id,
                           'check_father': False,
                           'grandfather_id': pproject.analytic_account_id.id,
                           'check_grandfather': False,
                           }
        return {'value': res}

    def onchange_check_father(self, cr, uid, ids, check_father,
                              check_grandfather, context=None):
        data = {}
        result = {}
        if check_father and check_grandfather:
            data = {'check_father': False}
            result = {'value': data}
            result.update({'warning': {'title': 'warning', 'message': 'You '
                                       'can not check 2 checks'}})
        return result

    def onchange_check_grandfather(self, cr, uid, ids, check_father,
                                   check_grandfather, context=None):
        data = {}
        result = {}
        if check_father and check_grandfather:
            data = {'check_grandfather': False}
            result = {'value': data}
            result.update({'warning': {'title': 'warning', 'message': 'You '
                                       'can not check 2 checks'}})
        return result

    def analytic_account_chart_open_window(self, cr, uid, ids, context=None):
        mod_obj = self.pool['ir.model.data']
        act_obj = self.pool['ir.actions.act_window']
        result_context = {}
        if context is None:
            context = {}
        result = mod_obj.get_object_reference(
            cr, uid, 'account', 'action_account_analytic_account_tree2')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        data = self.browse(cr, uid, ids[0], context)
        if data.from_date:
            result_context.update({'from_date': data.from_date})
        if data.to_date:
            result_context.update({'to_date': data.to_date})
        if data.check_father:
            result_context.update({'my_analytic_account_id':
                                   data.father_id.id})
            result['domain'] = [('id', '=', data.father_id.id)]
        if data.check_grandfather:
            result_context.update({'my_analytic_account_id':
                                   data.grandfather_id.id})
            result['domain'] = [('id', '=', data.grandfather_id.id)]

        result['context'] = str(result_context)
        return result
