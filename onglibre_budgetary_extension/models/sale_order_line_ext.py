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


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    _columns = {
        # Fuente de Financiación
        'financing_source_id': fields.many2one('financing.source',
                                               'Financing Source'),
        # Cliente
        'partner_id': fields.related(
            'order_id', 'partner_id', type='many2one', relation='res.partner',
            string='Partner', store=True),
    }
    _defaults = {'partner_id': lambda self, cr, uid, c: c.get('partner_id',
                                                              False)
                 }

    def create(self, cr, uid, vals, context=None):
        sale_order_line_id = super(SaleOrderLine, self).create(
            cr, uid, vals, context=context)
        order_line = self.browse(cr, uid, sale_order_line_id, context)
        if not order_line.financing_source_id:
            if order_line.order_id.financing_source_id:
                val = {'financing_source_id':
                       order_line.order_id.financing_source_id.id}
                self.write(cr, uid, [order_line.id], val, context=context)
        return sale_order_line_id

    def unlink(self, cr, uid, ids, context=None):
        financing_source_obj = self.pool['financing.source']
        project_financing_obj = self.pool['project.financing']
        datas = {}
        if ids:
            for line in self.browse(cr, uid, ids, context):
                if line.financing_source_id:
                    found = 0
                    for data in datas:
                        datos_array = datas[data]
                        fs_id = datos_array['financing_source_id']
                        if fs_id == line.financing_source_id.id:
                            found = 1
                    if found == 0:
                        vals = {'financing_source_id':
                                line.financing_source_id.id}
                        datas[(line.financing_source_id.id)] = vals
        super(SaleOrderLine, self).unlink(cr, uid, ids, context=context)
        if ids:
            for data in datas:
                # Cojo los datos del array
                datos_array = datas[data]
                financing_source_id = datos_array['financing_source_id']
                cond = [('financing_source_id', '=', financing_source_id)]
                sale_line_ids = self.search(cr, uid, cond, context=context)
                if sale_line_ids:
                    amount = 0
                    for sale_line in self.browse(cr, uid, sale_line_ids,
                                                 context):
                        if (sale_line.order_id.state not in
                            ('cancel', 'draft') and not
                                sale_line.order_id.project2_id):
                            amount = amount + sale_line.price_subtotal
                    vals = {'total_recognized': amount}
                    financing_source_obj.write(
                        cr, uid, [financing_source_id], vals, context=context)
                    financing_source = financing_source_obj.browse(
                        cr, uid, financing_source_id, context)
                    if financing_source.project_ids:
                        for project_financing in financing_source.project_ids:
                            tr = 0
                            if project_financing.project_id:
                                pf_p_id = project_financing.project_id.id
                                for sl in self.browse(
                                        cr, uid, sale_line_ids, context):
                                    if (sl.order_id.state != 'cancel'
                                            and sl.order_id.state != 'draft'):
                                        if sl.order_id:
                                            slo = sl.order_id
                                            if sl.order_id.project2_id:
                                                if (slo.project2_id.id ==
                                                        pf_p_id):
                                                    tr += sl.price_subtotal
                            if amount == 0 or tr == 0:
                                vals = {'percentage_total_recognized': 0}
                                project_financing_obj.write(
                                    cr, uid, [project_financing.id], vals,
                                    context=context)
                            else:
                                percentage_tr = (tr * 100) / amount
                                vals = {'percentage_total_recognized':
                                        percentage_tr}
                                project_financing_obj.write(
                                    cr, uid, [project_financing.id], vals,
                                    context=context)
                else:
                    vals = {'total_recognized': 0}
                    financing_source_obj.write(
                        cr, uid, [financing_source_id], vals, context=context)
                    financing_source = financing_source_obj.browse(
                        cr, uid, financing_source_id, context=context)
                    if financing_source.project_ids:
                        for project_financing in financing_source.project_ids:
                            vals = {'percentage_total_recognized': 0}
                            project_financing_obj.write(
                                cr, uid, [project_financing.id], vals,
                                context=context)
        return True
