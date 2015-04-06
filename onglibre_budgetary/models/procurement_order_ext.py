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
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ProcurementOrder(orm.Model):
    _inherit = 'procurement.order'

    def make_po(self, cr, uid, ids, context=None):
        res = {}
        if context is None:
            context = {}
        simulation_cost_obj = self.pool['simulation.cost']
        simulation_cost_line_obj = self.pool['simulation.cost.line']
        sale_order_obj = self.pool['sale.order']
        sale_order_line_obj = self.pool['sale.order.line']
        for procurement in self.browse(cr, uid, ids, context=context):
            if (procurement.product_id.type == 'service' and
                    procurement.product_id.procure_method == 'make_to_stock'):
                continue
            if procurement.sale_line_id:
                # Accedo a la LINEA DEL PEDIDO DE VENTA
                sale_order_line = sale_order_line_obj.browse(
                    cr, uid, procurement.sale_line_id.id, context=context)
                # Accedo al PEDIDO DE VENTA
                sale_order = sale_order_obj.browse(
                    cr, uid, sale_order_line.order_id.id, context=context)
                # SI EL PEDIDO DE VENTA VIENE DE UNA SIMULACION, COJO LA ÚLTIMA
                # SIMULACIÓN ACTIVA QUE NO ESTE CANCELADA, O LA ÚLTIMA
                # HISTORIFICADA
                w_found = 0
                w_simulation_cost_id = 0
                w_maxid = 0
                if sale_order.simulation_cost_ids:
                    # Recorro todas las simulaciones asociadas al pedido de
                    # venta
                    for simulation_cost in sale_order.simulation_cost_ids:
                        if ((not simulation_cost.historical_ok) and
                                (simulation_cost.state not in ('canceled'))):
                            # Si es una simulación activa, me quedo con este
                            # id
                            w_found = 1
                            w_simulation_cost_id = simulation_cost.id
                        else:
                            # Si no ha encontrado la activa me quedo con la
                            # última simulación de coste historificada (la mas
                            # nueva, la de mayor id)
                            if w_found == 0:
                                if simulation_cost.id > w_maxid:
                                    w_maxid = simulation_cost.id
                    if w_simulation_cost_id == 0:
                        # Si no he encontrado una simulación de coste activa
                        # para ese pedido de venta
                        if w_maxid == 0:
                            # Si no he encontrado una simulación de coste
                            # historificada para eses pedido de venta
                            raise orm.except_orm(_('PROCUREMENT_ORDER: '
                                                   'Purchase Order Creation '
                                                   'Error'),
                                                 _('Simulation Cost not '
                                                   'found'))
                        else:
                            # Si no he encontrado una simulación de coste
                            # activa para ese pedido de venta, me quedo con el
                            # id de la simulación de coste historificada mas
                            # nueva
                            w_simulation_cost_id = w_maxid
                    # ACCEDO AL OBJETO SIMULACION
                    simulation_cost = simulation_cost_obj.browse(
                        cr, uid, w_simulation_cost_id, context=context)
            # Si EL PEDIDO DE VENTA VIENE DE UNA SIMULACIÓN, MIRO SI YA TIENE
            # ASOCIADO UN PROYECTO
            if procurement.sale_line_id:
                if sale_order.simulation_cost_ids:
                    if not sale_order.project2_id:
                            raise orm.except_orm(_('PROCUREMENT_ORDER: '
                                                   'Purchase Order Creation '
                                                   'Error'),
                                                 _('Project not found'))
                    else:
                        # SI EL PEDIDO DE VENTA TIENE UN PROYECTO ASOCIADO,
                        # COJO SU ID
                        project_project_id = sale_order.project2_id.id
            # SI EL PEDIDO DE VENTA NO VIENE DE UNA SIMULACION, HAGO EL
            # TRATAMIENTO DE ANTES
            if not procurement.sale_line_id:
                # Llamo con SUPER al método padre
                res = super(ProcurementOrder, self).make_po(
                    cr, uid, [procurement.id], context=context)
            else:
                if not sale_order.simulation_cost_ids:
                    # Llamo con SUPER al método padre
                    res = super(ProcurementOrder, self).make_po(
                        cr, uid, [procurement.id], context=context)
                else:
                    # SI EL PEDIDO DE VENTA VIENE DE UNA SIMULACION
                    if not sale_order_line.simulation_cost_line_id:
                        # SI LA LINEA DEL PEDIDO DE VENTA NO VIENE DE UNA LINEA
                        # DE SIMULACION DE COSTE
                        raise orm.except_orm(_('PROCUREMENT_ORDER: Purchase'
                                               ' Order Creation Error'),
                                             _('Sale Order line ID %s WITHOUT '
                                               'Simulation Cost Line') %
                                             sale_order_line.id)
                    else:
                        # SI LA LINEA DEL PEDIDO DE VENTA, VIENE DE UNA LINEA
                        # DE SIMULACIÓN DE COSTE, TRATO LA LINEA DE SIMULACION
                        # DE COSTE
                        line_id = sale_order_line.simulation_cost_line_id.id
                        simulation_cost_line = simulation_cost_line_obj.browse(
                            cr, uid, line_id, context=context)
                        # Si la linea de simulación de coste, se corresponde
                        # con la linea de simulación de coste perteneciente a
                        # la simulación de coste activa o a la última
                        # historificada, trato la linea.
                        if (simulation_cost_line.simulation_cost_id.id ==
                                w_simulation_cost_id):
                            if simulation_cost_line.supplier_id:
                                res = self._simuline_with_supplier(
                                    cr, uid, procurement, sale_order,
                                    w_simulation_cost_id, simulation_cost_line,
                                    project_project_id, sale_order_line, res,
                                    context=context)
                            else:
                                res = self._simuline_without_supplier(
                                    cr, uid, procurement, sale_order,
                                    w_simulation_cost_id, simulation_cost_line,
                                    project_project_id, sale_order_line, res,
                                    context=context)
        return res

    def _simuline_with_supplier(self, cr, uid, procurement, sale_order,
                                w_simulation_cost_id, simulation_cost_line,
                                project_project_id, sale_order_line, res,
                                context=None):
        partner_obj = self.pool['res.partner']
        prod_obj = self.pool['product.product']
        acc_pos_obj = self.pool['account.fiscal.position']
        seq_obj = self.pool['ir.sequence']
        warehouse_obj = self.pool['stock.warehouse']
        purchase_order_obj = self.pool['purchase.order']
        purchase_order_line_obj = self.pool['purchase.order.line']
        user_obj = self.pool['res.users']
        purchase_type_obj = self.pool['purchase.type']
        company = user_obj.browse(cr, uid, uid, context=context).company_id
        # SI EL PRODUCTO VIENE CON UN PROVEEDOR EN CONTRETO, TRATO ESE
        # PROVEEDOR MIRO SI YA EXISTE UN PEDIDO DE COMPRA PARA ESTE PROVEEDOR
        # QUE VIENE EN LA LÍNEA
        cond = [('sale_order_id', '=', sale_order.id),
                ('partner_id', '=', simulation_cost_line.supplier_id.id),
                ('state', '=', 'draft'),
                ('type_cost', '=', simulation_cost_line.type_cost)]
        purchase_order_id = purchase_order_obj.search(cr, uid, cond,
                                                      context=context)
        res_id = procurement.move_id.id
        partner = simulation_cost_line.supplier_id
        qty = simulation_cost_line.amount
        partner_id = partner.id
        address_id = partner_obj.address_get(
            cr, uid, [partner_id], ['delivery'])['delivery']
        pricelist_id = partner.property_product_pricelist_purchase.id
        cond = [('company_id', '=', procurement.company_id.id or company.id)]
        warehouse_id = warehouse_obj.search(cr, uid, cond, context=context)
        uom_id = simulation_cost_line.uom_id.id
        price = sale_order_line.price_unit
        schedule_date = self._get_purchase_schedule_date(
            cr, uid, procurement, company, context=context)
        purchase_date = self._get_purchase_order_date(
            cr, uid, procurement, company, schedule_date, context=context)
        context.update({'lang': partner.lang, 'partner_id': partner_id})
        product = prod_obj.browse(
            cr, uid, simulation_cost_line.product_id.id, context=context)
        product_tmpl = simulation_cost_line.product_id.product_tmpl_id
        taxes_ids = product_tmpl.supplier_taxes_id
        taxes = acc_pos_obj.map_tax(
            cr, uid, partner.property_account_position, taxes_ids)
        if not purchase_order_id:
            # SI NO EXISTE EL PEDIDO DE COMPRA PARA EL PROVEEDOR
            mydate = schedule_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            simu_id = simulation_cost_line.simulation_cost_id.id
            line_vals = {'name': simulation_cost_line.name,
                         'product_qty': qty,
                         'product_id': simulation_cost_line.product_id.id,
                         'product_uom': uom_id,
                         'price_unit': price or 0.0,
                         'date_planned': mydate,
                         'move_dest_id': res_id,
                         'notes': product.description_purchase,
                         'taxes_id': [(6, 0, taxes)],
                         'simulation_cost_line_ids': [(6, 0, simu_id)],
                         }
            # Cojo el tipo de pedido de compra
            if simulation_cost_line.type_cost == 'Others':
                cond = [('name', '=', 'Others')]
                purchase_type_ids = purchase_type_obj.search(cr, uid, cond,
                                                             context=context)
                if not purchase_type_ids:
                    raise orm.except_orm(_('PROCUREMENT_ORDER: Purchase Order'
                                           ' Creation Error'),
                                         _('Others literal not found in Table'
                                           ' Purchase Type'))
            if simulation_cost_line.type_cost == 'Amortization':
                cond = [('name', '=', 'Amortization')]
                purchase_type_ids = purchase_type_obj.search(cr, uid, cond,
                                                             context=context)
                if not purchase_type_ids:
                    raise orm.except_orm(_('PROCUREMENT_ORDER: Purchase Order'
                                           ' Creation Error'),
                                         _('Amortization literal not found in'
                                           ' Table Purchase Type'))
            purchase_type = purchase_type_obj.browse(
                cr, uid, purchase_type_ids[0], context=context)
            name = (seq_obj.get(cr, uid, 'purchase.order') or
                    _('PO: %s') % procurement.name)
            mydate = purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            fiscalpos = (partner.property_account_position and
                         partner.property_account_position.id or False)
            simulation = simulation_cost_line.simulation_cost_id
            po_vals = {'name': name,
                       'origin': (procurement.origin + ' - ' +
                                  simulation.simulation_number),
                       'partner_id': partner_id,
                       'partner_address_id': address_id,
                       'location_id': procurement.location_id.id,
                       'warehouse_id': (warehouse_id and warehouse_id[0] or
                                        False),
                       'pricelist_id': pricelist_id,
                       'date_order': mydate,
                       'company_id': procurement.company_id.id,
                       'fiscal_position': fiscalpos,
                       'type': purchase_type.id,
                       'type_cost': simulation_cost_line.type_cost
                       }
            aanalytic_id = procurement.sale_line_id.account_analytic_id.id
            fsource_line = procurement.sale_line_id.financial_source_line_id
            budgetaccount = fsource_line.account_analytic_line_budgetary_id.id
            line_vals.update({'account_analytic_id': aanalytic_id,
                              'budgetary_line_id': budgetaccount,
                              'financial_source_line_id': fsource_line.id})
            res[procurement.id] = self.create_procurement_purchase_order(
                cr, uid, procurement, po_vals, line_vals, context=context)
            vals = {'state': 'running',
                    'purchase_id': res[procurement.id]}
            self.write(cr, uid, [procurement.id], vals, context=context)
            # AÑADO EL ID DEL SUBPROYECTO AL PEDIDO DE COMPRA
            pc = res[procurement.id]
            vals = {'sale_order_id': sale_order.id,
                    'project2_id': project_project_id}
            purchase_order_obj.write(cr, uid, [pc], vals, context=context)
            # COJO EL ID DE LA LINEA DE PEDIDO DE COMPRA QUE SE HA DADO DE
            # ALTA
            cond = [('order_id', '=', pc)]
            purchase_order_line_ids = purchase_order_line_obj.search(
                cr, uid, cond, context=context)
            if not purchase_order_line_ids:
                raise orm.except_orm(_('PROCUREMENT_ORDER: Purchase Order'
                                       ' Creation Error'),
                                     _('Purchase Order Line not found(2)'))
        else:
            # SI EXISTE EL PEDIDO DE COMPRA PARA EL PROVEEDOR DOY DE ALTA UNA
            # LINEA EN LA LINEA DE PEDIDOS DE COMPRA
            mydate = schedule_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            simu_id = simulation_cost_line.simulation_cost_id.id
            line_vals = {'name': simulation_cost_line.name,
                         'order_id': purchase_order_id[0],
                         'product_qty': qty,
                         'product_id': simulation_cost_line.product_id.id,
                         'product_uom': uom_id,
                         'price_unit': price or 0.0,
                         'date_planned': mydate,
                         'move_dest_id': res_id,
                         'notes': product.description_purchase,
                         'taxes_id': [(6, 0, taxes)],
                         'simulation_cost_line_ids': [(6, 0, simu_id)],
                         }
            aanalytic_id = procurement.sale_line_id.account_analytic_id.id
            fsource_line = procurement.sale_line_id.financial_source_line_id
            budgetaccount = fsource_line.account_analytic_line_budgetary_id.id
            line_vals.update({'account_analytic_id': aanalytic_id,
                              'budgetary_line_id': budgetaccount,
                              'financial_source_line_id': fsource_line.id})
            purchase_order_line_obj.create(cr, uid, line_vals, context=context)
        return res

    def _simuline_without_supplier(self, cr, uid, procurement, sale_order,
                                   w_simulation_cost_id, simulation_cost_line,
                                   project_project_id, sale_order_line, res,
                                   context=None):
        partner_obj = self.pool['res.partner']
        prod_obj = self.pool['product.product']
        acc_pos_obj = self.pool['account.fiscal.position']
        seq_obj = self.pool['ir.sequence']
        warehouse_obj = self.pool['stock.warehouse']
        purchase_order_obj = self.pool['purchase.order']
        purchase_order_line_obj = self.pool['purchase.order.line']
        user_obj = self.pool['res.users']
        purchase_type_obj = self.pool['purchase.type']
        supplierinfo_obj = self.pool['product.supplierinfo']
        company = user_obj.browse(cr, uid, uid, context=context).company_id
        # SI EL PRODUCTO NO VIENE CON UN PROVEEDOR EN CONCRETO, TRATO TODOS
        # SUS PROVEEDORES
        cond = [('product_id', '=', simulation_cost_line.product_id.id)]
        supplierinfo_ids = supplierinfo_obj.search(
            cr, uid, cond, context=context, order='sequence')
        if not supplierinfo_ids:
            # Si no hay proveedores definidos para el producto, muestro el
            # error
            raise orm.except_orm(_('PROCUREMENT_ORDER: Purchase Order Creation'
                                   ' Error'),
                                 _('You must define one supplier for the '
                                   'product: %s') %
                                 simulation_cost_line.product_id.name)
        else:
            # TRATO TODOS LOS PROVEEDORES ENCONTRADOS PARA EL PRODUCTO,
            # CREARE UN PEDIDO DE COMPRA PARA CADA PROVEEDOR DE ESE
            # PRODUCTO
            for supplierinfo in supplierinfo_ids:
                supplierinfo_id = supplierinfo_obj.browse(
                    cr, uid, supplierinfo, context=context)
                partner = self.pool.get('res.partner')
                supplier = partner_obj.browse(cr, uid, supplierinfo_id.name.id,
                                              context=context)
                # MIRO SI YA EXISTE UN PEDIDO DE COMPRA PARA EL PROVEEDOR QUE
                # VE VIENE  DE LA BUSQUEDA ANTERIOR
                cond = [('sale_order_id', '=', sale_order.id),
                        ('partner_id', '=', supplier.id),
                        ('state', '=', 'draft'),
                        ('type_cost', '=', simulation_cost_line.type_cost)]
                purchase_order_id = purchase_order_obj.search(cr, uid, cond,
                                                              context=context)
                res_id = procurement.move_id.id
                # Cojo al proveedor
                partner = partner_obj.browse(cr, uid, supplierinfo_id.name.id,
                                             context=context)
                # Fin coger proveedor
                qty = simulation_cost_line.amount
                partner_id = partner.id
                address_id = partner_obj.address_get(
                    cr, uid, [partner_id], ['delivery'])['delivery']
                pricelist_id = partner.property_product_pricelist_purchase.id
                cond = [('company_id', '=', procurement.company_id.id or
                         company.id)]
                warehouse_id = warehouse_obj.search(cr, uid, cond,
                                                    context=context)
                uom_id = simulation_cost_line.uom_id.id
                price = sale_order_line.price_unit
                schedule_date = self._get_purchase_schedule_date(
                    cr, uid, procurement, company, context=context)
                purchase_date = self._get_purchase_order_date(
                    cr, uid, procurement, company, schedule_date,
                    context=context)
                context.update({'lang': partner.lang,
                                'partner_id': partner_id})
                product = prod_obj.browse(
                    cr, uid, simulation_cost_line.product_id.id,
                    context=context)
                product_tmpl = simulation_cost_line.product_id.product_tmpl_id
                taxes_ids = product_tmpl.supplier_taxes_id
                taxes = acc_pos_obj.map_tax(
                    cr, uid, partner.property_account_position, taxes_ids)
                if not purchase_order_id:
                    # SI NO EXISTE EL PEDIDO DE COMPRA PARA EL PROVEEDOR
                    product = simulation_cost_line.product_id
                    da = schedule_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    simu_id = simulation_cost_line.simulation_cost_id.id
                    line_vals = {'name': simulation_cost_line.name,
                                 'product_qty': qty,
                                 'product_id': product.id,
                                 'product_uom': uom_id,
                                 'price_unit': price or 0.0,
                                 'date_planned': da,
                                 'move_dest_id': res_id,
                                 'notes': product.description_purchase,
                                 'taxes_id': [(6, 0, taxes)],
                                 'simulation_cost_line_ids': [(6, 0, simu_id)],
                                 }
                    # Cojo el tipo de pedido de compra
                    if simulation_cost_line.type_cost == 'Others':
                        cond = [('name', '=', 'Others')]
                        purchase_type_ids = purchase_type_obj.search(
                            cr, uid, cond, context=context)
                        if not purchase_type_ids:
                            raise orm.except_orm(_('PROCUREMENT_ORDER: '
                                                   'Purchase Order Creation '
                                                   'Error'),
                                                 _('Others literal not found '
                                                   'in Table Purchase Type'))
                    if simulation_cost_line.type_cost == 'Amortization':
                        cond = [('name', '=', 'Amortization')]
                        purchase_type_ids = purchase_type_obj.search(
                            cr, uid, cond, context=context)
                        if not purchase_type_ids:
                            raise orm.except_orm(_('PROCUREMENT_ORDER: '
                                                   'Purchase Order Creation '
                                                   'Error'),
                                                 _('Amortization literal not '
                                                   'found in Table Purchase '
                                                   'Type'))
                    purchase_type = purchase_type_obj.browse(
                        cr, uid, purchase_type_ids[0], context=context)
                    name = (seq_obj.get(cr, uid, 'purchase.order') or
                            _('PO: %s') % procurement.name)
                    da = purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    fpos = (partner.property_account_position and
                            partner.property_account_position.id or False)
                    simulation = simulation_cost_line.simulation_cost_id
                    po_vals = {'name': name,
                               'origin': (procurement.origin + ' - ' +
                                          simulation.simulation_number),
                               'partner_id': partner_id,
                               'partner_address_id': address_id,
                               'location_id': procurement.location_id.id,
                               'warehouse_id': (warehouse_id and
                                                warehouse_id[0] or False),
                               'pricelist_id': pricelist_id,
                               'date_order': da,
                               'company_id': procurement.company_id.id,
                               'fiscal_position': fpos,
                               'type': purchase_type.id,
                               'type_cost': simulation_cost_line.type_cost
                               }
                    p = procurement
                    aanalytic_id = p.sale_line_id.account_analytic_id.id
                    fsl = p.sale_line_id.financial_source_line_id
                    budgetaccount = fsl.account_analytic_line_budgetary_id.id
                    line_vals.update({'account_analytic_id': aanalytic_id,
                                      'budgetary_line_id': budgetaccount,
                                      'financial_source_line_id': fsl.id})
                    pr_id = procurement.id
                    res[pr_id] = self.create_procurement_purchase_order(
                        cr, uid, procurement, po_vals, line_vals,
                        context=context)
                    vals = {'state': 'running',
                            'purchase_id': res[procurement.id]}
                    self.write(cr, uid, [procurement.id], vals,
                               context=context)
                    # AÑADO EL ID DEL SUBPROYECTO AL PEDIDO DE COMPRA
                    pc = res[procurement.id]
                    vals = {'sale_order_id': sale_order.id,
                            'project2_id': project_project_id}
                    purchase_order_obj.write(cr, uid, [pc], vals,
                                             context=context)
                    # COJO EL ID DE LA LINEA DE PEDIDO DE COMPRA QUE SE HA
                    # DADO DE ALTA
                    purchase_order_line_ids = purchase_order_line_obj.search(
                        cr, uid, [('order_id', '=', pc)], context=context)
                    if not purchase_order_line_ids:
                        raise orm.except_orm(_('PROCUREMENT_ORDER: '
                                               'Purchase Order Creation '
                                               'Error'),
                                             _('Purchase Order Line not '
                                               'found(2)'))
                else:
                    # SI EXISTE EL PEDIDO DE COMPRA PARA EL PROVEEDOR DOY DE
                    # ALTA UNA LINEA EN LA LINEA DE PEDIDOS DE COMPRA
                    product_id = simulation_cost_line.product_id.id
                    d = schedule_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    simu_id = simulation_cost_line.simulation_cost_id.id
                    line_vals = {'name': simulation_cost_line.name,
                                 'order_id': purchase_order_id[0],
                                 'product_qty': qty,
                                 'product_id': product_id,
                                 'product_uom': uom_id,
                                 'price_unit': price or 0.0,
                                 'date_planned': d,
                                 'move_dest_id': res_id,
                                 'notes': product.description_purchase,
                                 'taxes_id': [(6, 0, taxes)],
                                 'simulation_cost_line_ids': [(6, 0, simu_id)],
                                 }
                    p = procurement
                    aanalytic_id = p.sale_line_id.account_analytic_id.id
                    fsl = p.sale_line_id.financial_source_line_id
                    budgetaccount = fsl.account_analytic_line_budgetary_id.id
                    line_vals.update({'account_analytic_id': aanalytic_id,
                                      'budgetary_line_id': budgetaccount,
                                      'financial_source_line_id': fsl.id})
                    purchase_order_line_obj.create(cr, uid, line_vals,
                                                   context=context)
        return res

    # HEREDO ESTA FUNCION QUE CREA LA ORDEN DE PEDIDO DE COMPRA
    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals,
                                          line_vals, context=None):
        purchase_type_obj = self.pool['purchase.type']
        purchase_order_obj = self.pool['purchase.order']
        # MODIFICACION: Si no viene un parametro con nombre 'type', significa
        # que no viene de una simulación, por lo tanto lo ponemos el campo
        # "type" como de compras (este campo indica que tipo de de pedido de
        # compra es, y servirá para generar el código del pedido de compra
        if 'type' not in po_vals:
            purchase_type_ids = purchase_type_obj.search(
                cr, uid, [('name', '=', 'Purchase')], context=context)
            if not purchase_type_ids:
                raise orm.except_orm(_('PROCUREMENT_ORDER: Purchase Order '
                                       'Creation Error'),
                                     _('Purchase literal not found in Table '
                                       'Purchase Type'))
            else:
                purchase_type = purchase_type_obj.browse(
                    cr, uid, purchase_type_ids[0], context=context)
                po_vals.update({'type': purchase_type.id})
        po_vals.update({'order_line': [(0, 0, line_vals)]})
        return purchase_order_obj.create(cr, uid, po_vals, context=context)

    def _create_service_task(self, cr, uid, procurement, context=None):
        project_task_obj = self.pool['project.task']
        simulation_cost_obj = self.pool['simulation.cost']
        simulation_cost_line_obj = self.pool['simulation.cost.line']
        sale_order_obj = self.pool['sale.order']
        sale_order_line_obj = self.pool['sale.order.line']
        project_project_obj = self.pool['project.project']
        product_obj = self.pool['product.product']
        task_id = False
        if (procurement.product_id.type == 'service' and
                procurement.product_id.procure_method == 'make_to_stock'):
            return task_id
        # Accedo a la LINEA DEL PEDIDO DE VENTA
        sale_order_line = sale_order_line_obj.browse(
            cr, uid, procurement.sale_line_id.id, context=context)
        # Accedo al PEDIDO DE VENTA
        sale_order = sale_order_obj.browse(
            cr, uid, sale_order_line.order_id.id, context=context)
        # SI EL PEDIDO DE VENTA VIENE DE UNA SIMULACION, COJO LA ÚLTIMA
        # SIMULACIÓN ACTIVA QUE NO ESTE CANCELADA, O LA ÚLTIMA
        # HITORIFICADA
        w_found = 0
        w_simulation_cost_id = 0
        w_maxid = 0
        if sale_order.simulation_cost_ids:
            # Recorro todas las simulaciones asociadas al pedido de venta
            for simulation_cost in sale_order.simulation_cost_ids:
                if ((not simulation_cost.historical_ok) and
                        (simulation_cost.state not in ('canceled'))):
                    # Si es una simulación activa, me quedo con este id
                    w_found = 1
                    w_simulation_cost_id = simulation_cost.id
                else:
                    # Si no ha encontrado la activa me quedo con la última
                    # simulación de coste historificada (la mas nueva, la
                    # de mayor id)
                    if w_found == 0:
                        if simulation_cost.id > w_maxid:
                            w_maxid = simulation_cost.id
            if w_simulation_cost_id == 0:
                # Si no he encontrado una simulación de coste activa para
                # ese pedido de venta
                if w_maxid == 0:
                    # Si no he encontrado una simulación de coste
                    # historificada para ese pedido de venta
                    raise orm.except_orm(_('PROCUREMENT_ORDER: Project '
                                           'Creation Error(2)'),
                                         _('Simulation Cost not found'))
                else:
                    # Si no he encontrado una simulación de coste activa
                    # para ese pedido de venta, me quedo con el id de la
                    # simulación de coste historificada mas nueva
                    w_simulation_cost_id = w_maxid
        # Si EL PEDIDO DE VENTA VIENE DE UNA SIMULACIÓN, MIRO SI YA TIENE
        # ASOCIADO UN PROYECTO
        if sale_order.simulation_cost_ids:
            if not sale_order.project2_id:
                raise orm.except_orm(_('PROCUREMENT_ORDER: Project '
                                       'Creation Error(2)'),
                                     _('Project not found'))
            else:
                # SI EL PEDIDO DE VENTA TIENE UN PROYECTO ASOCIADO, COJO
                # SU ID
                project_project_id = sale_order.project2_id.id
                # Ahora cojo su cuenta analítica
                project_project = project_project_obj.browse(
                    cr, uid,  project_project_id, context=context)
                aacount_id = project_project.analytic_account_id.id
                account_analytic_account_id = aacount_id

        # SI EL PEDIDO DE VENTA NO VIENE DE UNA SIMULACION, HAGO EL
        # TRATAMIENTO DE ANTES
        if not sale_order.simulation_cost_ids:
            # Llamo con SUPER al método padre
            task_id = super(ProcurementOrder, self)._create_service_task(
                cr, uid, procurement, context=context)
        else:
            # SI EL PEDIDO DE VENTA VIENE DE UNA SIMULACION
            if not sale_order_line.simulation_cost_line_id:
                raise orm.except_orm(_('PROCUREMENT_ORDER: Task Creation '
                                       'Error'),
                                     _('Sale Order line ID %s WITHOUT Simu'
                                       'lation Cost Line') %
                                     sale_order_line.id)
            else:
                # ACCEDO A LOS DATOS DE LA SIMULACION DE COSTES
                simulation_cost = simulation_cost_obj.browse(
                    cr, uid, w_simulation_cost_id, context=context)
                # SI LA LINEA DEL PEDIDO DE VENTA, VIENE DE UNA LINEA DE
                # SIMULACIÓN DE COSTE, TRATO TODAS LA LINEAS DE SIMULACION
                # DE COSTE
                simulation_cost_line = simulation_cost_line_obj.browse(
                    cr, uid, sale_order_line.simulation_cost_line_id.id,
                    context=context)
                # Si la linea de simulación de coste, se corresponde con
                # la linea de simulación de coste perteneciente a la
                # simulación de coste activa o a la última historificada,
                # trato la linea.
                if simulation_cost_line.simulation_cost_id.id:
                    simu_id = simulation_cost_line.simulation_cost_id.id
                else:
                    if simulation_cost_line.simulation_cost_id.id:
                        simline = simulation_cost_line
                        simu_id = simline.simulation_cost_id.id
                    else:
                        raise orm.except_orm(_('PROCUREMENT_ORDER: Project'
                                               ' Creation Error'),
                                             _('Task: %s') %
                                             str(simulation_cost_line.id))
                if simu_id == w_simulation_cost_id:
                    simline = simulation_cost_line
                    if not simline.estimated_date_purchase_completion:
                        raise orm.except_orm(_('PROCUREMENT_ORDER: Project'
                                               ' Creation Error(2)'),
                                             _('Simulation Cost not found'
                                               ' in cost line ID: %s WITH'
                                               'OUT estimated date task '
                                               'completion') %
                                             simulation_cost_line.name)
                    # COJO EL NOMBRE DEL PRODUCTO DE VENTA DE LA LINEA DE
                    # SIMULACION DE COSTES
                    cost_product = product_obj.browse(
                        cr, uid, simulation_cost_line.product_id.id,
                        context=context)
                    sale_product = product_obj.browse(
                        cr, uid, simulation_cost_line.product_sale_id.id,
                        context=context)
                    # DOY DE ALTA LA TAREA PARA EL SUBPROYECTO
                    aacount_id = account_analytic_account_id
                    simuline = simulation_cost_line
                    date = simuline.estimated_date_purchase_completion
                    user = simuline.product_id.product_manager.id
                    vals = {'account_analytic_account_id': aacount_id,
                            'name': simulation_cost_line.name,
                            'date_deadline': date,
                            'planned_hours': simulation_cost_line.amount,
                            'remaining_hours': simulation_cost_line.amount,
                            'user_id': user,
                            'notes': procurement.note,
                            'procurement_id': procurement.id,
                            'description': procurement.note,
                            'project_id':  project_project_id,
                            'company_id': procurement.company_id.id,
                            'cost_product_name': cost_product.name,
                            'sale_product_name': sale_product.name,
                            }
                    task_id = project_task_obj.create(cr, uid, vals,
                                                      context=context)
                    vals = {'task_id': task_id,
                            'state': 'running'}
                    self.write(cr, uid, [procurement.id], vals,
                               context=context)
        return task_id
