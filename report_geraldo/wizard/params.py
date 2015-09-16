# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
# Copyright (c) 2011 Cubic ERP - Teradata SAC. (http://cubicerp.com).
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import osv
from openerp.osv import fields as osv_fields
from openerp.osv.orm import setup_modifiers
from lxml import etree
import time

class base_report_params(osv.TransientModel):
    _name ="base.report.params"
    _inherit ="base.report.params"
    
    def fields_get(self, cr, uid, fields=None, context=None):
        if context.get('cubicReport'):
            report = self.pool.get('ir.actions.report.xml').browse(cr, uid, context['cubicReport'].get('id'), context=context)
            params = eval(report.custom_params_src)
            for p in params:
                self._columns[p['name']] = eval('fields.%(type)s(*args,**kwargs)'%p,{'fields':osv_fields,'args':p.get('args',[]),'kwargs':p.get('kwargs',{})})
        res = super(base_report_params, self).fields_get(cr, uid, fields, context)
        return res
    
    def default_get(self, cr, uid, fields_list, context=None):
        if context.get('cubicReport') and not context['cubicReport'].get('create',False):
            report = self.pool.get('ir.actions.report.xml').browse(cr, uid, context['cubicReport'].get('id'), context=context)
            params = eval(report.custom_params_src)
            for p in params:
                if p.has_key('default'):
                    context["default_%s"%p['name']] = p['default']
        res = super(base_report_params, self).default_get(cr, uid, fields_list, context=context)
        return res
    
    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(base_report_params, self).fields_view_get(cr, user, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        if res.get('type') != 'form':
            return res
        if context.get('cubicReport'):
            report = self.pool.get('ir.actions.report.xml').browse(cr, user, context['cubicReport'].get('id'), context=context)
            params = eval(report.custom_params_src)
            doc = etree.XML(res['arch'])
            group = doc.xpath("//group")[0]
            for p in params:
                node = etree.Element('field', {'name':p['name'], 'required':p.get('required','0'),
                                               'invisible':p.get('invisible','0'), 'attrs':p.get('attrs','{}')})
                group.append(node)
                res['fields'][p['name']] = {'selectable': True, 'views': {}, 'type': p.get('type','char'), 
                                            'string': p.get('string',p['name'])}
                if p.get('type') == 'selection':
                    res['fields'][p['name']]['selection'] = p.get('args')[0]
                elif p.get('type') == 'many2one':
                    res['fields'][p['name']]['relation'] = p.get('args')[0]
                elif p.get('type') == 'one2many':
                    res['fields'][p['name']]['relation'] = p.get('args')[0]
                    res['fields'][p['name']]['relation_field'] = p.get('args')[1]
                    
                if p.has_key('help'):
                    res['fields'][p['name']]['help'] = p.get('help')
                setup_modifiers(node, res['fields'][p['name']])
            res['arch'] = etree.tostring(doc)
        return res
    