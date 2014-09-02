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


class AccountAnalyticLine(orm.Model):
    _inherit = 'account.analytic.line'

    def _available_expense(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = (obj.updated_expense_budget + obj.remainder -
                           obj.real_expense - obj.expense_compromised -
                           obj.expense_request)
        return res

    def _sum_available_expense(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = 0
        return res

    # Calculo total Presupuesto de gasto
    def _sum_expense_budget(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.type:
                if (obj.type == 'initial_budgetary' or obj.type ==
                        'modif_budgetary' or obj.type == 'imputation'):
                    res[obj.id] = obj.expense_budget
                else:
                    if obj.type == 'financing_source':
                        w_imp = 0
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'imputation'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(cr, uid, cond,
                                                            context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = w_imp + initial_budgetary.expense_budget
                        res[obj.id] = w_imp
                    else:
                        if obj.type == 'budgetary':
                            w_imp = 0
                            cond = [('project_id', '=', obj.project_id.id),
                                    ('type', '=', 'initial_budgetary'),
                                    ('account_analytic_line_budgetary_id', '=',
                                     obj.id)]
                            initial_budgetary_ids = self.search(
                                cr, uid, cond, context=context)
                            for initial_budgetary_id in initial_budgetary_ids:
                                initial_budgetary = self.browse(
                                    cr, uid, initial_budgetary_id, context)
                                w_imp = (w_imp +
                                         initial_budgetary.expense_budget)
                            cond = [('project_id', '=', obj.project_id.id),
                                    ('type', '=', 'modif_budgetary'),
                                    ('account_analytic_line_budgetary_id', '=',
                                     obj.id)]
                            modif_budgetary_ids = self.search(
                                cr, uid, cond, context=context)
                            for modif_budgetary_id in modif_budgetary_ids:
                                modif_budgetary = self.browse(
                                    cr, uid, modif_budgetary_id, context)
                                w_imp = w_imp + modif_budgetary.expense_budget
                            cond = [('project_id', '=', obj.project_id.id),
                                    ('type', '=', 'financing_source'),
                                    ('account_analytic_line_budgetary_id', '=',
                                     obj.id)]
                            financing_source_ids = self.search(
                                cr, uid, cond, context=context)
                            for financing_source_id in financing_source_ids:
                                financing_source = self.browse(
                                    cr, uid, financing_source_id, context)
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'imputation'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=',
                                         financing_source.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                i_ids = initial_budgetary_ids
                                for initial_budgetary_id in i_ids:
                                    initial_budgetary = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = (w_imp +
                                             initial_budgetary.expense_budget)
                            res[obj.id] = w_imp
                        else:
                            res[obj.id] = 0
            else:
                res[obj.id] = 0
        return res

    # Calculo total Presupuesto de gasto Remanente
    def _sum_remainder(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.type:
                if (obj.type == 'initial_budgetary' or obj.type ==
                        'modif_budgetary' or obj.type == 'imputation'):
                    res[obj.id] = obj.remainder
                else:
                    if obj.type == 'financing_source':
                        w_imp = 0
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'imputation'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(
                            cr, uid, cond, context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = w_imp + initial_budgetary.remainder
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'initial_budgetary'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(
                            cr, uid, cond, context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = w_imp + initial_budgetary.remainder
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'modif_budgetary'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(
                            cr, uid, cond, context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = w_imp + initial_budgetary.remainder
                        res[obj.id] = w_imp
                    else:
                        if obj.type == 'budgetary':
                            w_imp = 0
                            cond = [('project_id', '=', obj.project_id.id),
                                    ('type', '=', 'financing_source'),
                                    ('account_analytic_line_budgetary_id', '=',
                                     obj.id)]
                            financing_source_ids = self.search(
                                cr, uid, cond, context=context)
                            for financing_source_id in financing_source_ids:
                                financing_source = self.browse(
                                    cr, uid, financing_source_id, context)
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'imputation'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=',
                                         financing_source.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                ib_ids = initial_budgetary_ids
                                for initial_budgetary_id in ib_ids:
                                    initial_budgetary = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = w_imp + initial_budgetary.remainder
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'initial_budgetary'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=',
                                         financing_source.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                ib_ids = initial_budgetary_ids
                                for initial_budgetary_id in ib_ids:
                                    initial_budgetary = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = w_imp + initial_budgetary.remainder
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'modif_budgetary'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=',
                                         financing_source.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                ib_ids = initial_budgetary_ids
                                for initial_budgetary_id in ib_ids:
                                    initial_budgetary = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = w_imp + initial_budgetary.remainder
                            res[obj.id] = w_imp
                        else:
                            res[obj.id] = 0
            else:
                res[obj.id] = 0
        return res

    # Calculo total Gasto Modificado
    def _sum_updated_expense_budget(self, cr, uid, ids, name, arg,
                                    context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.type:
                if (obj.type == 'initial_budgetary' or obj.type ==
                        'modif_budgetary' or obj.type == 'imputation'):
                    res[obj.id] = obj.updated_expense_budget
                else:
                    if obj.type == 'financing_source':
                        w_imp = 0
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'imputation'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(
                            cr, uid, cond, context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = (w_imp +
                                     initial_budgetary.updated_expense_budget)
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'initial_budgetary'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(
                            cr, uid, cond, context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = (w_imp +
                                     initial_budgetary.updated_expense_budget)
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'initial_budgetary'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(
                            cr, uid, cond, context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = (w_imp +
                                     initial_budgetary.updated_expense_budget)
                        res[obj.id] = w_imp
                    else:
                        if obj.type == 'budgetary':
                            w_imp = 0
                            cond = [('project_id', '=', obj.project_id.id),
                                    ('type', '=', 'financing_source'),
                                    ('account_analytic_line_budgetary_id', '=',
                                     obj.id)]
                            financing_source_ids = self.search(
                                cr, uid, cond, context=context)
                            for financing_source_id in financing_source_ids:
                                fs = self.browse(cr, uid, financing_source_id,
                                                 context)
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'imputation'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=', fs.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                ib_ids = initial_budgetary_ids
                                for initial_budgetary_id in ib_ids:
                                    ib = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = (w_imp +
                                             ib.updated_expense_budget)
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'initial_budgetary'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=', fs.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                ib_ids = initial_budgetary_ids
                                for initial_budgetary_id in ib_ids:
                                    ib = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = (w_imp +
                                             ib.updated_expense_budget)
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'initial_budgetary'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=', fs.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                ib_ids = initial_budgetary_ids
                                for initial_budgetary_id in ib_ids:
                                    ib = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = (w_imp +
                                             ib.updated_expense_budget)
                            res[obj.id] = w_imp
                        else:
                            res[obj.id] = 0
            else:
                res[obj.id] = 0
        return res

    # Calculo total Gasto Solicitado
    def _sum_expense_request(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.type:
                if (obj.type == 'initial_budgetary' or obj.type ==
                        'modif_budgetary' or obj.type == 'imputation'):
                    res[obj.id] = obj.expense_request
                else:
                    if obj.type == 'financing_source':
                        w_imp = 0
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'imputation'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(
                            cr, uid, cond, context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = w_imp + initial_budgetary.expense_request
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'initial_budgetary'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(
                            cr, uid, cond, context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = w_imp + initial_budgetary.expense_request
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'modif_budgetary'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(
                            cr, uid, cond, context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = w_imp + initial_budgetary.expense_request
                        res[obj.id] = w_imp
                    else:
                        if obj.type == 'budgetary':
                            w_imp = 0
                            cond = [('project_id', '=', obj.project_id.id),
                                    ('type', '=', 'financing_source'),
                                    ('account_analytic_line_budgetary_id', '=',
                                     obj.id)]
                            financing_source_ids = self.search(
                                cr, uid, cond, context=context)
                            for financing_source_id in financing_source_ids:
                                financing_source = self.browse(
                                    cr, uid, financing_source_id, context)
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'imputation'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=',
                                         financing_source.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                ib_ids = initial_budgetary_ids
                                for initial_budgetary_id in ib_ids:
                                    initial_budgetary = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = (w_imp +
                                             initial_budgetary.expense_request)
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'initial_budgetary'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=',
                                         financing_source.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                ib_ids = initial_budgetary_ids
                                for initial_budgetary_id in ib_ids:
                                    initial_budgetary = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = (w_imp +
                                             initial_budgetary.expense_request)
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'modif_budgetary'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=',
                                         financing_source.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                ib_ids = initial_budgetary_ids
                                for initial_budgetary_id in ib_ids:
                                    initial_budgetary = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = (w_imp +
                                             initial_budgetary.expense_request)
                            res[obj.id] = w_imp
                        else:
                            res[obj.id] = 0
            else:
                res[obj.id] = 0
        return res

    # Calculo total Gasto Comprometido
    def _sum_expense_compromised(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.type:
                if (obj.type == 'initial_budgetary' or obj.type ==
                        'modif_budgetary' or obj.type == 'imputation'):
                    res[obj.id] = obj.expense_compromised
                else:
                    if obj.type == 'financing_source':
                        w_imp = 0
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'imputation'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(
                            cr, uid, cond, context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = (w_imp +
                                     initial_budgetary.expense_compromised)
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'initial_budgetary'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(
                            cr, uid, cond, context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = (w_imp +
                                     initial_budgetary.expense_compromised)
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'modif_budgetary'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(
                            cr, uid, cond, context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = (w_imp +
                                     initial_budgetary.expense_compromised)
                        res[obj.id] = w_imp
                    else:
                        if obj.type == 'budgetary':
                            w_imp = 0
                            cond = [('project_id', '=', obj.project_id.id),
                                    ('type', '=', 'financing_source'),
                                    ('account_analytic_line_budgetary_id', '=',
                                     obj.id)]
                            financing_source_ids = self.search(
                                cr, uid, cond, context=context)
                            for financing_source_id in financing_source_ids:
                                fs = self.browse(cr, uid, financing_source_id,
                                                 context)
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'imputation'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=', fs.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                ib_ids = initial_budgetary_ids
                                for initial_budgetary_id in ib_ids:
                                    ib = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = (w_imp +
                                             ib.expense_compromised)
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'initial_budgetary'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=', fs.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                ib_ids = initial_budgetary_ids
                                for initial_budgetary_id in ib_ids:
                                    ib = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = (w_imp +
                                             ib.expense_compromised)
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'modif_budgetary'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=', fs.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                ib_ids = initial_budgetary_ids
                                for initial_budgetary_id in ib_ids:
                                    ib = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = (w_imp +
                                             ib.expense_compromised)
                            res[obj.id] = w_imp
                        else:
                            res[obj.id] = 0
            else:
                res[obj.id] = 0
        return res

    # Calculo total Gasto Real
    def _sum_real_expense(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.type:
                if (obj.type == 'initial_budgetary' or obj.type ==
                        'modif_budgetary' or obj.type == 'imputation'):
                    res[obj.id] = obj.real_expense
                else:
                    if obj.type == 'financing_source':
                        w_imp = 0
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'imputation'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(
                            cr, uid, cond, context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = w_imp + initial_budgetary.real_expense
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'initial_budgetary'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(
                            cr, uid, cond, context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = w_imp + initial_budgetary.real_expense
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'modif_budgetary'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        initial_budgetary_ids = self.search(
                            cr, uid, cond, context=context)
                        for initial_budgetary_id in initial_budgetary_ids:
                            initial_budgetary = self.browse(
                                cr, uid, initial_budgetary_id, context)
                            w_imp = w_imp + initial_budgetary.real_expense
                        res[obj.id] = w_imp
                    else:
                        if obj.type == 'budgetary':
                            w_imp = 0
                            cond = [('project_id', '=', obj.project_id.id),
                                    ('type', '=', 'financing_source'),
                                    ('account_analytic_line_budgetary_id',
                                     '=', obj.id)]
                            financing_source_ids = self.search(
                                cr, uid, cond, context=context)
                            for financing_source_id in financing_source_ids:
                                fs = self.browse(cr, uid, financing_source_id,
                                                 context)
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'imputation'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=', fs.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                ib_ids = initial_budgetary_ids
                                for initial_budgetary_id in ib_ids:
                                    ib = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = w_imp + ib.real_expense
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'initial_budgetary'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=', fs.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                ib_ids = initial_budgetary_ids
                                for initial_budgetary_id in ib_ids:
                                    ib = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = w_imp + ib.real_expense
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'modif_budgetary'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=', fs.id)]
                                initial_budgetary_ids = self.search(
                                    cr, uid, cond, context=context)
                                ib_ids = initial_budgetary_ids
                                for initial_budgetary_id in ib_ids:
                                    ib = self.browse(
                                        cr, uid, initial_budgetary_id, context)
                                    w_imp = w_imp + ib.real_expense
                            res[obj.id] = w_imp
                        else:
                            res[obj.id] = 0
            else:
                res[obj.id] = 0
        return res

    def _sum_paid_expense(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.type:
                if obj.type == 'imputation':
                    res[obj.id] = obj.paid_expense
                else:
                    if obj.type == 'financing_source':
                        w_imp = 0
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'imputation'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        financing_source_ids = self.search(
                            cr, uid, cond, context=context)
                        for financing_source_id in financing_source_ids:
                            financing_source = self.browse(
                                cr, uid, financing_source_id, context)
                            w_imp = w_imp + financing_source.paid_expense
                        res[obj.id] = w_imp
                    else:
                        if obj.type == 'budgetary':
                            w_imp = 0
                            cond = [('project_id', '=', obj.project_id.id),
                                    ('type', '=', 'financing_source'),
                                    ('account_analytic_line_budgetary_id', '=',
                                     obj.id)]
                            budgetary_ids = self.search(
                                cr, uid, cond, context=context)
                            for budgetary_id in budgetary_ids:
                                budgetary = self.browse(cr, uid, budgetary_id,
                                                        context)
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'imputation'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=', budgetary.id)]
                                fs_ids = self.search(
                                    cr, uid, cond, context=context)
                                for financing_source_id in fs_ids:
                                    fs = self.browse(
                                        cr, uid, financing_source_id, context)
                                    w_imp = w_imp + fs.paid_expense
                            res[obj.id] = w_imp
                        else:
                            res[obj.id] = 0
            else:
                res[obj.id] = 0
        return res

    def _sum_justified_expense(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.type:
                if obj.type == 'imputation':
                    res[obj.id] = obj.justified_expense
                else:
                    if obj.type == 'financing_source':
                        w_imp = 0
                        cond = [('project_id', '=', obj.project_id.id),
                                ('type', '=', 'imputation'),
                                ('account_analytic_line_financing_source_id',
                                 '=', obj.id)]
                        financing_source_ids = self.search(
                            cr, uid, cond, context=context)
                        for financing_source_id in financing_source_ids:
                            financing_source = self.browse(
                                cr, uid, financing_source_id, context)
                            w_imp = w_imp + financing_source.justified_expense
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
                                budget = self.browse(cr, uid, budgetary_id,
                                                     context)
                                cond = [('project_id', '=', obj.project_id.id),
                                        ('type', '=', 'imputation'),
                                        ('account_analytic_line_financing_'
                                         'source_id', '=', budget.id)]
                                fs_ids = self.search(
                                    cr, uid, cond, context=context)
                                for financing_source_id in fs_ids:
                                    fs = self.browse(
                                        cr, uid, financing_source_id, context)
                                    w_imp = w_imp + fs.justified_expense
                            res[obj.id] = w_imp
                        else:
                            res[obj.id] = 0
            else:
                res[obj.id] = 0
        return res

    _columns = {
        # Tipo de Apunte
        'type': fields.selection([('imputation', 'Imputation'),
                                  ('budgetary', 'Budgetary'),
                                  ('financing_source', 'Financing Source'),
                                  ('justification', 'Justification'),
                                  ('initial_budgetary', 'Initial Budgetary'),
                                  ('modif_budgetary',
                                   'Modification Budgetary'),
                                  ('initial_financial_source',
                                   'Initial Financing Source'),
                                  ('modif_financial_source',
                                   'Modif. Financing Source')],
                                 'Account Type'),
        # Campo para saber a que proyecto pertenece la línea de analítica
        'project_id': fields.many2one('project.project', 'Project'),
        # CAMPOS PRESUPUESTARIOS
        # Presupuesto de gasto
        'expense_budget': fields.float(
            'Expense Budget', digits_compute=dp.get_precision('Account')),
        # Remanente
        'remainder': fields.float(
            'Remainder', digits_compute=dp.get_precision('Account')),
        # Presupuesto de Gasto Actualizado
        'updated_expense_budget': fields.float(
            'Update Expense Budget',
            digits_compute=dp.get_precision('Account')),
        # Gasto Solicitado
        'expense_request': fields.float(
            'Expense Request', digits_compute=dp.get_precision('Account')),
        # Gasto Comprometido
        'expense_compromised': fields.float(
            'Expense Compromised', digits_compute=dp.get_precision('Account')),
        # Gasto Real
        'real_expense': fields.float(
            'Real Expense', digits_compute=dp.get_precision('Account')),
        # Gasto disponible
        'available_expense': fields.function(
            _available_expense, string='Available Expense', type='float',
            digits_compute=dp.get_precision('Account'), readonly=True,
            store=True),
        # Gasto Pagado
        'paid_expense': fields.float(
            'Paid Expense', digits_compute=dp.get_precision('Account')),
        # Gasto Justificado
        'justified_expense': fields.float(
            'Justified Expense', digits_compute=dp.get_precision('Account')),
        # SUMATORIOS DE CAMPOS PRESUPUESTARIOS
        # Presupuesto de gasto
        'sum_expense_budget': fields.function(
            _sum_expense_budget, string='Sum Expense Budget', type='float',
            digits_compute=dp.get_precision('Account')),
        # Remanente
        'sum_remainder': fields.function(
            _sum_remainder, string='Sum Remainder', type='float',
            digits_compute=dp.get_precision('Account')),
        # Presupuesto de Gasto Actualizado
        'sum_updated_expense_budget': fields.function(
            _sum_updated_expense_budget, string='Sum Updated Expense Budget',
            type='float', digits_compute=dp.get_precision('Account')),
        # Gasto Solicitado
        'sum_expense_request': fields.function(
            _sum_expense_request, string='Sum Expense Request',
            type='float', digits_compute=dp.get_precision('Account')),
        # Gasto Comprometido
        'sum_expense_compromised': fields.function(
            _sum_expense_compromised, string='Sum Expense Compromised',
            type='float', digits_compute=dp.get_precision('Account')),
        # Gasto Real
        'sum_real_expense': fields.function(
            _sum_real_expense, string='Sum Real Expense', type='float',
            digits_compute=dp.get_precision('Account')),
        # Gasto disponible
        'sum_available_expense': fields.function(
            _sum_available_expense, string='Sum Available Expense',
            type='float', digits_compute=dp.get_precision('Account'),
            readonly=True),
        # Gasto Pagado
        'sum_paid_expense': fields.function(
            _sum_paid_expense, string='Sum Paid Expense', type='float',
            digits_compute=dp.get_precision('Account')),
        # Gasto Justificado
        'sum_justified_expense': fields.function(
            _sum_justified_expense, string='Sum Justified Expense',
            type='float', digits_compute=dp.get_precision('Account')),
        # Cliente
        'partner_id': fields.many2one('res.partner', 'Financing Organism'),
    }

    _defaults = {
        'account_id': lambda self, cr, uid, c: c.get('account_id', False),
    }
