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

import os
from openerp.osv import fields, osv
from openerp import netsvc
from cubic_parser import cubic_parser

class report_xml(osv.osv):
    
    def __init__(self, pool, cr):
        super(report_xml, self).__init__(pool, cr)
        
    def _get_default_title(self, cr, uid, context=None): 
        return"""# %(model)s: Model description
# %(field)s: Field Name
{
'tree': [
        {'type':'system', 'expression':'%(report_title)s', 'top':0.4*cm, 'left':0*cm, 'width':BAND_WIDTH, 'style':'Title1'},
    ],
'form': [
        {'type':'value', 'name':'name', 'value_prefix':"%(model)s - %(field)s: ", 'top':0.5*cm, 'left':0*cm, 'width':BAND_WIDTH, 'style':'Title1'},
    ],
}"""
    
    def _get_default_style(self, cr, uid, context=None):
        return """{
'title1'   : {'fontName': 'Helvetica-Bold', 'fontSize': 16, 'alignment': TA_CENTER},
'title2'   : {'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_LEFT},
'title3'   : {'fontName': 'Helvetica-Bold', 'fontSize': 12, 'alignment': TA_LEFT},
'normal'   : {'fontName': 'Helvetica', 'fontSize': 11, 'alignment': TA_JUSTIFY},
'label'    : {'fontName': 'Helvetica-Bold', 'fontSize': 10, 'alignment': TA_LEFT},
'value'    : {'fontName': 'Helvetica', 'fontSize': 10, 'alignment': TA_LEFT},
'company'  : {'fontName': 'Helvetica', 'fontSize': 12, 'alignment': TA_LEFT},
'table'    : {'fontSize': 9, 'leftIndent': 0.1*cm, 'rightIndent': 0.1*cm},
'table.header':{'fontName': 'Helvetica-Bold', 'alignment': TA_CENTER},
'table.data':{'fontName': 'Helvetica', 'alignment': TA_LEFT, 'leftIndent': 0.15*cm, 'rightIndent': 0.1*cm},
'table.data.int':{'alignment': TA_CENTER},
'table.data.float':{'alignment': TA_RIGHT},
'table.data.date':{'alignment': TA_CENTER},
'table.data.text':{'alignment': TA_JUSTIFY},
'table.data.selection':{'alignment': TA_CENTER},
'group_by': {'fontName': 'Helvetica-Bold', 'fontSize': 12, 'alignment': TA_LEFT},
'group_by.level_1': {'fontName': 'Helvetica-Bold', 'fontSize': 13, 'leftIndent': 0.4*cm},
'group_by.level_2': {'fontName': 'Helvetica-Bold', 'fontSize': 12, 'leftIndent': 0.8*cm},
'group_by.level_3': {'fontName': 'Helvetica-Bold', 'fontSize': 11, 'leftIndent': 1.2*cm},
'group_by.level_4': {'fontName': 'Helvetica-Bold', 'fontSize': 10, 'leftIndent': 1.6*cm},
}"""
    
    def _get_default_attributes(self, cr, uid, context=None):
        return """{'page_header':{},
'title':{},
'begin':{},
'detail':{'borders':{'bottom':True}},
'summary':{},
'page_footer':{},
}"""

    def _get_default_report_properties(self, cr, uid, context=None):
        return """{'first_page_number': 1,
'margin_top': 1*cm,
'margin_bottom': 1*cm,
'margin_left': 1*cm,
'margin_right': 1*cm,
'page_footer': 1*cm,
'print_if_empty': True
}"""

    def _get_default_sql_fields(self, cr, uid, sql, context=None):
        cr.execute(sql)
        res = []
        for desc in cr._obj.description:
            res.append({'name':desc[0],'type':'field'})
        return """{
'detail'  :  [
            %s
            ],
'summary' :  [
           ]
}"""%str(res)[1:-1]
        
    def _get_default_fields(self, cr, uid, context=None):
        if context is None: context={}
        detail_summary = ""
        model = context.get('report_model',None)
        sql = context.get('report_sql',None)
        if sql:
            res = self._get_default_sql_fields(cr, uid, sql, context=context)
            detail_summary = res[2: -2]+','
        elif model is not None: 
            res = self.pool.get('ir.model')._get_cubic_report(cr, uid, model, context=context)
            detail_summary = res[2:-2]+','
        report_company_detail = """{'type':'label', 'text':s.browse('res.users',uid).company_id.name, 'top':0.3*cm, 'left':0*cm, 'width':BAND_WIDTH, 'style':{'alignment':TA_CENTER}},
            """
        if context.get('report_company_detail',False):
            report_company_detail = ""
        res= """{
'page_header': [
            {'type':'image', 'file':s.browse('res.users',uid).company_id.logo, 
                    'left':0*cm, 'top':0*cm, 'right':4*cm, 'bottom':0.5*cm,
                    'style':{'alignment':TA_LEFT}
                },
            """+report_company_detail+"""{'type':'label', 'text':s.browse('res.users',uid).company_id.rml_header1, 'top':0.3*cm, 'left':0*cm, 'width':BAND_WIDTH, 'style':{'alignment':TA_RIGHT}},
            ],
'begin'  :  [
            ],
"""+detail_summary+"""
'page_footer': [
            {'type':'label', 'text':s.pool('res.users').browse(cr,uid,uid).company_id.rml_footer, 'top':0.1*cm, 'left':0*cm, 'width':BAND_WIDTH, 'style':{'alignment':TA_CENTER}},
            {'type':'system', 'expression':'%(now:%d/%m/%Y)s %(now:%H:%M)s', 'top':0.1*cm, 'left':0*cm, 'width':BAND_WIDTH, 'style':{'alignment':TA_LEFT}},
            {'type':'system', 'expression':'Pag. %(page_number)s/%(page_count)s', 'top':0.1*cm, 'left':0*cm, 'width':BAND_WIDTH, 'style':{'alignment':TA_RIGHT}},
           ],
}"""
        return res

    def _get_fields(self, cr, uid, report_id, context=None):
        if context is None: context={}
        report = self.browse(cr, uid, report_id, context=context)
        if report.custom_fields:
            res = report.custom_fields_src
        else:
            context['report_company_detail'] = report.report_company_detail
            context['report_model'] = report.model
            context['report_sql'] = report.custom_sql and report.custom_sql_src or None
            res = self._get_default_fields(cr, uid, context=context)
        return res

    _name = 'ir.actions.report.xml'
    _inherit = 'ir.actions.report.xml'
    _columns = {
            'generator_type': fields.selection([('pdf','PDF Generator .pdf'),
                                                ('prn','Text Generator .prn'),
                                                ('csv','CSV Generator .csv')],'Generator Output Type'),
            'extension_file': fields.char('Custom Extension File',8),
            'report_company_detail': fields.boolean('Report Company Details'),
            'custom_report': fields.boolean('Basic Report Customize'),
            'report_title': fields.char('Report Main Title',1024),
            'report_page_size': fields.selection([('A6','A6'),('A5','A5'),('A4','A4'),('A3','A3'),('A2','A2'),('A1','A1'),('A0','A0'),
                                                  ('B6','B6'),('B5','B5'),('B4','B4'),('B3','B3'),('B2','B2'),('B1','B1'),('B0','B0'),
                                                  ('LETTER','Letter'),('LEGAL','Legal'),('ELEVENSEVENTEEN','Elevenseventeen'),('custom','Custom')],
                                                 'Report Page Size'),
            'report_page_size_custom': fields.char('Custom Page Size',32),
            'report_page_orientation': fields.selection([('portrait','Porttrait'),
                                                         ('landscape','Landscape')],'Report Page Orientation'),
            'report_mode': fields.selection([('auto','Automatic'),
                                             ('tree','List'),
                                             ('form','Form')],'Report Mode'),
            'report_layout': fields.selection([('4','Basic (four columns)'),
                                               ('2','Two Columns'),
                                               ('6','Six Columns'),
                                               ('8','Eight Columns'),],'Default Form Layout'),
            'custom_params_src': fields.text('Customized Report Params'),
            'custom_sql': fields.boolean('Based on Customize SQL'),
            'custom_sql_src': fields.text('Customized SQL'),
            'custom_domain': fields.boolean('Use Customized Domain in The Report'),
            'custom_domain_src': fields.text('Customized domain'),
            'custom_order': fields.boolean('Use Customized Order in The Report'),
            'custom_order_src': fields.text('Customized Order By'),
            'custom_fields': fields.boolean('Use Customized Fields in The Report'),
            'custom_fields_src': fields.text('Customized Fields'),
            'custom_style': fields.boolean('Use Customized Style in The Report'),
            'custom_style_src': fields.text('Customized Style'),
            'custom_class': fields.boolean('Use a Customized Class'),
            'report_module': fields.char('Report Module',254,help='Name of the module and ".py" file that contains the report class, separated by dots and don\'t put ".py" extension file. Example: sale_report.report (directory.file without the extension)'),
            'report_class': fields.char('Report Class',128,help="Name of the new customized class inheritance of CubicReport. Example: SaleOrderReport"),
            'custom_attributes': fields.boolean('Use Advanced Customized Attributes in The Report'),
            'custom_title_src': fields.text('Advanced Customized Main Title'),
            'custom_attributes_src': fields.text('Customized Attributes on Main Bands'),
            'custom_report_properties_src': fields.text('Customized Report Properties'),
        }
    _defaults = {
            'generator_type': 'pdf',
            'report_page_size': 'A4',
            'report_page_size_custom': '(21*cm,29*cm)',
            'report_page_orientation': 'portrait',
            'report_mode': 'auto',
            'report_layout': '4',
            'report_company_detail': False,
            'custom_class': False,
            'report_module': 'report_geraldo.cubic_report',
            'report_class': 'CubicReport',
            'custom_title_src': _get_default_title,
            'custom_domain_src': '[]',
            'custom_order_src': '',
            'custom_params_src': '[]',
            'custom_fields_src': '',
            'custom_style_src': _get_default_style,
            'custom_attributes_src': _get_default_attributes,
            'custom_report_properties_src': _get_default_report_properties,
        }
    
    def register_all(self,cr):
        super(report_xml, self).register_all(cr)
        cr.execute("SELECT * FROM ir_act_report_xml WHERE report_type = 'cubicReport'")
        records = cr.dictfetchall()
        for r in records:
            self.register_report(cr, r['report_name'], r['model'],r['report_rml'], r['header'])
            
    def register_report(self, cr, report_name, model, report_rml, header):
        opj = os.path.join
        svcs = netsvc.Service._services
        name = 'report.%s' % report_name
        service = svcs.get(name,False)
        if service:
            if isinstance(service, cubic_parser):
                return
            if hasattr(service, 'parser'):
                parser = service.parser
            del svcs[name]
        cubic_parser(name, model,rml=opj('addons',report_rml or '/'), header=header)

    def create(self, cr, uid, vals, context=None):
        if vals.get('report_type','') == 'cubicReport':
            self.register_report(cr,vals['report_name'],vals['model'], vals.get('report_rml', False), vals.get('header', False))
            if not vals.get('custom_fields_src',False):
                context['report_model'] = vals.get('model',False)
                vals['custom_fields_src'] = self._get_default_fields(cr, uid, context=context)
        return super(report_xml, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context={}
        ids = isinstance(ids, (int, long)) and [ids,] or ids
        for action in self.browse(cr, uid, ids, context=context):
            if action.report_type != 'cubicReport':
                continue
            self.register_report(cr, vals.get('report_name',action.report_name), vals.get('model',action.model),
                                 vals.get('report_rml',action.report_rml), vals.get('header',action.header))
        
        if ids and vals.get('custom_fields',False):
            report = self.browse(cr, uid, ids[0], context=context)
            if not (report.custom_fields_src or vals.get('custom_fields_src',False)):
                context['report_model'] = vals.get('model',False) or report.model
                vals['custom_fields_src'] = self._get_default_fields(cr, uid, context=context)
        return super(report_xml, self).write(cr, uid, ids, vals, context)