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

import StringIO
import time
import os
import importlib
import glob

from cubic_report import CubicReport

from geraldo.generators import PDFGenerator, TextGenerator, CSVGenerator
from openerp.report.report_sxw import report_sxw, rml_parse, pooler
from openerp.tools.translate import _

class cubic_parser(report_sxw):
    
    def __init__(self, name, table, rml=False, parser=rml_parse, header='external', store=False):
        super(cubic_parser,self).__init__(name, table, rml=rml, parser=parser, header=header, store=store)
    
    def _get_report_class(self, cr, uid, report, context=None):
        _module = importlib.import_module('.%s'%(report.custom_class and report.report_module or 'report_geraldo.cubic_report'),
                                          'openerp.addons')
        return eval('_module.%s'%(report.custom_class and report.report_class or 'CubicReport'),
                    {'_module':_module})
    
    def get_objects(self, cr, uid, ids, report, data={}, context=None):
        pool = pooler.get_pool(cr.dbname)
        objects = []
        if report.custom_sql:
            cr.execute(report.custom_sql_src%data.get('form',{}))
            records = cr.fetchall()
            for record in records:
                columns = {}
                i = 0
                for desc in cr._obj.description:
                    columns[desc[0]] = record[i]
                    i += 1
                objects.append(columns)
        else:
            if report.custom_domain:
                domain = eval(report.custom_domain_src%data.get('form',{}))
                if report.custom_order:
                    ids = pool.get(report.model).search(cr, uid, domain, order=report.custom_order_src, context=context)
                else: 
                    ids = pool.get(report.model).search(cr, uid, domain, context=context)
            elif report.custom_order:
                ids = pool.get(report.model).search(cr, uid, [('id','in',ids)], order=report.custom_order_src, context=context)
            objects = pool.get(report.model).browse(cr, uid, ids, context=context)
        return objects
    
    def create(self, cr, uid, ids, data, context=None):
        if context is None: context={}
        pool = pooler.get_pool(cr.dbname)
        report_obj = pool.get('ir.actions.report.xml')
        if context.has_key('cubicReport'):
            report = report_obj.browse(cr, uid, context.get('cubicReport').get('id'), context=context)
            context['active_id'] = data['form']['cubicReport']['context'].get('active_id')
            context['active_ids'] = data['form']['cubicReport']['context'].get('active_ids',[])
        else:
            report = report_obj.browse(cr, uid, report_obj.search(cr, uid, [('report_name', '=', self.name[7:])],
                                                                  context=context)[0], context=context)
        objects = self.get_objects(cr, uid, ids, report, data, context=context)
        
        tmp_file_name = '%s-%s'%(report.report_name,time.time())
        context['tmp_file_name'] = tmp_file_name
        for k in data.get('form',{}):
            context['params_'+k] = data['form'][k]
        tmp_file = report.generator_type == 'prn' and '%s.%s'%(tmp_file_name,report.generator_type) or StringIO.StringIO()
        _report_class = self._get_report_class(cr, uid, report, context=context)(cr, uid, pool,
                                                                            queryset=objects,
                                                                            report=report, context=context)
        if report.generator_type == 'pdf':
            _report_class.generate_by(PDFGenerator,filename=tmp_file, variables=data.get('form',{}))
        elif report.generator_type == 'prn':
            _report_class.generate_by(TextGenerator,filename=tmp_file, variables=data.get('form',{}))
        elif report.generator_type == 'csv':
            _report_class.generate_by(CSVGenerator,filename=tmp_file, variables=data.get('form',{}))
            
        res = (report.generator_type == 'prn' and open(tmp_file,'r').read() or tmp_file.getvalue(),report.extension_file or report.generator_type)
        for tmp_file in glob.glob('%s.*'%tmp_file_name):
            os.remove(tmp_file)
        return res