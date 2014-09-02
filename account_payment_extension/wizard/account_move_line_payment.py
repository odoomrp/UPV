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


class AccountMoveLinePayment(orm.TransientModel):
    _name = "account.move.line.payment"
    _description = "Pay Account Move Lines"

    def pay_move_lines(self, cr, uid, ids, context=None):
        obj_move_line = self.pool['account.move.line']
        if context is None:
            context = {}
        res = obj_move_line.pay_move_lines(
            cr, uid, context['active_ids'], context)
        res['nodestroy'] = False
        return res
