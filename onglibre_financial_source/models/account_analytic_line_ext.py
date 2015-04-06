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
import time


class AccountAnalyticLine(orm.Model):

    _inherit = 'account.analytic.line'

    def _get_parent_line(self, cr, uid, ids, name, arg, context=None):
        res = {}
        journal_obj = self.pool['account.analytic.journal']
        account_obj = self.pool['account.account']
        project_obj = self.pool['project.project']
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = False
            if obj.account_analytic_line_financing_source_id:
                res[obj.id] = obj.account_analytic_line_financing_source_id.id
                continue
            if obj.account_analytic_line_budgetary_id:
                res[obj.id] = obj.account_analytic_line_budgetary_id.id
                continue
            if obj.type == 'budgetary':
                cond = [('is_project', '=', True),
                        ('account_id', '=', obj.account_id.id)]
                line_list = self.search(cr, uid, cond, context=context)
                if line_list:
                    res[obj.id] = line_list[0]
                else:
                    cond = [('analytic_account_id', '=', obj.account_id.id)]
                    project_list = project_obj.search(
                        cr, uid, cond, context=context)
                    if project_list:
                        project_id = project_list[0]
                        vals = {'is_project': True,
                                'account_id': obj.account_id.id,
                                'name': obj.account_id.name,
                                'active': True,
                                'project_id': project_id,
                                'general_account_id': account_obj.search(
                                    cr, uid, [], context)[0],
                                'journal_id': journal_obj.search(
                                    cr, uid, [], context)[0],
                                'date': time.strftime('%Y-%m-%d')
                                }
                        line_id = self.create(cr, uid, vals, context)
                        res[obj.id] = line_id
                continue
            if obj.is_project:
                if obj.account_id.parent_id:
                    cond = [('is_project', '=', True),
                            ('account_id', '=', obj.account_id.parent_id.id)]
                    line_list = self.search(cr, uid, cond, context=context)
                    if line_list:
                        res[obj.id] = line_list[0]
                    else:
                        cond = [('analytic_account_id', '=',
                                 obj.account_id.parent_id.id)]
                        project_list = project_obj.search(
                            cr, uid, cond, context=context)
                        if project_list:
                            project_id = project_list[0]
                            vals = {'is_project': True,
                                    'account_id': obj.account_id.parent_id.id,
                                    'name': obj.account_id.parent_id.name,
                                    'active': True,
                                    'project_id': project_id,
                                    'journal_id': journal_obj.search(
                                        cr, uid, [], context=context)[0],
                                    'general_account_id': account_obj.search(
                                        cr, uid, [], context=context)[0],
                                    'date': time.strftime('%Y-%m-%d')
                                    }
                            line_id = self.create(cr, uid, vals, context)
                            res[obj.id] = line_id
                continue
        return res

    def _child_compute(self, cr, uid, ids, name, arg, context=None):
        result = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            result[line.id] = map(lambda x: x.id, [child for child in
                                                   line.child_ids])
        return result

    def _sum_available_expense(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            # res[obj.id] = (obj.sum_expense_budget +
            # obj.sum_updated_expense_budget +
            # obj.sum_remainder
            # - obj.sum_real_expense -
            # obj.sum_expense_compromised -
            # obj.sum_expense_request)
            res[obj.id] = (obj.sum_updated_expense_budget + obj.sum_remainder
                           - obj.sum_real_expense -
                           obj.sum_expense_compromised -
                           obj.sum_expense_request)
        return res

    # Calculo total Asignado
    def _sum_assigned(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if not obj.type:
                res[obj.id] = 0
            else:
                if obj.type in ('imputation', 'initial_financial_source',
                                'modif_financial_source'):
                    res[obj.id] = obj.assigned
                else:
                    if obj.type == 'financing_source':
                        w_imp = 0
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'initial_financial_source'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        modif_financing_ids = self.search(
                            cr, uid, cond, context=context)
                        for modif_financing_id in modif_financing_ids:
                            modif_financing = self.browse(
                                cr, uid, modif_financing_id, context)
                            w_imp = w_imp + modif_financing.assigned
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'modif_financial_source'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        modif_financing_ids = self.search(
                            cr, uid, cond, context=context)
                        for modif_financing_id in modif_financing_ids:
                            modif_financing = self.browse(
                                cr, uid, modif_financing_id, context)
                            w_imp = w_imp + modif_financing.assigned
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'imputation'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        modif_financing_ids = self.search(
                            cr, uid, cond, context=context)
                        for modif_financing_id in modif_financing_ids:
                            modif_financing = self.browse(
                                cr, uid, modif_financing_id, context)
                            w_imp = w_imp + modif_financing.assigned
                        res[obj.id] = w_imp
                    else:
                        if obj.type == 'budgetary':
                            w_imp = 0
                            cond = [('project_id', '=', obj.project_id.id),
                                    ('type', '=', 'financing_source'),
                                    ('account_analytic_line_budgetary_id',
                                     '=', obj.id)]
                            budgetary_ids = self.search(
                                cr, uid, cond, context=context)
                            for budgetary_id in budgetary_ids:
                                budgetary = self.browse(
                                    cr, uid, budgetary_id, context)
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=',
                                         'initial_financial_source'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=', budgetary.id)]
                                modif_financing_ids = self.search(
                                    cr, uid, cond, context=context)
                                for modif_financing_id in modif_financing_ids:
                                    modif_financing = self.browse(
                                        cr, uid, modif_financing_id, context)
                                    w_imp = w_imp + modif_financing.assigned
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=',
                                         'modif_financial_source'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=', budgetary.id)]
                                modif_financing_ids = self.search(
                                    cr, uid, cond, context=context)
                                for modif_financing_id in modif_financing_ids:
                                    modif_financing = self.browse(
                                        cr, uid, modif_financing_id, context)
                                    w_imp = w_imp + modif_financing.assigned
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'imputation'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=', budgetary.id)]
                                modif_financing_ids = self.search(
                                    cr, uid, cond, context=context)
                                for modif_financing_id in modif_financing_ids:
                                    modif_financing = self.browse(
                                        cr, uid, modif_financing_id, context)
                                    w_imp = w_imp + modif_financing.assigned
                            res[obj.id] = w_imp
                        else:
                            res[obj.id] = 0
        return res

    _columns = {
        # CAMPOS REFERENTES A FUENTE DE FINANCIACIÓN (TAREA 2.2.D)
        # Asignado
        'assigned': fields.float('Assigned',
                                 digits_compute=dp.get_precision('Account')),
        # Pagado
        'paid': fields.float('Paid',
                             digits_compute=dp.get_precision('Account')),
        # Área de Gasto
        'expense_area_id': fields.many2one('expense.area', 'Expense Area'),
        # Tipo de Apunte
        'type':
            fields.selection([('imputation', 'Imputation'),
                              ('budgetary', 'Budgetary'),
                              ('financing_source', 'Financing Source'),
                              ('justification', 'Justification'),
                              ('initial_budgetary', 'Initial Budgetary'),
                              ('modif_budgetary', 'Modification Budgetary'),
                              ('initial_financial_source',
                               'Initial Financing Source'),
                              ('modif_financial_source',
                               'Modif. Financing Source')], 'Account Type'),
        # Padre Apunte Fondo Financiador
        'account_analytic_line_financing_source_id':
            fields.many2one('account.analytic.line',
                            'Financing Source Parent',
                            domain=[('type', '=', 'financing_source')]),
        # Padre Apunte Presupuestaria
        'account_analytic_line_budgetary_id':
            fields.many2one('account.analytic.line', 'Budgetary Parent',
                            domain=[('type', '=', 'budgetary')]),
        # Padre Apunte Presupuestaria sólo lectura
        'account_analytic_line_budgetary_readonly_id':
            fields.many2one('account.analytic.line', 'Budgetary Parent',
                            store=False, domain=[('type', '=', 'budgetary')],
                            attrs={'invisible': ['|', ('type', '=',
                                                       'budgetary'),
                                                 ('type', '=',
                                                  'financing_source')],
                                   'readonly': [('type', '=',
                                                 'justification')]}),
        'account_parent_id':
            fields.related('account_id', 'parent_id', type="many2one",
                           relation="account.analytic.account",
                           string="Parent account", store=True, readonly=True),
        'parent_line_id':
            fields.function(_get_parent_line, type="many2one",
                            relation="account.analytic.line",
                            string="Parent line", store=True),
        'child_ids': fields.one2many('account.analytic.line',
                                     'parent_line_id', 'Child Lines'),
        'child_complete_ids':
            fields.function(_child_compute, relation='account.analytic.line',
                            string="Line Hierarchy", type='many2many'),
        'is_project': fields.boolean('Is project'),
        # Campos totales
        # Asignado
        'sum_assigned':
            fields.function(_sum_assigned, string='Sum Assigned', type='float',
                            digits_compute=dp.get_precision('Account'),
                            group_operator="sum"),
        # Gasto disponible
        'sum_available_expense':
            fields.function(_sum_available_expense,
                            string='Sum Available Expense', type='float',
                            digits_compute=dp.get_precision('Account'),
                            readonly=True),
        # Fechas Justificaction
        'justification_date_ids':
            fields.many2many('justification.date',
                             'justifdate_analyticline_rel',
                             'account_analytic_line_id',
                             'justification_date_id', 'Justification Dates'),
            }
    _defaults = {'type': lambda self, cr, uid, c: c.get('type', False),
                 }

    def create(self, cr, uid, vals, context=None):
        if 'account_analytic_line_budgetary_id' in vals:
            vals['account_analytic_line_budgetary_readonly_id'] = (
                vals.get('account_analytic_line_budgetary_id'))
        res = super(AccountAnalyticLine, self).create(cr, uid, vals,
                                                      context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if 'account_analytic_line_budgetary_id' in vals:
            vals['account_analytic_line_budgetary_readonly_id'] = (
                vals.get('account_analytic_line_budgetary_id'))
        return super(AccountAnalyticLine, self).write(cr, uid, ids, vals,
                                                      context=context)

    # Función que asigna el padre presupuestario a una línea de tipo
    # justificación
    def onchange_account_analytic_line_financing_source(
            self, cr, uid, ids, account_analytic_line_financing_source_id):
        analytic_line_obj = self.pool['account.analytic.line']
        data = {}
        if account_analytic_line_financing_source_id:
            line = analytic_line_obj.browse(
                cr, uid, account_analytic_line_financing_source_id)
            if line.account_analytic_line_budgetary_id:
                budg_id = line.account_analytic_line_budgetary_id.id
                data = {'account_analytic_line_budgetary_id': budg_id,
                        'account_analytic_line_budgetary_readonly_id': budg_id
                        }
        return {'value': data}
