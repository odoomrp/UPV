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


class AccountAnalyticAccount(orm.Model):
    _inherit = 'account.analytic.account'

    def _calc_totals(self, cr, uid, ids, name, arg, context=None):
        res = {}
        project_obj = self.pool['project.project']
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = {'expense_budget': 0.0,
                           'remainder': 0.0,
                           'updated_expense_budget': 0.0,
                           'expense_compromised': 0.0,
                           'available_expense': 0.0,
                           'real_expense': 0.0,
                           'paid_expense': 0.0,
                           'justified_expense': 0.0
                           }
            condition = [('analytic_account_id', '=', obj.id)]
            project_list = project_obj.search(
                cr, uid, condition, context=context)
            if project_list:
                project_id = project_list[0]
                project_o = project_obj.browse(cr, uid, project_id, context)
                expense_budget = 0
                remainder = 0
                expense_request = 0
                updated_expense_budget = 0
                expense_compromised = 0
                available_expense = 0
                real_expense = 0
                paid_expense = 0
                justified_expense = 0
                for analytic_line in project_o.account_analytic_line_ids:
                    expense_budget += analytic_line.expense_budget
                    remainder += analytic_line.remainder
                    expense_request += analytic_line.expense_request
                    l = analytic_line
                    updated_expense_budget += l.updated_expense_budget
                    expense_compromised += analytic_line.expense_compromised
                    available_expense += analytic_line.available_expense
                    real_expense += analytic_line.real_expense
                    paid_expense += analytic_line.paid_expense
                    justified_expense += analytic_line.justified_expense

                res[obj.id]['expense_budget'] = expense_budget
                res[obj.id]['remainder'] = remainder
                res[obj.id]['expense_request'] = expense_request
                res[obj.id]['updated_expense_budget'] = updated_expense_budget
                res[obj.id]['expense_compromised'] = expense_compromised
                res[obj.id]['available_expense'] = available_expense
                res[obj.id]['real_expense'] = real_expense
                res[obj.id]['paid_expense'] = paid_expense
                res[obj.id]['justified_expense'] = justified_expense
        return res

    def _debit_credit_bal_qtty_project_financer(self, cr, uid, ids, fields,
                                                arg, context=None):
        res = {}
        if context is None:
            context = {}
        condition = [('parent_id', 'child_of', ids)]
        child_ids = tuple(self.search(cr, uid, condition, context=context))
        for i in child_ids:
            res[i] = {}
            for n in fields:
                res[i][n] = 0.0
        if not child_ids:
            return res
        where_date = ''
        where_clause_args = [tuple(child_ids)]
        if context.get('from_date', False):
            where_date += " AND l.date >= %s"
            where_clause_args += [context['from_date']]
        if context.get('to_date', False):
            where_date += " AND l.date <= %s"
            where_clause_args += [context['to_date']]
        cr.execute("""
              SELECT a.id,
                     sum(
                         CASE WHEN l.amount > 0
                         THEN l.amount
                         ELSE 0.0
                         END
                          ) as debit,
                     sum(
                         CASE WHEN l.amount < 0
                         THEN -l.amount
                         ELSE 0.0
                         END
                          ) as credit,
                     COALESCE(SUM(l.expense_budget),0) AS sum_expense_budget,
                     COALESCE(SUM(l.remainder),0) AS sum_remainder,
                     COALESCE(SUM(l.expense_request),0) AS sum_expense_request,
                     COALESCE(SUM(l.updated_expense_budget),0)
                         AS sum_updated_expense_budget,
                     COALESCE(SUM(l.expense_compromised),0)
                         AS sum_expense_compromised,
                     COALESCE(SUM(l.available_expense),0)
                         AS sum_available_expense,
                     COALESCE(SUM(l.real_expense),0) AS sum_real_expense,
                     COALESCE(SUM(l.paid_expense),0) AS sum_paid_expense,
                     COALESCE(SUM(l.justified_expense),0)
                         AS sum_justified_expense,
                     COALESCE(SUM(l.amount),0) AS balance,
                     COALESCE(SUM(l.unit_amount),0) AS quantity,
                     COALESCE(SUM(l.assigned),0) AS sum_assigned
              FROM account_analytic_account a
                  LEFT JOIN account_analytic_line l ON (a.id = l.account_id)
              WHERE a.id IN %s
              """ + where_date + """
              GROUP BY a.id""", where_clause_args)

        for row in cr.dictfetchall():
            res[row['id']] = {}
            for field in fields:
                res[row['id']][field] = row[field]
        return self._compute_level_tree(cr, uid, ids, child_ids, res, fields,
                                        context)

    _columns = {
        # Estado
        'state': fields.selection([('template', 'Template'),
                                   ('draft', 'New'),
                                   ('approved', 'Approved'),
                                   ('running', 'Running'),
                                   ('open', 'Open'),
                                   ('pending', 'Pending'),
                                   ('cancelled', 'Cancelled'),
                                   ('close', 'Closed')], 'State',
                                  required=True),
        # Traspaso automático de remanentes
        'remainder_automatic_transfer':
            fields.boolean('Remainder Automatic Transfer'),
        # Proyecto destino
        'project_destination_id':
            fields.many2one('project.project', 'Project Destination'),
        # CAMPOS INFORMACION ECONÓMICA (TAREA 1.2.B)
        # IVA DEDUCIBLE
        'deductible_iva': fields.boolean('Deductible IVA'),
        # Presupuesto de gasto
        'expense_budget':
            fields.function(_calc_totals, method=True, string='Expense Budget',
                            type='float',
                            digits_compute=dp.get_precision('Account'),
                            store=True, multi="analytic_totals"),
        # Remanente
        'remainder':
            fields.function(_calc_totals, method=True, string='Remainder',
                            ype='float',
                            digits_compute=dp.get_precision('Account'),
                            store=True, multi="analytic_totals"),
        # Remanente
        'expense_request':
            fields.function(_calc_totals, method=True,
                            string='Expense Request', type='float',
                            digits_compute=dp.get_precision('Account'),
                            store=True, multi="analytic_totals"),
        # Presupuesto de Gasto Actualizado
        'updated_expense_budget':
            fields.function(_calc_totals, method=True,
                            string='Update Expense Budget', type='float',
                            digits_compute=dp.get_precision('Account'),
                            store=True, multi="analytic_totals"),
        # Gasto Comprometido
        'expense_compromised':
            fields.function(_calc_totals, method=True,
                            string='Expense Compromised', type='float',
                            digits_compute=dp.get_precision('Account'),
                            store=True, multi="analytic_totals"),
        # Gasto disponible
        'available_expense':
            fields.function(_calc_totals, method=True,
                            string='Available Expense', type='float',
                            digits_compute=dp.get_precision('Account'),
                            store=True, multi="analytic_totals"),
        # Gasto Real
        'real_expense':
            fields.function(_calc_totals, method=True, string='Real Expense',
                            type='float',
                            digits_compute=dp.get_precision('Account'),
                            store=True, multi="analytic_totals"),
        # Gasto Pagado
        'paid_expense':
            fields.function(_calc_totals, method=True, string='Paid Expense',
                            type='float',
                            digits_compute=dp.get_precision('Account'),
                            store=True, multi="analytic_totals"),
        # Gasto Justificado
        'justified_expense':
            fields.function(_calc_totals, method=True,
                            string='Justified Expense', type='float',
                            digits_compute=dp.get_precision('Account'),
                            store=True, multi="analytic_totals"),
        # Proyecto
        'project_id': fields.many2one('project.project', 'Project'),
        # Código
        #'code': fields.related('project_id', 'project_code', type='char',
                               #string='Code/Reference', size=20),
        # Campos para el plan de cuentas analíticas
        'sum_expense_budget':
            fields.function(_debit_credit_bal_qtty_project_financer,
                            type='float', string='Expense Budget',
                            multi='debit_credit_bal_qtty',
                            digits_compute=dp.get_precision('Account')),
        'sum_remainder':
            fields.function(_debit_credit_bal_qtty_project_financer,
                            type='float', string='Remainder',
                            multi='debit_credit_bal_qtty',
                            digits_compute=dp.get_precision('Account')),
        'sum_expense_request':
            fields.function(_debit_credit_bal_qtty_project_financer,
                            type='float', string='Expense Request',
                            multi='debit_credit_bal_qtty',
                            digits_compute=dp.get_precision('Account')),
        'sum_updated_expense_budget':
            fields.function(_debit_credit_bal_qtty_project_financer,
                            type='float', string='Updated Expense Budget',
                            multi='debit_credit_bal_qtty',
                            digits_compute=dp.get_precision('Account')),
        'sum_expense_compromised':
            fields.function(_debit_credit_bal_qtty_project_financer,
                            type='float', string='Expense Compromised',
                            multi='debit_credit_bal_qtty',
                            digits_compute=dp.get_precision('Account')),
        'sum_available_expense':
            fields.function(_debit_credit_bal_qtty_project_financer,
                            type='float', string='Available Expense',
                            multi='debit_credit_bal_qtty',
                            digits_compute=dp.get_precision('Account')),
        'sum_real_expense':
            fields.function(_debit_credit_bal_qtty_project_financer,
                            type='float', string='Real Expense',
                            multi='debit_credit_bal_qtty',
                            digits_compute=dp.get_precision('Account')),
        'sum_paid_expense':
            fields.function(_debit_credit_bal_qtty_project_financer,
                            type='float', string='Paid Expense',
                            multi='debit_credit_bal_qtty',
                            digits_compute=dp.get_precision('Account')),
        'sum_justified_expense':
            fields.function(_debit_credit_bal_qtty_project_financer,
                            type='float', string='Justified Expense',
                            multi='debit_credit_bal_qtty',
                            digits_compute=dp.get_precision('Account')),
        'balance':
            fields.function(_debit_credit_bal_qtty_project_financer,
                            type='float', string='Balance',
                            multi='debit_credit_bal_qtty',
                            digits_compute=dp.get_precision('Account')),
        'debit':
            fields.function(_debit_credit_bal_qtty_project_financer,
                            type='float', string='Debit',
                            multi='debit_credit_bal_qtty',
                            digits_compute=dp.get_precision('Account')),
        'credit':
            fields.function(_debit_credit_bal_qtty_project_financer,
                            type='float', string='Credit',
                            multi='debit_credit_bal_qtty',
                            digits_compute=dp.get_precision('Account')),
        'quantity':
            fields.function(_debit_credit_bal_qtty_project_financer,
                            type='float', string='Quantity',
                            multi='debit_credit_bal_qtty'),
        'sum_assigned':
            fields.function(_debit_credit_bal_qtty_project_financer,
                            type='float', string='Assigned',
                            multi='debit_credit_bal_qtty'),
            }

    _defaults = {
        'state': 'draft',
    }
