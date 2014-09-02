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
from openerp.addons import decimal_precision as dp


class ProjectProject(orm.Model):

    _inherit = 'project.project'

    def _get_parent(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for project_o in self.browse(cr, uid, ids, context):
            p_id = False
            cond = [('analytic_account_id', '=',
                     project_o.analytic_account_id.parent_id.id)]
            project_list = self.search(cr, uid, cond, context=context)
            if project_list:
                p_id = project_list[0]
            res[project_o.id] = p_id
        return res

    def _get_analytic_account(self, cr, uid, ids, field_name, arg,
                              context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = (rec.analytic_account_id.id)
        return result

    def _calc_sum_expense_budget(self, cr, uid, ids, field_name, arg,
                                 context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        result = {}
        if ids:
            for rec in self.browse(cr, uid, ids, context=context):
                w_imp = 0
                cond = [('account_id', '=', rec.analytic_account_id.id),
                        ('project_id', '=', rec.id),
                        ('type', '=', 'budgetary'), ]
                account_analytic_line_ids = analytic_line_obj.search(
                    cr, uid, cond, context=context)
                for analytic_line in analytic_line_obj.browse(
                        cr, uid, account_analytic_line_ids, context):
                    w_imp = w_imp + analytic_line.sum_expense_budget
                result[rec.id] = w_imp
        return result

    def _calc_sum_remainder(self, cr, uid, ids, field_name, arg, context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        result = {}
        if ids:
            for rec in self.browse(cr, uid, ids, context=context):
                w_imp = 0
                cond = [('account_id', '=', rec.analytic_account_id.id),
                        ('project_id', '=', rec.id),
                        ('type', '=', 'budgetary'), ]
                account_analytic_line_ids = analytic_line_obj.search(
                    cr, uid, cond, context=context)
                for analytic_line in analytic_line_obj.browse(
                        cr, uid, account_analytic_line_ids, context):
                    w_imp = w_imp + analytic_line.sum_remainder
                result[rec.id] = w_imp
        return result

    def _calc_sum_updated_expense_budget(self, cr, uid, ids, field_name, arg,
                                         context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        result = {}
        if ids:
            for rec in self.browse(cr, uid, ids, context=context):
                w_expense_budget = 0
                cond = [('account_id', '=', rec.analytic_account_id.id),
                        ('project_id', '=', rec.id),
                        ('type', '=', 'budgetary'), ]
                account_analytic_line_ids = analytic_line_obj.search(
                    cr, uid, cond, context=context)
                for analytic_line in analytic_line_obj.browse(
                        cr, uid, account_analytic_line_ids, context):
                    w_expense_budget = (w_expense_budget +
                                        analytic_line.sum_expense_budget)
                result[rec.id] = w_expense_budget + rec.sum_remainder
        return result

    def _calc_sum_expense_request(self, cr, uid, ids, field_name, arg,
                                  context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        result = {}
        if ids:
            for rec in self.browse(cr, uid, ids, context=context):
                w_imp = 0
                cond = [('account_id', '=', rec.analytic_account_id.id),
                        ('project_id', '=', rec.id),
                        ('type', '=', 'budgetary'), ]
                account_analytic_line_ids = analytic_line_obj.search(
                    cr, uid, cond, context=context)
                for analytic_line in analytic_line_obj.browse(
                        cr, uid, account_analytic_line_ids, context):
                    w_imp = w_imp + analytic_line.sum_expense_request
                result[rec.id] = w_imp
        return result

    def _calc_sum_expense_compromised(self, cr, uid, ids, field_name, arg,
                                      context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        result = {}
        if ids:
            for rec in self.browse(cr, uid, ids, context=context):
                w_imp = 0
                cond = [('account_id', '=', rec.analytic_account_id.id),
                        ('project_id', '=', rec.id),
                        ('type', '=', 'budgetary'), ]
                account_analytic_line_ids = analytic_line_obj.search(
                    cr, uid, cond, context=context)
                for analytic_line in analytic_line_obj.browse(
                        cr, uid, account_analytic_line_ids, context):
                    w_imp = w_imp + analytic_line.sum_expense_compromised
                result[rec.id] = w_imp
        return result

    def _calc_sum_available_expense(self, cr, uid, ids, field_name, arg,
                                    context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        result = {}
        if ids:
            for rec in self.browse(cr, uid, ids, context=context):
                w_imp = 0
                cond = [('account_id', '=', rec.analytic_account_id.id),
                        ('project_id', '=', rec.id),
                        ('type', '=', 'budgetary'), ]
                account_analytic_line_ids = analytic_line_obj.search(
                    cr, uid, cond, context=context)
                for analytic_line in analytic_line_obj.browse(
                        cr, uid, account_analytic_line_ids, context):
                    w_imp = w_imp + analytic_line.sum_available_expense
                result[rec.id] = w_imp
        return result

    def _calc_sum_real_expense(self, cr, uid, ids, field_name, arg,
                               context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        result = {}
        if ids:
            for rec in self.browse(cr, uid, ids, context=context):
                w_imp = 0
                cond = [('account_id', '=', rec.analytic_account_id.id),
                        ('project_id', '=', rec.id),
                        ('type', '=', 'budgetary'), ]
                account_analytic_line_ids = analytic_line_obj.search(
                    cr, uid, cond, context=context)
                for analytic_line in analytic_line_obj.browse(
                        cr, uid, account_analytic_line_ids, context):
                    w_imp = w_imp + analytic_line.sum_real_expense
                result[rec.id] = w_imp
        return result

    def _calc_sum_paid_expense(self, cr, uid, ids, field_name, arg,
                               context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        result = {}
        if ids:
            for rec in self.browse(cr, uid, ids, context=context):
                w_imp = 0
                cond = [('account_id', '=', rec.analytic_account_id.id),
                        ('project_id', '=', rec.id),
                        ('type', '=', 'budgetary'), ]
                account_analytic_line_ids = analytic_line_obj.search(
                    cr, uid, cond, context=context)
                for analytic_line in analytic_line_obj.browse(
                        cr, uid, account_analytic_line_ids, context):
                    w_imp = w_imp + analytic_line.sum_paid_expense
                result[rec.id] = w_imp
        return result

    def _calc_sum_justified_expense(self, cr, uid, ids, field_name, arg,
                                    context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        result = {}
        if ids:
            for rec in self.browse(cr, uid, ids, context=context):
                w_imp = 0
                cond = [('account_id', '=', rec.analytic_account_id.id),
                        ('project_id', '=', rec.id),
                        ('type', '=', 'budgetary'), ]
                account_analytic_line_ids = analytic_line_obj.search(
                    cr, uid, cond, context=context)
                for analytic_line in analytic_line_obj.browse(
                        cr, uid, account_analytic_line_ids, context):
                    w_imp = w_imp + analytic_line.justified_expense
                result[rec.id] = w_imp
        return result

    _columns = {
        # Campo para mostrar la cuenta analitica del proyecto
        'analytic_account_id2': fields.function(
            _get_analytic_account, type='many2one',
            relation='account.analytic.account', string='Analytic Account'),
        # CAMPOS BASE (TAREA 1.2.A)
        # Código de proyecto
        'project_code': fields.char('Project Code', size=20, required=True),
        # Código de Aplicación
        'application_code': fields.char('Application Code', size=15),
        # Tipo de Aplicación
        'application_type': fields.selection([('gev', 'GEV'),
                                              ('giic', 'GIIC')],
                                             'Application Type'),
        # Restricciones en viajes
        'travel_restrictions': fields.boolean('Travel Restrictions'),
        # Tipo de Proyecto
        'project_type_ids': fields.many2many(
            'project.type', 'project_projectype_rel', 'project_id',
            'project_type_id', 'Project Types'),
        # Localización o Centro
        'project_center_ids': fields.many2many(
            'project.center', 'project_projeccenter_rel', 'project_id',
            'project_center_id', 'Project Centers'),
        # Localización o Centro
        'project_ambit_id': fields.many2one('project.ambit', 'Project Ambit'),
        # Concurrencia competitiva
        'competitive_concurrence': fields.boolean('Competitive Concurrence'),
        # Investigación
        'investigation': fields.boolean('Investigation'),
        # Biotecnología
        'biotechnology': fields.boolean('Biotechnology'),
        # Miembros
        'members': fields.many2many(
            'users.role', 'project_usersrole_rel', 'project_id', 'userrole_id',
            'Project Members',
            help="Project's members are users who can have an access to the "
                 "tasks related to this project.",
            states={'close': [('readonly', True)],
                    'cancelled': [('readonly', True)]}),
        'parent2_id': fields.function(
            _get_parent, method=True, type="many2one",
            relation="project.project", store=True),
        # Proyectos hijos
        # child_project_ids':fields.one2many('project.project','parent2_id',
        # Child Projects', readonly=True),
        # Proyectos hijos-2
        # child_project_ids2':fields.one2many('project.project','parent_id',
        # Child Projects', readonly=True),
        # CAMPOS PARA PESTAÑA DE LINEAS DE ANALITICA
        # Líneas de analítica pertenecientes al proyecto
        'account_analytic_line_ids':
            fields.one2many('account.analytic.line', 'project_id',
                            'Analytic Lines',
                            domain=[('type', '!=', False),
                                    ('type', 'not in', ('budgetary',
                                                        'financing_source'))]),
        # Iva deducible
        'deductible_iva': fields.boolean('Deductible Iva'),
        # Expense budgeet
        'sum_expense_budget':
            fields.function(_calc_sum_expense_budget, string='Expense Budget',
                            type='float',
                            digits_compute=dp.get_precision('Account'),
                            readonly=True, store=True),
        # Remainder
        'sum_remainder':
            fields.function(_calc_sum_remainder, string='Remainder',
                            type='float',
                            digits_compute=dp.get_precision('Account'),
                            readonly=True, store=True),
        # Updated Expense Budget
        'sum_updated_expense_budget':
            fields.function(_calc_sum_updated_expense_budget,
                            string='Updated Expense Budget', type='float',
                            digits_compute=dp.get_precision('Account'),
                            readonly=True, store=True),
        # Expense request
        'sum_expense_request':
            fields.function(_calc_sum_expense_request,
                            string='Expense Request', type='float',
                            digits_compute=dp.get_precision('Account'),
                            readonly=True, store=True),
        # Expense compromised
        'sum_expense_compromised':
            fields.function(_calc_sum_expense_compromised,
                            string='Expense Compromised', type='float',
                            digits_compute=dp.get_precision('Account'),
                            readonly=True, store=True),
        # Available Expense
        'sum_available_expense':
            fields.function(_calc_sum_available_expense,
                            string='Available Expense', type='float',
                            digits_compute=dp.get_precision('Account'),
                            readonly=True, store=True),
        # Real Expense
        'sum_real_expense':
            fields.function(_calc_sum_real_expense, string='Real Expense',
                            type='float',
                            digits_compute=dp.get_precision('Account'),
                            readonly=True, store=True),
        # Paid Expense
        'sum_paid_expense':
            fields.function(_calc_sum_paid_expense, string='Paid Expense',
                            type='float',
                            digits_compute=dp.get_precision('Account'),
                            readonly=True, store=True),
        # Justified Expense
        'sum_justified_expense':
            fields.function(_calc_sum_justified_expense,
                            string='Justified Expense', type='float',
                            digits_compute=dp.get_precision('Account'),
                            readonly=True, store=True),
        # Proyecto Padre
        'parent_project_id': fields.many2one('project.project',
                                             'Parent Project'),
        # Proyecot hijos.
        'childrend_project_ids':
            fields.one2many('project.project', 'parent_project_id',
                            'Projects'),
            }

    def create(self, cr, uid, vals, context=None):
        analytic_account_obj = self.pool['account.analytic.account']
        simulation_obj = self.pool['simulation.cost']
        project_id = super(ProjectProject, self).create(cr, uid, vals,
                                                        context)
        project2 = self.browse(cr, uid, project_id, context)
        analytic_account_obj.write(
            cr, uid, [project2.analytic_account_id.id],
            {'project_id': project_id}, context)
        if project2.parent_project_id:
            cond = [('project_id', '=', project2.id)]
            simulation_ids = simulation_obj.search(cr, uid, cond,
                                                   context=context)
            if simulation_ids:
                for simulation in simulation_ids:
                    nvals = {'parent_project_id':
                             project2.parent_project_id.id}
                    simulation_obj.write(cr, uid, [simulation], nvals,
                                         context)
                    paccount = project2.parent_project_id.analytic_account_id
                    nvals = {'parent_id': paccount.id}
                    analytic_account_obj.write(
                        cr, uid,
                        [simulation.project_id.analytic_account_id.id], nvals)
        return project_id

    def set_approved(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approved'}, context=context)
        return True

    def set_running(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'open'}, context=context)
        return True

    def write(self, cr, uid, ids, vals, context={}):
        analytic_account_obj = self.pool['account.analytic.account']
        analytic_line_obj = self.pool['account.analytic.line']
        simulation_obj = self.pool['simulation.cost']
        res = super(ProjectProject, self).write(cr, uid, ids, vals, context)
        if not isinstance(ids, list):
            ids = [ids]
        for obj in self.browse(cr, uid, ids, context):
            analytic_account_obj.write(cr, uid, [obj.analytic_account_id.id],
                                       {}, context)
            if obj.parent2_id:
                self.write(cr, uid, [obj.parent2_id.id], {}, context)
            if 'project_code' in vals and obj.simulation_cost_id.id:
                cond = [('project_id', '=', ids)]
                simulation_cost_list = simulation_obj.search(cr, uid, cond,
                                                             context=context)
                nvals = {'simulation_number': vals.get('project_code')}
                simulation_obj.write(cr, uid, simulation_cost_list, nvals,
                                     context)
            if obj.parent_project_id:
                account_id2 = obj.parent_project_id.analytic_account_id2.id
                cond = [('project_id', '=', obj.id)]
                simulation_ids = simulation_obj.search(cr, uid, cond, context)
                if simulation_ids:
                    for simulation in simulation_obj.browse(
                            cr, uid, simulation_ids, context):
                        nvals = {'parent_project_id': obj.parent_project_id.id}
                        simulation_obj.write(
                            cr, uid, [simulation.id], nvals, context)
                        if simulation.project_id:
                            pacc = obj.parent_project_id.analytic_account_id
                            nvals = {'parent_id': pacc.id}
                            pacc = simulation.project_id.analytic_account_id
                            analytic_account_obj.write(cr, uid, [pacc.id],
                                                       nvals, context)
                        # Voy a buscar lines de analítica
                        cond = [('project_id', '=', obj.id)]
                        analytic_line_ids = analytic_line_obj.search(
                            cr, uid, cond, context)
                        if analytic_line_ids:
                            analytic_line = analytic_line_obj.browse(
                                cr, uid, analytic_line_ids[0], context)
                            p = obj.parent_project_id.analytic_account_id2.id
                            if analytic_line.account_parent_id.id != p:
                                aparent = analytic_line.account_parent_id
                                cond = [('project_id', '=', obj.id),
                                        ('account_parent_id', '=', aparent.id)]
                                analytic_line_ids = analytic_line_obj.search(
                                    cr, uid, cond, context)
                                if analytic_line_ids:
                                    nvals = {'account_parent_id': account_id2}
                                    analytic_line_obj.write(
                                        cr, uid, analytic_line_ids, nvals,
                                        context)
        return res

    def copy(self, cr, uid, id, defaults, context=None):
        project_obj = self.pool['project.project']
        item = project_obj.browse(cr, uid, id, context)
        vals = {'name': item.name + ' (copia)'}
        res = super(ProjectProject, self).copy(cr, uid, id, vals, context)
        return res

    def onchange_parent_project_id(self, cr, uid, ids, parent_project_id,
                                   context=None):
        project_obj = self.pool['project.project']
        res = {}
        if not parent_project_id:
            res.update({'parent_id': False})
        else:
            project = project_obj.browse(cr, uid, parent_project_id, context)
            res.update({'parent_id': project.analytic_account_id.id})
        return{'value': res}
