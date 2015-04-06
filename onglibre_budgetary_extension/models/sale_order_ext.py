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


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        # Cliente
        'partner_id': fields.many2one(
            'res.partner', 'Customer', readonly=True, required=True,
            states={'draft': [('readonly', False)]}, change_default=True,
            select=True),
    }
    _defaults = {'partner_id': lambda self, cr, uid, c: c.get('partner_id',
                                                              False)
                 }

    def action_wait(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        financing_source_obj = self.pool['financing.source']
        sale_order_line_obj = self.pool['sale.order.line']
        project_financing_obj = self.pool['project.financing']
        super(SaleOrder, self).action_wait(cr, uid, ids, context)
        if ids:
            for sale in self.browse(cr, uid, ids, context):
                datas = {}
                for line in sale.order_line:
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
                for data in datas:
                    # Cojo los datos del array
                    datos_array = datas[data]
                    financing_source_id = datos_array['financing_source_id']
                    cond = [('financing_source_id', '=', financing_source_id)]
                    sale_line_ids = sale_order_line_obj.search(cr, uid, cond,
                                                               context=context)
                    if sale_line_ids:
                        amount = 0
                        sale_amount = 0
                        for sale_line in sale_order_line_obj.browse(
                                cr, uid, sale_line_ids, context=context):
                            if (sale_line.order_id.state not in
                                ('cancel', 'draft') and not
                                    sale_line.order_id.project2_id):
                                amount = amount + sale_line.price_subtotal
                                if sale_line.order_id.id == sale.id:
                                    sale_amount = (sale_amount +
                                                   sale_line.price_subtotal)
                        vals = {'total_recognized': amount}
                        financing_source_obj.write(
                            cr, uid, [financing_source_id], vals,
                            context=context)
                        financing_source = financing_source_obj.browse(
                            cr, uid, financing_source_id, context=context)
                        if financing_source.project_ids:
                            p_ids = financing_source.project_ids
                            for project_financing in p_ids:
                                total_recognized = 0
                                if project_financing.project_id:
                                    for sl in sale_order_line_obj.browse(
                                            cr, uid, sale_line_ids, context):
                                        ps = sl.price_subtotal
                                        if (sl.order_id.state !=
                                            'cancel' and
                                            sl.order_id.state !=
                                                'draft'):
                                            if sl.order_id:
                                                o_id = sl.order_id
                                                if o_id.project2_id:
                                                    pf = project_financing
                                                    if (o_id.project2_id.id ==
                                                            pf.project_id.id):
                                                        total_recognized += ps
                                if amount == 0 or total_recognized == 0:
                                    percentage_tr = 0
                                else:
                                    percentage_tr = ((total_recognized * 100) /
                                                     amount)
                                vals = {'percentage_total_recognized':
                                        percentage_tr}
                                project_financing_obj.write(
                                    cr, uid, [project_financing.id], vals,
                                    context=context)
                        if financing_source.rd_preliminary:
                            fsg = financing_source.grant_without_overheads
                            grant_without_overheads = fsg + sale_amount
                            vals = {'grant_without_overheads':
                                    grant_without_overheads}
                            financing_source_obj.write(
                                cr, uid, financing_source_id, vals,
                                context=context)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        financing_source_obj = self.pool['financing.source']
        sale_order_line_obj = self.pool['sale.order.line']
        project_financing_obj = self.pool['project.financing']
        datas = {}
        super(SaleOrder, self).action_cancel(cr, uid, ids, context=context)
        if ids:
            for sale in self.browse(cr, uid, ids, context):
                datas = {}
                for line in sale.order_line:
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
                for data in datas:
                    # Cojo los datos del array
                    datos_array = datas[data]
                    financing_source_id = datos_array['financing_source_id']
                    cond = [('financing_source_id', '=', financing_source_id)]
                    sale_line_ids = sale_order_line_obj.search(
                        cr, uid, cond, context=context)
                    if sale_line_ids:
                        amount = 0
                        sale_amount = 0
                        for sale_line in sale_order_line_obj.browse(
                                cr, uid, sale_line_ids, context=context):
                            if (sale_line.order_id.state not in
                                ('cancel', 'draft') and not
                                    sale_line.order_id.project2_id):
                                amount = amount + sale_line.price_subtotal
                            else:
                                if (sale_line.order_id.state != 'draft' and not
                                        sale_line.order_id.project2_id):
                                    if sale_line.order_id.id == sale.id:
                                        sl = sale_line
                                        sale_amount = (sale_amount +
                                                       sl.price_subtotal)
                        vals = {'total_recognized': amount}
                        financing_source_obj.write(
                            cr, uid, [financing_source_id], vals,
                            context=context)
                        financing_source = financing_source_obj.browse(
                            cr, uid, financing_source_id, context)
                        if financing_source.project_ids:
                            p_ids = financing_source.project_ids
                            for project_financing in p_ids:
                                tr = 0
                                if project_financing.project_id:
                                    for sl in sale_order_line_obj.browse(
                                            cr, uid, sale_line_ids, context):
                                        if (sl.order_id.state != 'cancel' and
                                                sl.order_id.state != 'draft'):
                                            if sl.order_id:
                                                if sl.order_id.project2_id:
                                                    o = sl.order_id
                                                    p_id = o.project2_id.id
                                                    pf = project_financing
                                                    p2_id = pf.project_id.id
                                                    if p_id == p2_id:
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
                        if financing_source.rd_preliminary:
                            ov = financing_source.grant_without_overheads
                            grant_without_overheads = ov - sale_amount
                            vals = {'grant_without_overheads':
                                    grant_without_overheads}
                            financing_source_obj.write(
                                cr, uid, financing_source_id, vals,
                                context=context)
                    else:
                        vals = {'total_recognized': 0}
                        financing_source_obj.write(
                            cr, uid, [financing_source_id], vals,
                            context=context)
                        financing_source = financing_source_obj.browse(
                            cr, uid, financing_source_id, context)
                        if financing_source.project_ids:
                            pro_ids = financing_source.project_ids
                            for project_financing in pro_ids:
                                vals = {'percentage_total_recognized': 0}
                                project_financing_obj.write(
                                    cr, uid, [project_financing.id], vals,
                                    context=context)
        return True
