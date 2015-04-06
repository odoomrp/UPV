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


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'state': fields.selection([('potential', 'Potential'),
                                   ('active', 'Active'),
                                   ('oldest', 'Oldest'),
                                   ('discarded', 'Discarded'),
                                   ], 'State', readonly=True),
        # Campo solo para proveedores, campo que indica si el proveedor está
        # homologado
        'approved': fields.boolean('Approved'),
        # Campo solo para proveedores, campo que indica la fecha de la
        # homologacion del proveedor
        'approval_date': fields.date('Approval Date'),
        # Campo solo para proveedores, campo que indica la fecha de la ultima
        # revision de la homologación del proveedor
        'last_revision_date': fields.date('Last Revision Date'),
        # Móvil
        'mobile': fields.char('Mobile', size=64),
    }

    _defaults = {'state': lambda *a: 'potential',
                 }

    def action_potential(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state': 'potential'})
        return True

    def action_active(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state': 'active'})
        return True

    def action_oldest(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state': 'oldest'})
        return True

    def action_discarded(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state': 'discarded'})
        return True
