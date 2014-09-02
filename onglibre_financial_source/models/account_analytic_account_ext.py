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

    def _assigned(self, cr, uid, ids, name, arg, context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        res = {}
        if len(ids) > 1:
            return res
        cond = [('account_id', '=', ids[0]),
                ('type', 'in', ['initial_financial_source',
                                'modif_financial_source'])]
        account_analytic_line_ids = analytic_line_obj.search(cr, uid, cond,
                                                             context)
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = 0
            for account_analytic_line in analytic_line_obj.browse(
                    cr, uid, account_analytic_line_ids, context):
                res[data.id] = res[data.id] + account_analytic_line.assigned
        return res

    def _imputed(self, cr, uid, ids, name, arg, context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        res = {}
        if len(ids) > 1:
            return res
        cond = [('account_id', '=', ids[0]),
                ('type', 'in', ['initial_financial_source',
                                'modif_financial_source', 'imputation'])]
        account_analytic_line_ids = analytic_line_obj.search(cr, uid, cond,
                                                             context)
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = 0
            for account_analytic_line in analytic_line_obj.browse(
                    cr, uid, account_analytic_line_ids, context):
                res[data.id] = res[data.id] + account_analytic_line.imputed
        return res

    def _available(self, cr, uid, ids, name, arg, context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        res = {}
        if len(ids) > 1:
            return res
        cond = [('account_id', '=', ids[0]),
                ('type', 'in', ['initial_financial_source',
                                'modif_financial_source', 'imputation'])]
        account_analytic_line_ids = analytic_line_obj.search(cr, uid, cond,
                                                             context)
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = 0
            for account_analytic_line in analytic_line_obj.browse(
                    cr, uid, account_analytic_line_ids, context):
                res[data.id] = (res[data.id] + account_analytic_line.assigned
                                - account_analytic_line.imputed)
        return res

    def _justified(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = 0
        return res

    def _paid(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = 0
        return res

    _columns = {
        # CAMPOS PESTAÑA FUENTES DE FINANCIACIÓN (TAREA 2.2.D)
        # Asignado
        'assigned': fields.function(_assigned, string='Assigned', type='float',
                                    digits_compute=dp.get_precision('Account'),
                                    readonly=True),
        # Imputado
        'imputed': fields.function(_imputed, string='Imputed', type='float',
                                   digits_compute=dp.get_precision('Account'),
                                   readonly=True),
        # Disponible
        'available':
            fields.function(_available, string='Available', type='float',
                            digits_compute=dp.get_precision('Account'),
                            readonly=True),
        # Justificado
        'justified':
            fields.function(_justified, string='Justified', type='float',
                            digits_compute=dp.get_precision('Account'),
                            readonly=True),
        # Pagado
        'paid': fields.function(_paid, string='Paid', type='float',
                                digits_compute=dp.get_precision('Account'),
                                readonly=True),
    }
