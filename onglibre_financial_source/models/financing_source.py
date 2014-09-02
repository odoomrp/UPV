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
import re


class FinancingSource(orm.Model):

    _name = 'financing.source'
    _description = 'Financing Source'

    def _calc_grant(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = (data.grant_without_overheads + data.overheads +
                            data.transfered)
        return res

    def _calc_transfered(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            total = 0
            for line in data.transfer_fund_origin_ids:
                total = total - line.amount
            for line in data.transfer_fund_target_ids:
                total = total + line.amount
            res[data.id] = total
        return res

    def _calc_total_allocated(self, cr, uid, ids, field_names, arg=None,
                              context=None):
        res = {}
        analytic_line_obj = self.pool['account.analytic.line']
        for data in self.browse(cr, uid, ids, context=context):
            cond = [('financing_source_id', '=', data.id)]
            account_analytic_line_parent_ids = analytic_line_obj.search(
                cr, uid, cond, context=context)
            cond = [('account_analytic_line_financing_source_id', 'in',
                     account_analytic_line_parent_ids),
                    ('type', 'in', ['initial_financial_source',
                                    'modif_financial_source'])]
            analytic_line_ids = analytic_line_obj.search(cr, uid, cond,
                                                         context=context)
            assigned = 0
            for line in analytic_line_obj.browse(cr, uid, analytic_line_ids,
                                                 context):
                assigned = assigned + line.assigned
            res[data.id] = assigned
        return res

    def _calc_total_allocated_percent(self, cr, uid, ids, field_names,
                                      arg=None, context=None):
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = 0
            if data.grant != 0:
                res[data.id] = data.total_allocated / data.grant * 100
        return res

    def _calc_pending_allocation(self, cr, uid, ids, field_names, arg=None,
                                 context=None):
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = data.grant - data.total_allocated
        return res

    def _check_pending_allocation(self, cr, uid, ids, context=None):
        for data in self.browse(cr, uid, ids, context=context):
            if data.pending_allocation < 0:
                return False
        return True

    def _calc_pending_allocation_percent(self, cr, uid, ids, field_names,
                                         arg=None, context=None):
        res = {}
        for data in self.browse(cr, uid, ids, context=context):
            res[data.id] = 0
            if data.grant != 0:
                res[data.id] = data.pending_allocation / data.grant * 100

        return res

    _columns = {
        # CAMPOS BASE (TAREA 2.1.A)
        # Nombre
        'name': fields.char('Name', size=128, required=True),
        # Organismo Financiador
        'res_partner_id': fields.many2one('res.partner', 'Financing Organism',
                                          required=True,
                                          domain="[('funder', '=', '1'), "
                                          "('customer', '=', '1')]"),
        # Soporte Jurídico
        'legal_support_id': fields.many2one('legal.support', 'Legal Support'),
        # Código Convocatoria
        'code_call_id': fields.many2one('code.call', 'Code Call'),
        # Código expediente organismo financiador
        'funder_record_code': fields.char('Funder Record Code', size=64),
        # Tipo de Financiación
        'financing_type_id': fields.many2one('financing.type',
                                             'Financing Type'),
        # Sistema de disposición de fondos
        'availability_fund': fields.selection([('granted', 'Granted'),
                                               ('accepted', 'Accepted'),
                                               ('charged', 'Charged')],
                                              string="Availability Fund",
                                              required=True),
        # Fecha de concesión
        'grant_date': fields.date('Grant Date'),
        # Proyectos
        'project_ids':
            fields.one2many('project.financing', 'financing_source_id',
                            'Projects', readonly=True),
        # Fecha Elegibilidad Desde
        'eligibility_date_from': fields.date('Eligibility Date From'),
        # Fecha Elegibilidad HAsta
        'eligibility_date_to': fields.date('Eligibility Date To'),
        # Fechas de justificación
        'justification_date_ids':
            fields.one2many('justification.date', 'financing_source_id',
                            'Justification Dates'),
        # Importe Concedido = grant_without_overheads + overheads + transfered
        'grant': fields.function(_calc_grant, method=True, string='Grant',
                                 type="float", store=False),
        # Concedido sin Overheads
        'grant_without_overheads': fields.integer('Grant Without Overheads'),
        # Overheads
        'overheads': fields.integer('Overheads'),
        # Transferido = Sumatorio de Traspasos entre Fuentes
        'transfered':
            fields.function(_calc_transfered, method=True, string='Transfered',
                            type="float", store=False),
        # Total Asignado = Sumatorio de Asignados de Líneas Analíticas
        'total_allocated':
            fields.function(_calc_total_allocated, method=True,
                            string='Total Allocated', type="float",
                            store=False),
        # Total Asignado % = total_allocated / grant * 100
        'total_allocated_percent':
            fields.function(_calc_total_allocated_percent, method=True,
                            string='Total Allocated %', type="float",
                            store=False),
        # Pendiente Asignación = grant - total_allocated
        'pending_allocation':
            fields.function(_calc_pending_allocation, method=True,
                            string='Pending Allocation', type="float",
                            store=False),
        # Pendiente Asignación % = pending_allocation / grant * 100
        'pending_allocation_percent':
            fields.function(_calc_pending_allocation_percent, method=True,
                            string='Pending Allocation %', type="float",
                            store=False),
        # Reconocimientos de derecho
        'right_recognition_ids':
            fields.one2many('right.recognition', 'financing_source_id',
                            'Right Recognitions'),
        # Fondo Financiador de Ingresos
        'financier_fund_income_id':
            fields.many2one('financier.fund', 'Financier Fund Income'),
        # Fondo Financiador de Gastos
        'financier_fund_expense_id':
            fields.many2one('financier.fund', 'Financier Fund Expense'),
        # historico de las prorrogas por determinada fuente de financiacion
        'historical_extension_ids':
            fields.one2many('historical.extension', 'historical_extension_id',
                            'Historical_Extension', readonly=False),
        # Campo para observaciones
        'observations': fields.text('observations'),
        # Traspaso Fuente - Origen
        'transfer_fund_origin_ids':
            fields.one2many('transfer.fund', 'financing_source_origin_id',
                            'Transfer Funds Origin', readonly=True),
        # Traspaso Fuente - Target
        'transfer_fund_target_ids':
            fields.one2many('transfer.fund', 'financing_source_target_id',
                            'Transfer Funds Target', readonly=True),
    }

    _constraints = [
        (_check_pending_allocation,
         'Field Pending Allocation must be positive', ['pending_allocation']),
    ]

    # OnChange cuando se cambia el Organismo Financiador
    def onchange_res_partner_id(self, cr, uid, ids, name, res_partner_id):
        partner_obj = self.pool['res.partner']
        data = {}
        if res_partner_id:
            ref = ""
            res_partner = partner_obj.browse(cr, uid, res_partner_id)
            ref = res_partner.ref
            if name:
                match = re.search('\[([\w]+)\]\s*([\w\s\W]*)', name)
                if match:
                    name = match.group(2).strip()
                if ref:
                    name = '[' + ref + '] ' + name
            else:
                if ref:
                    name = '[' + ref + ']'
            data = {'name': name
                    }
        return {'value': data}
