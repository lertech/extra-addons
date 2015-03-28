# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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

from osv import osv, fields
import binascii
import netsvc

class report_xml(osv.osv):
    
    def _report_content_txt(self, cr, uid, ids, name, arg, context=None):
        if context is None: context = {}
        res = {}
        context['bin_size'] = False
        for report in self.read(cr,uid,ids,['report_rml_content'],context=context):
            data = report['report_rml_content']
            res[report['id']] = data!=u'False' and data or ''
        return res
    
    def _report_content_txt_inv(self, cr, uid, id, name, value, arg, context=None):
        self.write(cr,uid,id,{'report_rml_content':str(value or '')},context=context)
    
    def _menu_show(self, cr, uid, ids, name, arg, context=None):
        res = {}
        values_obj = self.pool.get('ir.values')
        for report in self.browse(cr, uid, ids, context=context):
            values_ids = values_obj.search(cr, uid, [('key','=','action'),
                                                     ('key2','=','client_print_multi'),
                                                     ('model','=',report.model),
                                                     ('res_id','=',False),
                                                     ('value','=','%s,%s'%(report.act_window_id and report.act_window_id.type or report.type, report.act_window_id and report.act_window_id.id or report.id))] , context=context)
            res[report.id] = bool(values_ids)
        return res
    
    def _menu_show_inv(self, cr, uid, id, name, value, arg, context=None):
        report = self.browse(cr, uid, id, context=context)
        values_obj = self.pool.get('ir.values')
        act_obj = self.pool.get('ir.actions.act_window')
        values_ids = values_obj.search(cr, uid, [('key','=','action'),
                                                 ('key2','=','client_print_multi'),
                                                 ('model','=',report.model),
                                                 ('res_id','=',False),
                                                 ('value','=','%s,%s'%(report.act_window_id and report.act_window_id.type or report.type, report.act_window_id and report.act_window_id.id or report.id))] , context=context)
        if value and not values_ids:
            values_obj.create(cr, uid, {'key': 'action',
                                         'key2': 'client_print_multi',
                                         'model': report.model,
                                         'value': '%s,%s'%(report.act_window_id and report.act_window_id.type or report.type, report.act_window_id and report.act_window_id.id or report.id),
                                         'name': report.name}, context=context)
            if report.act_window_id:
                act_ctx = eval(report.act_window_id.context)
                act_ctx['cubicReport'] = {'id': report.id}
                act_obj.write(cr, uid, [report.act_window_id.id], {'context': str(act_ctx)}, context=context)
        elif not value and values_ids:
            values_obj.unlink(cr, uid, values_ids, context=context)
            if report.act_window_id:
                act_ctx = eval(report.act_window_id.context)
                if act_ctx.has_key('cubicReport'):
                    del act_ctx['cubicReport']
                act_obj.write(cr, uid, [report.act_window_id.id], {'context': str(act_ctx)}, context=context)
    
    _name = 'ir.actions.report.xml'
    _inherit = 'ir.actions.report.xml'
    _columns = {
            'report_rml_content_txt': fields.function(_report_content_txt, fnct_inv=_report_content_txt_inv, type='text', string='Report Edit'),
            'menu_show': fields.function(_menu_show, fnct_inv=_menu_show_inv, type='boolean',string='Show in Menu', help="Show this report on menu related to the madel"),
            'act_window_id': fields.many2one('ir.actions.act_window',string="Params Window"),
        }
    _defaults = {
        }
    
    def write(self, cr, uid, ids, vals, context=None):
        values_obj = self.pool.get('ir.values')
        act_obj = self.pool.get('ir.actions.act_window')
        if vals.has_key('model') or vals.has_key('name') or vals.has_key('act_window_id'):
            for report in self.browse(cr, uid, ids, context=context):
                values_ids = values_obj.search(cr, uid, [('key','=','action'),
                                                     ('key2','=','client_print_multi'),
                                                     ('model','=',report.model),
                                                     ('res_id','=',False),
                                                     ('value','=','%s,%s'%(report.act_window_id and report.act_window_id.type or report.type, report.act_window_id and report.act_window_id.id or report.id))] , context=context)
                if values_ids:
                    act_id = vals.get('act_window_id', report.act_window_id.id)
                    if act_id:
                        act = self.pool.get('ir.actions.act_window').browse(cr, uid, act_id, context=context)
                    else:
                        act = report
                    values_obj.write(cr, uid, values_ids, {'model':vals.get('model',report.model),
                                                           'name': vals.get('name',report.name),
                                                           'value': '%s,%s'%(act.type,act.id)}, context=context)
                    if vals.has_key('act_window_id'):
                        if report.act_window_id:
                            act_ctx = eval(report.act_window_id.context)
                            if act_ctx.has_key('cubicReport'):
                                del act_ctx['cubicReport']
                            act_obj.write(cr, uid, [report.act_window_id.id], {'context': str(act_ctx)}, context=context)
                        if act_id:
                            act_ctx = eval(act.context)
                            act_ctx['cubicReport'] = {'id': report.id}
                            act_obj.write(cr, uid, [act.id], {'context': str(act_ctx)}, context=context)
        return super(report_xml, self).write(cr, uid, ids, vals, context)
    
    def unlink(self, cr, uid, ids, context=None):
        values_obj = self.pool.get('ir.values')
        act_obj = self.pool.get('ir.actions.act_window')
        for report in self.browse(cr, uid, ids, context=context):
            values_ids = values_obj.search(cr, uid, [('key','=','action'),
                                                 ('key2','=','client_print_multi'),
                                                 ('model','=',report.model),
                                                 ('res_id','=',False),
                                                 ('value','=','%s,%s'%(report.act_window_id and report.act_window_id.type or report.type, report.act_window_id and report.act_window_id.id or report.id))] , context=context)
            if values_ids:
                values_obj.unlink(cr, uid, values_ids, context=context)
                if report.act_window_id:
                    act_ctx = eval(report.act_window_id.context)
                    if act_ctx.has_key('cubicReport'):
                        del act_ctx['cubicReport']
                    act_obj.write(cr, uid, [report.act_window_id.id], {'context': str(act_ctx)}, context=context)
        return super(report_xml, self).unlink(cr, uid, ids, context=context)