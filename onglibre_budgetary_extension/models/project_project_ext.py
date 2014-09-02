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


class ProjectProject(orm.Model):
    _inherit = 'project.project'

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, int):
            ids = [ids]
        result = super(ProjectProject, self).write(cr, uid, ids, vals, context)
        project_financing_obj = self.pool['project.financing']
        project_financing_ids = project_financing_obj.search(
            cr, uid, [('project_id', '=', ids[0])], context=context)
        project_financing_obj.write(cr, uid, project_financing_ids, {},
                                    context=context)
        return result
