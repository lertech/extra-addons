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
    
    def _get_default_cubic_report(self, cr, uid, model, context=None):
        res = []
        model_obj = self.pool.get(model)
        for field in model_obj._all_columns:
            if model_obj._all_columns[field].column._type in ('binary','text','one2many','many2many'):
                continue
            res.append({'name':field,'type':'field'})
        return """{
'detail'  :  [
            %s
            ],
'summary' :  [
           ]
}"""%str(res)[1:-1]
    
    def _get_cubic_report(self, cr, uid, model, context=None):
        model_id = self.search(cr, uid, [('model','=',model)],context=context)[0]
        model_brw = self.browse(cr, uid, model_id, context=context)
        if model_brw.custom_cubic_report:
            res = model_brw.custom_cubic_report_src
        else:
            res = self._get_default_cubic_report(cr, uid, model, context=context)
        return res
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('custom_cubic_report',False):
            res = []
            for field in vals.get('field_id'):
                name = field[2]['name']
                res+= [{'name':name, 'type':'field'}]
            vals['custom_cubic_report_src'] = str(res)
        return super(ir_model, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if ids and vals.get('custom_cubic_report',False):
            model = self.browse(cr, uid, ids[0], context=context)
            if not (model.custom_cubic_report_src or vals.get('custom_cubic_report_src',False)):
                vals['custom_cubic_report_src'] = self._get_default_cubic_report(cr, uid, model.model, context=context)
        return super(ir_model, self).write(cr, uid, ids, vals, context=context)
    
    _name = 'ir.model'
    _inherit = 'ir.model'
    _columns = {
            'custom_cubic_report': fields.boolean('Customize Cubic Report'),
            'custom_cubic_report_src': fields.text('Customized Cubic Report'),
        }
    _defaults = {
            'custom_cubic_report': False,
        }