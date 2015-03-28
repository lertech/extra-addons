# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

class ir_model(osv.osv):
    
    def _report_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for model in self.browse(cr, uid, ids):
            res[model.id] = self.pool.get("ir.actions.report.xml").search(cr, uid, [('model', '=', model.model)])
        return res
    
    _name = 'ir.model'
    _inherit = 'ir.model'
    _columns = {
            'report_ids': fields.function(_report_ids, type='one2many', obj='ir.actions.report.xml', string='Reports'),
        }