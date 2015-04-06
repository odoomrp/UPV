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
import datetime


class ProjectJustification(orm.Model):
    _name = 'project.justification'
    _rec_name = 'sequence'
    _columns = {
        'state':
            fields.selection([('draft', 'Draft'),
                              ('done', 'Done')], string="State",
                             required=True, readonly=True),
        'sequence': fields.char('Justification num.', size=64, required=True),
        'year': fields.integer('Year'),
        'project_id': fields.many2one('project.project', 'Project'),
        'program_id':
            fields.related('project_id', 'type_program_id', type="many2one",
                           relation='type.program', string='Call'),
        'justification_line_ids':
            fields.many2many('account.invoice.line',
                             'invoice_justification_lines_rel',
                             'justification_id', 'invoice_line_id',
                             'Invoice Lines',
                             domain="[('invoice_type', '=', 'in_invoice')]")
    }

    _defaults = {
        'state': lambda *a: 'draft',
        'year': lambda * a: datetime.datetime.now().year,
        'sequence': lambda obj, cr, uid, context:
            obj.pool.get('ir.sequence').get(cr, uid, 'project.justification')
    }

    def write(self, cr, uid, ids, vals, context=None):
        invoice_line_obj = self.pool['account.invoice.line']
        justified_import_obj = self.pool['justified.invoice.import']
        if vals is None:
            vals = {}
        for id in ids:
            if 'justification_line_ids' in vals:
                for line in vals['justification_line_ids'][0][2]:
                    cond = [('justification_id', '=', id),
                            ('invoice_line_id', '=', line)]
                    imported_list = justified_import_obj.search(
                        cr, uid, cond, context=context)
                    if not imported_list:
                        line_o = invoice_line_obj.browse(cr, uid, line,
                                                         context=context)
                        jimport = line_o.to_justified_import
                        line_vals = {'justification_id': id,
                                     'invoice_line_id': line,
                                     'to_justified_import': jimport
                                     }
                        justified_import_obj.create(cr, uid, line_vals,
                                                    context=context)
        return super(ProjectJustification, self).write(cr, uid, ids, vals,
                                                       context)

    def create(self, cr, uid, vals, context=None):
        invoice_line_obj = self.pool['account.invoice.line']
        justified_import_obj = self.pool['justified.invoice.import']
        res = super(ProjectJustification, self).create(cr, uid, vals, context)
        if vals is None:
            vals = {}
        if 'justification_line_ids' in vals:
            for line in vals['justification_line_ids'][0][2]:
                line_o = invoice_line_obj.browse(cr, uid, line, context)
                jimport = line_o.to_justified_import
                line_vals = {'justification_id': res,
                             'invoice_line_id': line,
                             'to_justified_import': jimport}
                justified_import_obj.create(cr, uid, line_vals, context)
        return res

    def on_change_project(self, cr, uid, ids, project_id, context=None):
        project_obj = self.pool['project.project']
        res = {}
        if project_id:
            project = project_obj.browse(cr, uid, project_id, context)
            res.update({'program_id': project.type_program_id.id})
        return {'value': res}

    def set_done(self, cr, uid, ids, context=None):
        justified_import_obj = self.pool['justified.invoice.import']
        invoice_line_obj = self.pool['account.invoice.line']
        self.write(cr, uid, ids, {'state': 'done'}, context)
        for id in ids:
            id_o = self.browse(cr, uid, id, context)
            for justification_line in id_o.justification_line_ids:
                cond = [('justification_id', '=', id),
                        ('invoice_line_id', '=', justification_line.id)]
                justifi_import_id = justified_import_obj.search(cr, uid, cond,
                                                                context)
                if justifi_import_id:
                    jus_import = justified_import_obj.browse(
                        cr, uid, justifi_import_id[0],
                        context).to_justified_import
                    total_import = (justification_line.justified_import +
                                    jus_import)
                    percent = (total_import /
                               justification_line.price_subtotal) * 100
                    vals = {'justified_import': total_import,
                            'justified_percent': percent}
                    invoice_line_obj.write(cr, uid, justification_line.id,
                                           vals, context)
        return True

    def set_draft(self, cr, uid, ids, context=None):
        invoice_line_obj = self.pool['account.invoice.line']
        justified_import_obj = self.pool['justified.invoice.import']
        self.write(cr, uid, ids, {'state': 'draft'}, context)
        for id in ids:
            id_o = self.browse(cr, uid, id, context)
            for justification_line in id_o.justification_line_ids:
                cond = [('justification_id', '=', id),
                        ('invoice_line_id', '=', justification_line.id)]
                justifi_import_id = justified_import_obj.search(cr, uid, cond,
                                                                context)
                if justifi_import_id:
                    jus_import = justified_import_obj.browse(
                        cr, uid, justifi_import_id[0],
                        context).to_justified_import
                    total_import = (justification_line.justified_import -
                                    jus_import)
                    percent = (total_import /
                               justification_line.price_subtotal) * 100
                    vals = {'justified_import': total_import,
                            'justified_percent': percent}
                    invoice_line_obj.write(
                        cr, uid, justification_line.id, vals, context)
        return True


class JustifiedInvoiceImport(orm.Model):
    _name = "justified.invoice.import"

    _columns = {
        'invoice_line_id': fields.many2one('account.invoice.line',
                                           'Invoice line'),
        'justification_id': fields.many2one('project.justification',
                                            'Justification'),
        'to_justified_import':
            fields.float('Import to justified',
                         digits_compute=dp.get_precision('Account')),
    }
