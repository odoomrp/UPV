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
from openerp.tools.translate import _


class PurchaseOrder(orm.Model):
    _inherit = 'purchase.order'

    STATE_SELECTION = [('draft', 'Request for Quotation'),
                       ('request', 'Solicitud'),
                       ('wait', 'Waiting'),
                       ('confirmed', 'Waiting Approval'),
                       ('approved', 'Approved'),
                       ('except_picking', 'Shipping Exception'),
                       ('except_invoice', 'Invoice Exception'),
                       ('done', 'Done'),
                       ('cancel', 'Cancelled')
                       ]
    _columns = {
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True,
                                  help="The state of the purchase order or the"
                                  " quotation request. A quotation is a "
                                  "purchase order in a 'Draft' state. Then the"
                                  " order has to be confirmed by the user, the"
                                  " state switch to 'Confirmed'. Then the "
                                  "supplier must confirm the order to change "
                                  "the state to 'Approved'. When the purchase "
                                  "order is paid and received, the state "
                                  "becomes 'Done'. If a cancel action occurs "
                                  "in the invoice or in the reception of "
                                  "goods, the state becomes in exception.",
                                  select=True),
    }

    # Si cambian el pedido, valido que si han cambiado las lineas, también se
    # cambien en analitica
    def write(self, cr, uid, ids, vals, context=None):
        analytic_line_obj = self.pool['account.analytic.line']
        project_obj = self.pool['project.project']
        analytic_journal_obj = self.pool['account.analytic.journal']
        res = super(PurchaseOrder, self).write(cr, uid, ids, vals,
                                               context=context)
        for purchase in self.browse(cr, uid, ids, context):
            if purchase.state == 'request':
                for purchase_line in purchase.order_line:
                    if not purchase_line.line_financing_source_ids:
                        cond = [('purchase_order_line_id', '=',
                                 purchase_line.id),
                                ('expense_type', '=', 'purchase_expense')]
                        analytic_line_ids = analytic_line_obj.search(
                            cr, uid, cond, context=context)
                        if analytic_line_ids:
                            analytic_line_obj.unlink(
                                cr, uid, analytic_line_ids, context=context)
                    else:
                        w_contador = 0
                        fs_ids = purchase_line.line_financing_source_ids
                        for line_financing_source in fs_ids:
                            w_contador = w_contador + 1
                        w_contador2 = 0
                        w_importe2 = 0
                        w_importe3 = 0
                        for line_financing_source in fs_ids:
                            cond = [('purchase_order_line_id', '=',
                                     purchase_line.id),
                                    ('line_financing_source_id', '=',
                                     line_financing_source.id),
                                    ('expense_type', '=', 'purchase_expense')]
                            analytic_line_ids = analytic_line_obj.search(
                                cr, uid, cond, context=context)
                            ptmpl = purchase_line.product_id.product_tmpl_id
                            pincome = ptmpl.property_account_income
                            cat = purchase_line.product_id.categ_id
                            cincome = cat.property_account_income_categ
                            if analytic_line_ids:
                                if not pincome and not cincome:
                                    name1 = purchase_line.product_id.name
                                    p_id = purchase_line.product_id.id
                                    raise orm.except_orm(_('Error !'),
                                                         _('There is no '
                                                           'income account '
                                                           'defined for this '
                                                           'product: "%s" '
                                                           '(id:%d)') %
                                                         (name1, p_id))
                                else:
                                    if pincome:
                                        a = pincome.id
                                    else:
                                        a = cincome.id
                                # Ahora cojo el valor para journal_id, esto
                                # esta basado en la funcion
                                # on_change_unit_amount, del objeto
                                # account_analytic_line
                                cond = [('type', '=', 'purchase')]
                                j_ids = analytic_journal_obj.search(
                                    cr, uid, cond, context=context)
                                journal_id = j_ids and j_ids[0] or False
                                if not journal_id:
                                    raise orm.except_orm(_('Load In Analytical'
                                                           ' Notes ERROR'),
                                                         _('NOT ACCOUNT '
                                                           'ANALYTIC JOURNAL '
                                                           'FOUND'))
                                # Calculo importe con iva O sin iva
                                cond = [('analytic_account_id', '=',
                                         purchase_line.account_analytic_id.id)]
                                project_ids = project_obj.search(
                                    cr, uid, cond, context=context)
                                project = project_obj.browse(
                                    cr, uid, project_ids[0], context=context)
                                if not project.deductible_iva:
                                    # busco el iva
                                    w_taxes = 0
                                    for taxes in purchase_line.taxes_id:
                                        if taxes.name.find("iva") >= 0:
                                            w_taxes = taxes.amount
                                        else:
                                            if taxes.name.find("IVA") >= 0:
                                                w_taxes = taxes.amount
                                    psub = purchase_line.price_subtotal
                                    if w_taxes == 0:
                                        w_importe = psub
                                    else:
                                        w_iva = psub * w_taxes
                                        w_importe = psub + w_iva
                                else:
                                    w_importe = purchase_line.price_subtotal
                                w_contador2 = w_contador2 + 1
                                if w_contador == w_contador2:
                                    w_importe2 = w_importe - w_importe3
                                else:
                                    lfs = line_financing_source
                                    perc = lfs.line_financing_percentage
                                    w_importe2 = (w_importe * perc) / 100
                                    w_importe3 = w_importe3 + w_importe2
                                lfs = line_financing_source
                                fsl = lfs.financial_source_line_id
                                area = fsl.expense_area_id
                                line = {
                                    'account_id':
                                    purchase_line.account_analytic_id.id,
                                    'general_account_id': a,
                                    'journal_id': journal_id,
                                    'unit_amount': purchase_line.product_qty,
                                    'product_id': purchase_line.product_id.id,
                                    'product_uom_id':
                                    purchase_line.product_uom.id,
                                    'sale_amount':  0,
                                    'type': 'imputation',
                                    'expense_request': w_importe2,
                                    'expense_area_id': area.id,
                                    'account_analytic_line_financing_source'
                                    '_id': fsl.id,
                                    'account_analytic_line_budgetary_id':
                                    fsl.account_analytic_line_budgetary_id.id,
                                    'account_analytic_line_budgetary_readonly'
                                    '_id':
                                    fsl.account_analytic_line_budgetary_id.id
                                    }
                                analytic_line_obj.write(
                                    cr, uid, analytic_line_ids, line,
                                    context=context)
                            else:
                                # Si no existe la linea de analitica es que
                                # han dado de alta una linea de pedido estando
                                # en estado REQUEST Calculo el campo
                                # GENERAL_ACCOUNT_ID, esto esta basado en la
                                # funcion on_change_unit_amount, del objeto
                                # account_analytic_line
                                pl = purchase_line
                                ptmpl = pl.product_id.product_tmpl_id
                                pincome = ptmpl.property_account_income
                                cat = pl.product_id.categ_id
                                cincome = cat.property_account_income_categ
                                if not pincome and not cincome:
                                    name = pl.product_id.name
                                    p = pl.product_id.id
                                    raise orm.except_orm(_('Error !'),
                                                         _('There is no income'
                                                           ' account defined '
                                                           'for this product: '
                                                           '"%s" (id:%d)') %
                                                         (name, p))
                                else:
                                    if pincome:
                                        a = pincome.id
                                    else:
                                        a = cincome.id
                                # Ahora cojo el valor para journal_id, esto
                                # esta basado en la funcion
                                # on_change_unit_amount, del objeto
                                # account_analytic_line
                                cond = [('type', '=', 'purchase')]
                                j_ids = analytic_journal_obj.search(
                                    cr, uid, cond, context=context)
                                journal_id = j_ids and j_ids[0] or False
                                if not journal_id:
                                    raise orm.except_orm(_('Load In Analytical'
                                                           ' Notes ERROR'),
                                                         _('NOT ACCOUNT '
                                                           'ANALYTIC JOURNAL '
                                                           'FOUND'))
                                # Calculo importe con iva O sin iva
                                cond = [('analytic_account_id', '=',
                                         purchase_line.account_analytic_id.id)]
                                project_ids = project_obj.search(
                                    cr, uid, cond, context=context)
                                project = project_obj.browse(
                                    cr, uid, project_ids[0], context=context)
                                if not project.deductible_iva:
                                    # busco el iva
                                    w_taxes = 0
                                    for taxes in purchase_line.taxes_id:
                                        if taxes.name.find("iva") >= 0:
                                            w_taxes = taxes.amount
                                        else:
                                            if taxes.name.find("IVA") >= 0:
                                                w_taxes = taxes.amount
                                    psub = purchase_line.price_subtotal
                                    if w_taxes == 0:
                                        w_importe = psub
                                    else:
                                        w_iva = psub * w_taxes
                                        w_importe = psub + w_iva
                                else:
                                    w_importe = purchase_line.price_subtotal
                                w_contador2 = w_contador2 + 1
                                if w_contador == w_contador2:
                                    w_importe2 = w_importe - w_importe3
                                else:
                                    lfs = line_financing_source
                                    perc = lfs.line_financing_percentage
                                    w_importe2 = (w_importe * perc) / 100
                                    w_importe3 = w_importe3 + w_importe2
                                lfs = line_financing_source
                                fsl = lfs.financial_source_line_id
                                area = fsl.expense_area_id
                                line = {
                                    'name': purchase.name,
                                    'account_id':
                                    purchase_line.account_analytic_id.id,
                                    'general_account_id': a,
                                    'journal_id': journal_id,
                                    'unit_amount': purchase_line.product_qty,
                                    'product_id': purchase_line.product_id.id,
                                    'product_uom_id':
                                    purchase_line.product_uom.id,
                                    'sale_amount':  0,
                                    'type': 'imputation',
                                    'expense_request': w_importe2,
                                    'expense_area_id': area.id,
                                    'account_analytic_line_financing_source_'
                                    'id': fsl.id,
                                    'account_analytic_line_budgetary_id':
                                    fsl.account_analytic_line_budgetary_id.id,
                                    'account_analytic_line_budgetary_readonly'
                                    '_id':
                                    fsl.account_analytic_line_budgetary_id.id,
                                    'purchase_order_line_id': purchase_line.id,
                                    'line_financing_source_id':
                                    line_financing_source.id,
                                    'expense_type': 'purchase_expense'
                                }
                                analytic_line_obj.create(cr, uid, line,
                                                         context=context)
        return res

    # Funcion que se ejecuta cuando cancelo un pedido
    def action_cancel(self, cr, uid, ids, context=None):
        account_analytic_line_obj = self.pool['account.analytic.line']
        # Trato los pedidos de compra
        for purchase in self.browse(cr, uid, ids, context=context):
            analytic_lines_ids = account_analytic_line_obj.search(
                cr, uid, [('name', '=', purchase.name)], context=context)
            if analytic_lines_ids:
                account_analytic_line_obj.unlink(cr, uid, analytic_lines_ids,
                                                 context=context)
        super(PurchaseOrder, self).action_cancel(cr, uid, ids, context)
        return True

    # ESTA FUNCION SE EJECUTA CUANDO PASO EL PEDIDO DE COMPRA DE SOLICITUD DE
    # PRESUPUESTO A SOLICITUD
    def action_request(self, cr, uid, ids, context=None):
        account_analytic_line_obj = self.pool['account.analytic.line']
        project_obj = self.pool['project.project']
        analytic_journal_obj = self.pool['account.analytic.journal']
        # Trato los pedidos de compra
        for purchase in self.browse(cr, uid, ids, context=context):
            # Trato las lineas del pedido de compra
            for purchase_line in purchase.order_line:
                if purchase_line.line_financing_source_ids:
                    fs_ids = purchase_line.line_financing_source_ids
                    for line_financing_source in fs_ids:
                        # Calculo el campo GENERAL_ACCOUNT_ID, esto esta
                        # basado en la funcion on_change_unit_amount, del
                        # objeto account_analytic_line
                        ptmpl = purchase_line.product_id.product_tmpl_id
                        aexpense = ptmpl.property_account_expense
                        cat = purchase_line.product_id.categ_id
                        cexpense = cat.property_account_expense_categ
                        if not aexpense and not cexpense:
                            name = purchase_line.product_id.name
                            prod = purchase_line.product_id
                            raise orm.except_orm(_('Error !'),
                                                 _('There is no income account'
                                                   ' defined for this product:'
                                                   ' "%s" (id:%d)') %
                                                 (name, prod.id))
                        else:
                            if aexpense:
                                a = aexpense.id
                            else:
                                a = cexpense.id
                        # Ahora cojo el valor para journal_id, esto esta basado
                        # en la funcion on_change_unit_amount, del objeto
                        # account_analytic_line
                        cond = [('type', '=', 'purchase')]
                        j_ids = analytic_journal_obj.search(cr, uid, cond,
                                                            context=context)
                        journal_id = j_ids and j_ids[0] or False
                        if not journal_id:
                            raise orm.except_orm(_('Load In Analytical Notes '
                                                   'ERROR'),
                                                 _('NOT ACCOUNT ANALYTIC '
                                                   'JOURNAL FOUND'))
                        # Calculo importe con iva O sin iva
                        cond = [('analytic_account_id', '=',
                                 purchase_line.account_analytic_id.id)]
                        project_ids = project_obj.search(cr, uid, cond,
                                                         context=context)
                        project = project_obj.browse(
                            cr, uid, project_ids[0], context=context)
                        if not project.deductible_iva:
                            # busco el iva
                            w_taxes = 0
                            for taxes in purchase_line.taxes_id:
                                if taxes.name.find("iva") >= 0:
                                    w_taxes = taxes.amount
                                else:
                                    if taxes.name.find("IVA") >= 0:
                                        w_taxes = taxes.amount
                            if w_taxes == 0:
                                w_importe = purchase_line.price_subtotal
                            else:
                                w_iva = purchase_line.price_subtotal * w_taxes
                                w_importe = (purchase_line.price_subtotal +
                                             w_iva)
                        else:
                            w_importe = purchase_line.price_subtotal
                        perc = line_financing_source.line_financing_percentage
                        w_importe = (w_importe * perc) / 100
                        lfs = line_financing_source
                        fsl = lfs.financial_source_line_id
                        area = fsl.expense_area_id
                        line = {
                            'name': purchase.name,
                            'account_id': purchase_line.account_analytic_id.id,
                            'general_account_id': a,
                            'journal_id': journal_id,
                            'unit_amount': purchase_line.product_qty,
                            'product_id': purchase_line.product_id.id,
                            'product_uom_id': purchase_line.product_uom.id,
                            'sale_amount':  0,
                            'type': 'imputation',
                            'expense_request': w_importe,
                            'expense_area_id': area.id,
                            'account_analytic_line_financing_source_id':
                            fsl.id,
                            'account_analytic_line_budgetary_id':
                            fsl.account_analytic_line_budgetary_id.id,
                            'account_analytic_line_budgetary_readonly_id':
                            fsl. account_analytic_line_budgetary_id.id,
                            'purchase_order_line_id': purchase_line.id,
                            'line_financing_source_id':
                            line_financing_source.id,
                            'expense_type': 'purchase_expense'
                        }
                        account_analytic_line_obj.create(cr, uid, line,
                                                         context=context)
        self.write(cr, uid, ids, {'state': 'request'}, context=context)
        return True

    # CUANDO CONFIRMO EL PEDIDO DE COMPRA, PASA D ESTADO SOLICITUD  ESTADO
    # CONFIRMADO
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        account_analytic_line_obj = self.pool['account.analytic.line']
        project_obj = self.pool['project.project']
        financing_source_obj = self.pool['financing.source']
        account_journal_obj = self.pool['account.analytic.journal']
        # Llamo al metodo SUPER
        super(PurchaseOrder, self).wkf_confirm_order(cr, uid, ids, context)
        # Trato los pedidos de compra
        for purchase in self.browse(cr, uid, ids, context=context):
            # Trato las lineas del pedido de compra
            datas = {}
            for purchase_line in purchase.order_line:
                if purchase_line.line_financing_source_ids:
                    fs_ids = purchase_line.line_financing_source_ids
                    for line_financing_source in fs_ids:
                        cond = [('analytic_account_id', '=',
                                 purchase_line.account_analytic_id.id)]
                        project_ids = project_obj.search(cr, uid, cond,
                                                         context=context)
                        project = project_obj.browse(
                            cr, uid, project_ids[0], context=context)
                        if not project.deductible_iva:
                            # busco el iva
                            w_taxes = 0
                            for taxes in purchase_line.taxes_id:
                                if taxes.name.find("iva") >= 0:
                                    w_taxes = taxes.amount
                                else:
                                    if taxes.name.find("IVA") >= 0:
                                        w_taxes = taxes.amount
                            if w_taxes == 0:
                                w_imp = purchase_line.price_subtotal
                            else:
                                w_iva = purchase_line.price_subtotal * w_taxes
                                w_imp = purchase_line.price_subtotal + w_iva
                        else:
                            w_imp = purchase_line.price_subtotal
                        perc = line_financing_source.line_financing_percentage
                        w_imp = (w_imp * perc) / 100
                        w_found = 0
                        for data in datas:
                            datos_array = datas[data]
                            fs_id = datos_array['financing_source_id']
                            amount = datos_array['amount']
                            lfs = line_financing_source
                            fsl = lfs.financial_source_line_id
                            if fs_id == fsl.financing_source_id.id:
                                w_found = 1
                                amount = amount + w_imp
                                datas[data].update({'amount': amount})
                        if w_found == 0:
                            lfs = line_financing_source
                            fsl = lfs.financial_source_line_id
                            fs_id = fsl.financing_source_id.id
                            vals = {'financing_source_id': fs_id,
                                    'amount': w_imp}
                            datas[(fs_id)] = vals
            if datas:
                for data in datas:
                    datos_array = datas[data]
                    financing_source_id = datos_array['financing_source_id']
                    amount = datos_array['amount']
                    financing_source = financing_source_obj.browse(
                        cr, uid, financing_source_id, context=context)
                    if financing_source.availability_fund == 'granted':
                        if amount > financing_source.grant:
                            name = financing_source.name
                            raise orm.except_orm(_('Financing Source ERROR'),
                                                 _("The Financing Source '%s',"
                                                   " only have an amount "
                                                   "available for %s euros and"
                                                   " can not finance %s "
                                                   "euros") %
                                                 (name, financing_source.grant,
                                                  amount,))
                    if financing_source.availability_fund == 'accepted':
                        if (amount > (financing_source.total_recognized +
                                      financing_source.transfered)):
                            name = financing_source.name
                            t = (financing_source.total_recognized +
                                 financing_source.transfered)
                            raise orm.except_orm(_('Financing Source ERROR'),
                                                 _("The Financing Source '%s',"
                                                   " only have an amount "
                                                   "available for %s euros and"
                                                   " can not finance %s "
                                                   "euros") % (name, t,
                                                               amount))
                    if financing_source.availability_fund == 'charged':
                        if (amount > (financing_source.total_invoices_billed +
                                      financing_source.transfered)):
                            name = financing_source.name
                            t = (financing_source.total_invoices_billed +
                                 financing_source.transfered)
                            raise orm.except_orm(_('Financing Source ERROR'),
                                                 _("The Financing Source '%s',"
                                                   " only have an amount "
                                                   "available for %s euros and"
                                                   " can not finance %s "
                                                   "euros") %
                                                 (name, t, amount))
            for purchase_line in purchase.order_line:
                if purchase_line.line_financing_source_ids:
                    lfs_ids = purchase_line.line_financing_source_ids
                    for line_financing_source in lfs_ids:
                        # Control de Importes que puede financiar las Fuentes
                        # de financiación. Calculo el campo GENERAL_ACCOUNT_ID,
                        # esto esta basado en la funcion on_change_unit_amount,
                        # del objeto account_analytic_line
                        ptmpl = purchase_line.product_id.product_tmpl_id
                        aexpense = ptmpl.property_account_expense
                        cat = purchase_line.product_id.categ_id
                        cexpense = cat.property_account_expense_categ
                        if not aexpense and cexpense:
                            name = purchase_line.product_id.name
                            prod = purchase_line.product_id
                            raise orm.except_orm(_('Error !'),
                                                 _('There is no income account'
                                                   ' defined for this product:'
                                                   ' "%s" (id:%d)') %
                                                 (name, prod.id))
                        if aexpense:
                            a = aexpense.id
                        else:
                            a = cexpense.id
                        # Ahora cojo el valor para journal_id, esto esta basado
                        # en la funcion on_change_unit_amount, del objeto
                        # account_analytic_line
                        cond = [('type', '=', 'purchase')]
                        j_ids = account_journal_obj.search(cr, uid, cond,
                                                           context=context)
                        journal_id = j_ids and j_ids[0] or False
                        if not journal_id:
                            raise orm.except_orm(_('Load In Analytical Notes '
                                                   'ERROR'),
                                                 _('NOT ACCOUNT ANALYTIC '
                                                   'JOURNAL FOUND'))
                        # Calculo importe con iva O sin iva
                        cond = [('analytic_account_id', '=',
                                 purchase_line.account_analytic_id.id)]
                        project_ids = project_obj.search(cr, uid, cond,
                                                         context=context)
                        project = project_obj.browse(
                            cr, uid, project_ids[0], context=context)
                        if not project.deductible_iva:
                            # busco el iva
                            w_taxes = 0
                            for taxes in purchase_line.taxes_id:
                                if taxes.name.find("iva") >= 0:
                                    w_taxes = taxes.amount
                                else:
                                    if taxes.name.find("IVA") >= 0:
                                        w_taxes = taxes.amount
                            if w_taxes == 0:
                                w_importe = purchase_line.price_subtotal
                            else:
                                w_iva = purchase_line.price_subtotal * w_taxes
                                w_importe = (purchase_line.price_subtotal +
                                             w_iva)
                        else:
                            w_importe = purchase_line.price_subtotal
                        perc = line_financing_source.line_financing_percentage
                        w_importe = (w_importe * perc) / 100
                        lfs = line_financing_source
                        fsl = lfs.financial_source_line_id
                        area = fsl.expense_area_id
                        line = {'name': purchase.name,
                                'account_id':
                                purchase_line.account_analytic_id.id,
                                'general_account_id': a,
                                'journal_id': journal_id,
                                'unit_amount': purchase_line.product_qty,
                                'product_id': purchase_line.product_id.id,
                                'product_uom_id': purchase_line.product_uom.id,
                                'sale_amount':  0,
                                'type': 'imputation',
                                'expense_compromised': w_importe,
                                'expense_request': w_importe * (-1),
                                'expense_area_id': area.id,
                                'account_analytic_line_financing_source_id':
                                fsl.id,
                                'account_analytic_line_budgetary_id':
                                fsl.account_analytic_line_budgetary_id.id,
                                'account_analytic_line_budgetary_readonly_id':
                                fsl.account_analytic_line_budgetary_id.id,
                                'purchase_order_line_id': purchase_line.id,
                                'line_financing_source_id':
                                line_financing_source.id,
                                'expense_type': 'purchase_compromised'
                                }
                        account_analytic_line_obj.create(cr, uid, line,
                                                         context=context)
        return True

    # Cuando doy valores a la linea de factura de compra
    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        financing_line_obj = self.pool['line.financing.source']
        list = []
        for line in order_line.line_financing_source_ids:
            vals = {'purchase_order_line_id': False}
            new_id = financing_line_obj.copy(cr, uid, line.id, vals,
                                             context=context)
            list.append(new_id)
        return {
            'name': order_line.name,
            'account_id': account_id,
            'price_unit': order_line.price_unit or 0.0,
            'quantity': order_line.product_qty,
            'product_id': order_line.product_id.id or False,
            'uos_id': order_line.product_uom.id or False,
            'invoice_line_tax_id': [(6, 0,
                                     [x.id for x in order_line.taxes_id])],
            'account_analytic_id': order_line.account_analytic_id.id or False,
            'budgetary_line_id': order_line.budgetary_line_id.id or False,
            'line_financing_source_ids': [(6, 0, list)]
            }
