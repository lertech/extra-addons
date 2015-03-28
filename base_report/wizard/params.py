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

class base_report_params(osv.TransientModel):
    _name ="base.report.params"
    _columns = {
            'vals': osv_fields.text('Vals'),
        }
    
    def create(self, cr, uid, vals, context=None):
        context['cubicReport']['create'] = True
        return super(base_report_params,self).create(cr, uid, {'vals': str(vals)}, context=context)
    
    def read(self, cr, uid, ids, fields=None, context=None):
        if context is None:
            context = {}
        vals = super(base_report_params,self).read(cr, uid, ids, ['vals'], context=context)
        res = []
        for val in vals:
            v = eval(val['vals'])
            v['id'] = val['id']
            res += [v]
        return res
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        report = self.pool.get('ir.actions.report.xml').browse(cr, uid, context.get('cubicReport').get('id'),context=context)
        data['cubicReport'] = {'context': context.copy()}
        datas = {
             'ids': context.get('active_ids',[]),
             'model': report.model,
             'form': data
                 }
        return {
            'type': report.type,
            'report_name': report.report_name,
            'datas': datas,
            }
    