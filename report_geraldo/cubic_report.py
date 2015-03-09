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

import base64
import time
import openerp.addons as ad
import os

from reportlab.lib.pagesizes import *
from reportlab.lib.enums import *
from reportlab.lib.colors import *

from geraldo.utils import cm
from geraldo import *
from geraldo.widgets import Widget
from geraldo.graphics import Graphic

from openerp import osv

class CubicGraphic(Graphic):
    pass

class CubicImage(Image, CubicGraphic):
    def __init__(self, *args, **kwargs):
        super(CubicImage, self).__init__(*args, **kwargs)
        
class CubicRect(Rect, CubicGraphic):
    def __init__(self, *args, **kwargs):
        super(CubicRect, self).__init__(*args, **kwargs)    

class CubicWidget(Widget):    
    colWidth = None
    colSpan = None
    height = 0.65*cm
    
    def clone(self):
        new = super(CubicWidget, self).clone()
        new.colWidth = self.colWidth
        new.colSpan = self.colSpan
        return new

class CubicLabel(Label, CubicWidget):
    def __init__(self, *args, **kwargs):
        super(CubicLabel, self).__init__(*args, **kwargs)
    
class CubicSystemField(SystemField, CubicWidget):
    def __init__(self, *args, **kwargs):
        super(CubicSystemField, self).__init__(*args, **kwargs)
    
class CubicObjectValue(ObjectValue, CubicWidget):
    customCode = None
    customCodeMethod = None
    attribute_src = None
    
    def clone(self):
        new = super(CubicObjectValue, self).clone()
        new.customCode = self.customCode
        new.customCodeMethod = self.customCodeMethod
        new.attribute_src = self.attribute_src
        return new
    
    def get_object_value(self, instance=None, attribute_name=None):
        if self.customCode:
            instance = instance or self.instance
            name = attribute_name or self.attribute_name
            src = self.attribute_src
            vals = {'cr' : self.band.cb._cr,
                    'uid': self.band.cb._uid,
                    'context': self.band.cb._context,
                    'pool' : self.band.cb._pool,
                    'cb' : self.band.cb,
                    'obj': instance,
                    'result': ''}
            vals.update(self.band.cb._codes)
            if self.customCodeMethod=='eval':
                value = eval(src,vals)
            else:
                exec src in vals
                value = vals['result']
            self.band.cb._codes[name] = value
            return value
        else:
            value = super(CubicObjectValue, self).get_object_value(instance=instance, attribute_name=attribute_name)
        if value is None:
            return ''
        ctx = {}
        ctx['table_name'] = self.band.table_name or 'main'
        (model_field_value, n, b, model) = self.band.get_model_field_value(self.attribute_name,context=ctx)
        if isinstance(value,bool) and model_field_value['type'] != 'boolean':
            value = ''
        if model_field_value['type'] == 'selection':
            ctx['translate_types'] = ('selection',)
            ctx['translate_model'] = '%s,%s'%(model._name,value)
            for t in model_field_value['selection']:
                if t[0] == value:
                    value = t[1]
            value = self.band.translate(value, context=ctx)
        elif model_field_value['type'] in ('one2many','many2many'):
            vals = [v.name for v in value]
            value = '; '.join(vals)
        elif model_field_value.get('translate',False):
            ctx['translate_types'] = ('model',)
            ctx['translate_model'] = '%s,%s'%(model._name,value)
            value = self.band.translate(value, context=ctx)
        return value

class CubicReportBand(ReportBand):
    
    cols = 4 #fixed columns
    _top_increment = 0.7*cm #increments on top for form
    _top_initial = 0.3*cm # from this value begin the top format on fields
    _left_initial = 0.0*cm #left initial
    _left_proportion_value = 2.0/3
    _left_proportion_label = 1.0/3
    table_name = None
    visible_force = None
    # Modifiy geraldo/generators/base.py line 385 by self.update_top_pos(band_height,set_position=getattr(band,'top_position',None))
    top_position = None #absolute lop position
    
    def __init__(self, cr, uid, cb, vals, context=None):
        global _
        _ = self.translate
        super(CubicReportBand, self).__init__()
        self.load(cr, uid, cb, vals, context=context)
        self.set_visible()
        
    def load(self, cr, uid, cb, vals={}, context=None):
        self.cb = cb
        self.cols = int(cb._report.report_layout)
        self.mode = cb.mode
        for k,v in vals.get('band',{}).items():
            setattr(self, k, v)
        return True

    def set_visible(self):
        self.visible = self.is_visible()

    def is_visible(self):
        if self.visible_force is not None:
            return self.visible_force 
        v = False
        if self.elements:
            v = True
        elif self.child_bands:
            for child in self.child_bands:
                if child.visible:
                    v = True
                    break
        return v
    
    def translate(self, source, vals=(), context=None):
        if context is None: context={}
        lang = self.cb._context.get('lang',False)
        if not lang:
            return source
        types = context.get('translate_types',False) or ('view','report','code')
        model = context.get('translate_model') or self.cb._report.model
        res = self.cb._pool.get('ir.translation')._get_source(self.cb._cr, self.cb._uid, model, types, lang, source)
        if vals:
            vals = isinstance(vals, tuple) and vals or (vals)
            res = res%vals
        return res

    def cr(self):
        return self.cb._cr
    
    def pool(self,*args):
        res = self.cb._pool
        if len(args) > 0:
            res = self.cb._pool.get(args[0])
        return res
    
    def browse(self, obj, ids, **kwargs):
        return self.cb._pool.get(obj).browse(self.cb._cr, self.cb._uid, ids, context=self.cb._context, **kwargs)
    
    def search(self, obj, arg):
        return self.cb._pool.get(obj).browse(self.cb._cr, self.cb._uid, arg, context=self.cb._context, **kwargs)
    
    def read(self, obj, ids, fields):
        return self.cb._pool.get(obj).read(self.cb._cr, self.cb._uid, ids, fields, context=self.cb._context, **kwargs)
    
    def read_group(self, obj, arg, fields, group):
        return self.cb._pool.get(obj).read(self.cb._cr, self.cb._uid, arg, fields, group, context=self.cb._context, **kwargs)
    
    def write(self, obj, ids, arg):
         return self.cb._pool.get(obj).read(self.cb._cr, self.cb._uid, ids, arg, context=self.cb._context, **kwargs)
        
    def label(self, string, **kwargs):
        context = kwargs.get('context',{})
        if context.get('table_name','main') not in self.cb._default_table_names: 
            if not kwargs.has_key('style'):
                kwargs['style'] = self.get_style('table.header', context=context)
        return [CubicLabel(text=string and _(string,context=context) or ' ', **kwargs)]
    
    def system(self, expression, **kwargs):
        return [CubicSystemField(expression=expression, **kwargs)]
    
    def image(self, **kwargs):
        if kwargs.has_key('file'):
            kwargs.pop('filename','')
            image = kwargs.pop('file')
            tmp_file_name = "/tmp/%s.%s.image"%(self.cb._context.get('tmp_file_name'),time.time())
            buff = base64.decodestring(image)
            tmp_file = file(tmp_file_name,'wb')
            tmp_file.write(buff)
            tmp_file.close()
            return [CubicImage(filename=tmp_file_name, **kwargs)]
        return [CubicImage(**kwargs)]
    
    def get_model_field_value(self, name, context=None):
        if context is None: context={}
        names = name.split('.')
        name_back = '.'.join(names[:-1])
        table_name = context.get('table_name','main')
        qs = self.cb._table[table_name].get('queryset',self.cb.queryset)
        table_model = self.cb._table[table_name].get('model',self.cb._model) # review
        table_model_field = table_model.fields_get(self.cb._cr,self.cb._uid).get(names[0],{}) # review
        if not qs:
            return table_model_field, name, None, table_model
        if self.cb._report.custom_sql:
            return {'string':name, 'type':'char'},name, None, None
        brw = eval('qs[0].%s'%name,{'qs':qs})
        for qs_local in qs:
            brw_tmp = eval('qs.%s'%name,{'qs':qs_local})
            if brw_tmp:
                brw = brw_tmp
                break
        if isinstance(brw,osv.orm.types.NoneType):
            return table_model_field, name, None, table_model
        elif isinstance(brw,(osv.orm.browse_record,)): #osv.orm.browse_record_list
            model = brw._model
            name = "%s.name"%name
            names = name.split('.')
            brw = eval('qs[0].%s'%name,{'qs':qs})
            for _qs in qs:
                _brw = eval('qs.%s'%name,{'qs':_qs})
                if _brw:
                    brw = _brw
                    break 
        else:
            model_brw = eval('qs[0]%s%s'%(name_back and '.' or '', name_back),{'qs':qs})
            for _qs in qs:
                _brw = eval('qs%s%s'%(name_back and '.' or '', name_back),{'qs':_qs})
                if _brw:
                    model_brw = _brw
                    break
            model = model_brw._model
        model_field = model.fields_get(self.cb._cr,self.cb._uid)[names[-1]]
        return model_field, name, brw, model
    
    def dummy(self,**kwargs):
        return [CubicLabel(text=' ', **kwargs)]
    
    def rect(self,**kwargs):
        return [CubicRect(**kwargs)]
    
    def code(self,name,src,**kwargs):
        if not kwargs.has_key('customCode'):
            kwargs['customCode'] = True
        return [CubicObjectValue(attribute_name=name, attribute_src=src, **kwargs)]
    
    def value(self, name, **kwargs):
        res = []
        context = kwargs.get('context',{})
        model_field, name, brw, model = self.get_model_field_value(name,context=context)
        if not model_field:
            return self.dummy()
        prefix = kwargs.pop('value_prefix','')
        suffix = kwargs.pop('value_suffix','')
        if prefix or suffix:
            prefix = prefix%{'model': _(model._description), 'field': _(model_field['string']), 'report_title':self.cb.title}
            suffix = suffix%{'model': _(model._description), 'field': _(model_field['string']), 'report_title':self.cb.title}
            display_format = kwargs.get('display_format','')
            if display_format:
                display_format = prefix + display_format + suffix
            else:
                display_format = prefix + '%s' + suffix
            kwargs['display_format'] = display_format
        table_name = context.get('table_name',False)
        if not kwargs.has_key('style') and self.cb._table[table_name or 'main'].has_key('style'):
            kwargs['style'] = self.get_style(self.cb._table[table_name].get('style'), context=context)
        if context.get('table_name','main') not in self.cb._default_table_names:
            if not kwargs.has_key('style') and not self.default_style:
                if isinstance(brw,int):
                    kwargs['style'] = self.get_style('table.data.int', context=context)
                elif isinstance(brw,float):
                    kwargs['style'] = self.get_style('table.data.float', context=context)
                elif model_field['type'] in ('date','datetime',):
                    kwargs['style'] = self.get_style('table.data.date', context=context)
                elif model_field['type'] in ('text',):
                    kwargs['style'] = self.get_style('table.data.text', context=context)
                elif model_field['type'] in ('selection',):
                    kwargs['style'] = self.get_style('table.data.selection', context=context)
                else:
                    kwargs['style'] = self.get_style('table.data', context=context)
        return [CubicObjectValue(attribute_name=name,**kwargs)]
    
    def field(self, name, table='main', **kwargs):
        context = kwargs.get('context',{})
        res = []
        names = name.split('.')
        tree_band_begin = self.cb._table[table].get('tree_band_begin',self.cb.band_begin)
        model_field, name, brw, model = self.get_model_field_value(name,context=context)
        string = kwargs.pop('string',model_field.get('string',name))
        fields_insert = kwargs.pop('insert',False)
        kwargs_label = kwargs.copy()
        context['translate_types'] = ('field',)
        if model:
            context['translate_model'] = '%s,%s'%(model._name,name)
        kwargs_value = kwargs.copy()
        for arg in kwargs:
            if arg[:6] == 'label.':
                kwargs_label[arg[6:]] = kwargs[arg]
                del kwargs_label[arg]
                del kwargs_value[arg]
            elif arg[:6] == 'value.':
                kwargs_value[arg[6:]] = kwargs[arg]
                del kwargs_label[arg]
                del kwargs_value[arg]
        if not kwargs_label.has_key('style') and not self.default_style:
            if table in self.cb._default_table_names:
                kwargs_label['style'] = self.get_style('label', context=context)
        if not kwargs_value.has_key('style') and not self.default_style:
            if table in self.cb._default_table_names:
                kwargs_value['style'] = self.get_style('value', context=context)
        if not kwargs.pop('nolabel',False):
            if self.mode=='tree':
                tree_band_begin.elements += self.label(string, **kwargs_label)
            else:
                res += self.label(string, **kwargs_label)
        if fields_insert:
            res += self.get_widgets(fields_insert, context=context)
        if self.cb._table[table].get('queryset',[]):
            res += self.value(name, **kwargs_value)
        return res
    
    def format_widgets(self, cr, uid, context=None):
        widgets = []
        colWidths = []
        for element in self.elements:
            if not isinstance(element,(CubicImage,CubicRect,CubicGraphic)):
                if element.top==0 and element.left==0:
                    widgets.append(element)
                    colWidths.append(element.colWidth or 0.0)
                elif element.colWidth:
                    element._width = element.colWidth
        if self.width is None:
            _band_width = self.cb.page_size[0] - self.cb.margin_left -self.cb.margin_right
        else:
            _band_width = self.width
        cols = self.cols
        if self.mode == 'tree':
            cols = len(widgets)
            col_width_diff= _band_width - sum(colWidths)
            cols_with_0 = len(filter(lambda n:n==0.0,colWidths))
            col_diff = cols_with_0 and (col_width_diff / cols_with_0) or 0.0
            left_increments = []
            for colWidth in colWidths:
                if not colWidth:
                    left_increments.append(col_diff)
                else:
                    left_increments.append(colWidth)
        else:
            left_increments = [cols and (_band_width / cols) or 0.0 for l in range(cols)]
        top_increment = self._top_increment
        left = self._left_initial
        top = self._top_initial
        left_proportion_value = (self.mode=='tree' or cols%2) and 1.0 or self._left_proportion_value*2
        left_proportion_label = (self.mode=='tree' or cols%2) and 1.0 or self._left_proportion_label*2
        pair = False
        i = 0
        col_increment = left_increments and (left_increments[i] * left_proportion_label) or 0.0
        col_width_diff = 0.0
        for widget in widgets:
            if widget.colSpan:
                span = i + widget.colSpan
                if span > cols:
                    # New Phanton Row
                    left = self._left_initial
                    top += widget.height or top_increment
                    pair = True
                    i=0
                    span = widget.colSpan
                    span_increment=0.0
                else:
                    span_increment = col_increment
                    i+=1
                while(i < span):
                    # New Phanton Column
                    if pair:
                        pair = False
                        span_increment += left_increments[i]*left_proportion_label
                    else:
                        pair = True
                        span_increment += left_increments[i]*left_proportion_value
                    i+=1
                col_increment = span_increment
                i-=1
            if widget.colWidth and self.mode != 'tree':
                col_width_diff = col_increment - widget.colWidth + col_width_diff
                col_increment = widget.colWidth
            elif col_width_diff and self.mode != 'tree':
                col_increment += col_width_diff
                col_width_diff = 0.0
            widget.top = top
            widget.left = left
            widget.width = col_increment
            left += col_increment
            i += 1
            if left >= _band_width or i >= cols :
                # New row
                left = self._left_initial
                top += widget.height or top_increment
                pair = True
                i=0
                col_width_diff = 0.0
            # New Column
            if pair:
                pair = False
                col_increment = left_increments[i]*left_proportion_label
            else:
                pair = True
                col_increment = left_increments[i]*left_proportion_value
        return True
    
    def get_company_detail(self, context=None):
        res = []
        if self.cb._report.report_company_detail:
            cubic_report = self.cb._pool.get('res.company')._get_cubic_report(self.cb._cr, self.cb._uid, self.cb._report.id, context=context)
            fields = eval(cubic_report, {'company':self.cb._company,'cm':cm})
            for field in fields:
                if not field.has_key('style'):
                    field['style'] = 'company'
            res += self.get_widgets(fields, context=context)
        return res
    
    def get_main_title(self, context=None):
        if context is None: context={}
        res = []
        top = 0.1
        if self.cb._report.custom_attributes:
            fields = eval(self.cb._report.custom_title_src)
            res = self.get_widgets(fields[self.cb.mode], context=context)
        elif self.cb._report.custom_report:
            if self.cb._report.report_title:
                res += self.get_widget({'type':'system', 'expression':self.cb._report.report_title, 'top':top*cm, 'left':0*cm, 'width':BAND_WIDTH, 'style':'Title1'})
        elif self.cb._report.custom_sql:
            res += self.get_widget({'type':'system', 'expression':self.cb._report.name, 'top':top*cm, 'left':0*cm, 'width':BAND_WIDTH, 'style':'Title1'})
        else:
            if self.cb.mode=='tree':
                res += self.get_widgets(eval(self.cb._pool.get('ir.actions.report.xml')._get_default_title(self.cb._cr, self.cb._uid, context=context))['tree'], context=context)
            else:
                res += self.get_widgets(eval(self.cb._pool.get('ir.actions.report.xml')._get_default_title(self.cb._cr, self.cb._uid, context=context))['form'], context=context)
        return res
            
    def get_style(s, name, context=None):
        if isinstance(name,dict): 
            return name
        if s.cb._report.custom_style:
            res = eval(s.cb._report.custom_style_src)
        else:
            res = eval(s.cb._pool.get('ir.actions.report.xml')._get_default_style(s.cb._cr, s.cb._uid, context=context))
        return res.get(name.lower(),{})
        
    def get_fields(s, cr, uid, name='all', context=None):
        """
        Obtiene los fields de todas las bandas por default del reporte
        Parmaetro:
        name: nombre de la banda para devolver los field
        """
        if isinstance(name,list): 
            return name
        vars = {'s':s,
               'cr':cr,
               'uid':uid,
               'context':context,
               }
        vars.update(globals())
        if s.cb._report.custom_fields:
            res = eval(s.cb._report.custom_fields_src, vars)
        else:
            src = s.cb._pool.get('ir.actions.report.xml')._get_fields(s.cb._cr, s.cb._uid, s.cb._report.id, context=context)
            res = eval(src, vars)
        return name=='all' and res or res.get(name.lower(),[{}])

    def get_widget(self, field, context=None):
        """
        Transforma un diccionario en un widget
        """
        if context is None: context = {}
        res = []
        if field.get('style',False):
            field['style'] = self.get_style(field.get('style'), context=context)
        type = field.pop('type','').lower()
        field.update({'context':context})
        if type == 'field':
            name = field.pop('name',False)
            if name:
                table = context.get('table_name','main')
                res += self.field(name,table=table,**field)
        elif type == 'value':
            name = field.pop('name',False)
            if name:
                res += self.value(name,**field)
        elif type == 'label':
            text =  field.pop('text','')
            if text:
                res += self.label(text,**field)
        elif type == 'system':
            exp = field.pop('expression',False)
            if exp:
                res += self.system(exp,**field)
        elif type == 'image':
            if field.has_key('filename') or (field.has_key('file') and field.get('file')):
                res += self.image(**field)
        elif type == 'dummy':
            res += self.dummy(**field)
        elif type == 'rect':
            res += self.rect(**field)
        elif type == 'code':
            name = field.pop('name',False)
            src = field.pop('src',False)
            _eval = field.pop('eval',False)
            if name and src:
                res += self.code(name, src, **field)
            elif name and _eval:
                field['customCodeMethod'] = 'eval'
                res += self.code(name, _eval, **field)
        return res
    
    def get_widgets(self, fields, context=None):
        """
        Obtiene una lista de widgets a partir de una lista de diccionarios de diferentes tipos
        """
        res = []
        for field in fields:
            res += self.get_widget(field, context=context)
        return res

    def get_elements(self, name, context=None):
        """
        Obtiene los elementos con widgets para una banda determinada
        """
        if context is None: context={}
        fields =  context.get('report_custom_fields',self.get_fields(self.cb._cr, self.cb._uid, context=context)).get(name,[])
        return self.get_widgets(fields, context=context)


class CubicDetailBand(DetailBand, CubicReportBand):
    
    def load(self, cr, uid, cb, vals={}, context=None):
        super(CubicDetailBand, self).load(cr, uid, cb, vals=vals, context=context)
        for k,v in vals.get('detailBand',{}).items():
            setattr(self, k, v)
        return True


class CubicSubReport(SubReport):
    
    mode = 'tree'
    
    def __init__(self, cr, uid, cb, vals, context=None, **kwargs):
        super(CubicSubReport, self).__init__(**kwargs)
        self.load(cr, uid, cb, vals, context)
    
    def load(self, cr, uid, cb, vals={}, context=None):
        self.cb = cb
        for k,v in vals.get('subreport',{}).items():
            setattr(self, k, v)
        return True


class CubicReportGroup(ReportGroup):
    
    mode = 'tree'
    
    def __init__(self, cr, uid, cb, vals, context=None, **kwargs):
        super(CubicReportGroup, self).__init__(**kwargs)
        self.load(cr, uid, cb, vals, context)
    
    def load(self, cr, uid, cb, vals={}, context=None):
        self.cb = cb
        for k,v in vals.get('reportgroup',{}).items():
            setattr(self, k, v)
        return True


class CubicReportBandPageHeader(CubicReportBand):
    height = 1.3*cm
    borders = {'bottom': Line(stroke_color=black, stroke_width=3)}
    
    def load(self, cr, uid, cb, vals={}, context=None):
        super(CubicReportBandPageHeader,self).load(cr, uid, cb, vals=vals, context=context)
        if not cb._report.header:
            self.borders = {}
            self.height = 0
        for k,v in vals.get('page_header',{}).items():
            setattr(self, k, v)
        if cb._report.header:
            self.elements += self.get_elements('page_header', context=context)
        return True


class CubicReportBandPageFooter(CubicReportBand):
    height = 0.5*cm
    borders = {'top': Line(stroke_color=grey, stroke_width=3)}
    
    def load(self, cr, uid, cb, vals={}, context=None):
        super(CubicReportBandPageFooter,self).load(cr, uid, cb, vals=vals, context=context)
        if not cb._report.header:
            self.borders = {}
            self.height = 0
        for k,v in vals.get('page_footer',{}).items():
            setattr(self, k, v)
        if cb._report.header:
            self.elements += self.get_elements('page_footer', context=context)
        return True


class CubicReportBandCompany(CubicReportBand):
    height=0.0*cm
    visible = False
    auto_expand_height = True
    _top_increment = 0.6*cm
    
    def load(self, cr, uid, cb, vals={}, context=None):
        super(CubicReportBandCompany,self).load(cr, uid, cb, vals=vals, context=context)
        if context is None: context = {}
        table_name = context.get('table_name','company')
        cb._table[table_name]['tree_band_detail'] = self
        self.cols = int(cb._company.custom_cubic_report_layout)
        self.mode = 'form'
        for k,v in vals.get('company',{}).items():
            setattr(self, k, v)
        self.elements += self.get_company_detail(context=context)
    
class CubicReportBandMainTitle(CubicReportBand):
    height=1.6*cm
    table_name = 'main'
    
    def load(self, cr, uid, cb, vals={}, context=None):
        super(CubicReportBandMainTitle,self).load(cr, uid, cb, vals=vals, context=context)
        for k,v in vals.get('mainTitle',{}).items():
            setattr(self, k, v)
        self.elements += self.get_main_title(context=context)

class CubicReportBandTitle(CubicReportBand):
    height=1.6*cm
    
    def load(self, cr, uid, cb, vals={}, context=None):
        super(CubicReportBandTitle,self).load(cr, uid, cb, vals=vals, context=context)
        for k,v in vals.get('title',{}).items():
            setattr(self, k, v)
        self.elements += self.get_elements('title', context=context)

class CubicReportBandBeginContent(CubicReportBand):
    height=0.5*cm
    auto_expand_height = True
    
    def load(self, cr, uid, cb, vals={}, context=None):
        super(CubicReportBandBeginContent,self).load(cr, uid, cb, vals=vals, context=context)
        if context is None: context = {}
        table_name = context.get('table_name','main')
        cb._table[table_name]['tree_band_begin'] = self
        for k,v in vals.get('begin',{}).items():
            setattr(self, k, v)
        self.elements += self.get_elements('begin', context=context)

class CubicReportBandBegin(CubicReportBand):
    
    height = 0.0*cm
    
    def load(self, cr, uid, cb, vals={}, context=None):
        super(CubicReportBandBegin,self).load(cr, uid, cb, vals=vals, context=context)
        table_name = context.get('table_name','main')
        cb._table[table_name]['tree_band_begin_parent'] = self
        for k,v in vals.get('begin.parent',{}).items():
            setattr(self, k, v)
        self.elements += self.get_elements('begin.parent', context=context)
        if cb._table[table_name].get('default_mode',cb.mode) == 'tree':
            if vals.get('begin.parent',{}).get('table_name','main') == 'main':
                self.child_bands += [CubicReportBandCompany(cr, uid, cb, vals, context=context)]    
            if vals.get('begin.parent',{}).get('table_name','main') == 'main':
                self.child_bands += [CubicReportBandMainTitle(cr, uid, cb, vals, context=context)]
            self.child_bands += [CubicReportBandTitle(cr, uid, cb, vals, context=context)]
        self.child_bands += [CubicReportBandBeginContent(cr, uid, cb, vals, context=context)]
        return True


class CubicReportBandDetailContent(CubicDetailBand):
    height = 0.0*cm
    _top_initial = 0.07*cm
    auto_expand_height = True
    display_inline = True
    
    def load(self, cr, uid, cb, vals={}, context=None):
        super(CubicReportBandDetailContent,self).load(cr, uid, cb, vals=vals, context=context)
        if context is None: context = {}
        table_name = context.get('table_name','main')
        cb._table[table_name]['tree_band_detail'] = self
        for k,v in vals.get('detail',{}).items():
            setattr(self, k, v)
        self.elements += self.get_elements('detail', context=context)

class CubicReportBandDetail(CubicDetailBand):
    
    auto_expand_height = True
    borders = {'bottom': False}
    display_inline = True
    
    def load(self, cr, uid, cb, vals={}, context=None):
        super(CubicReportBandDetail,self).load(cr, uid, cb, vals=vals, context=context)
        table_name = context.get('table_name','main')
        if cb._table[table_name].get('default_mode',cb.mode) == 'tree':
            if vals.get('detail.parent',{}).get('table_name','main') == 'main':
                self.force_new_page = False
        else:
            if vals.get('detail.parent',{}).get('table_name','main') == 'main':
                self.force_new_page = True
            self.borders = {}
        for k,v in vals.get('detail.parent',{}).items():
            setattr(self, k, v)
        if cb.mode != 'tree':
            if vals.get('begin.parent',{}).get('table_name','main') == 'main':
                self.child_bands += [CubicReportBandCompany(cr, uid, cb, vals, context=context)]   
            if vals.get('detail.parent',{}).get('table_name','main') == 'main':
                self.child_bands += [CubicReportBandMainTitle(cr, uid, cb, vals, context=context)]
            self.child_bands += [CubicReportBandTitle(cr, uid, cb, vals, context=context)]
        self.child_bands += [CubicReportBandDetailContent(cr, uid, cb, vals, context=context)]
        return True
        

class CubicReportBandSummaryContent(CubicReportBand):
    
    def load(self, cr, uid, cb, vals={}, context=None):
        super(CubicReportBandSummaryContent,self).load(cr, uid, cb, vals=vals, context=context)
        table_name = context.get('table_name','main')
        cb._table[table_name]['tree_band_summary'] = self
        for k,v in vals.get('summary',{}).items():
            setattr(self, k, v)
        self.elements += self.get_elements('summary', context=context)
            
class CubicReportBandSummary(CubicReportBand):
    
    def load(self, cr, uid, cb, vals={}, context=None):
        super(CubicReportBandSummary,self).load(cr, uid, cb, vals=vals, context=context)
        for k,v in vals.get('summary.parent',{}).items():
            setattr(self, k, v)
        self.child_bands += [CubicReportBandSummaryContent(cr, uid, cb, vals, context=context)]
        return True


class CubicReport(Report):
    
    _table = {'main': {},
              'company': {}}
    _default_table_names = ('main','company')
    _codes = {}
    
    def __init__(self, cr, uid, pool, queryset=None, report=None, context=None):
        super(CubicReport, self).__init__(queryset=queryset)
        if context is None: context = {}
        self._table['main']['main'] = self
        self._table['main']['queryset'] = queryset
        self._table['company']['queryset'] = queryset
        self._cr = cr
        self._uid = uid
        self._pool = pool
        self._report = report
        self._model = pool.get(report.model)
        self._context = context
        self._company = pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        self.mode = report.report_mode=='auto' and (len(context.get('active_ids',[]))>1 and 'tree' or 'form') or report.report_mode
        report_page_size = report.report_page_size!='custom' and report.report_page_size or report.report_page_size_custom
        self.page_size = eval('%s(%s)'%(report.report_page_orientation,report_page_size))
        self.layout = report.report_layout
        if report.custom_attributes:
            report_properties = eval(report.custom_report_properties_src)
            for k,v in report_properties.items():
                setattr(self, k, v)
        self.load(cr, uid, queryset, report, self.get_attributes(cr, uid, pool, report, context=context), context=context)
        self.post_load(cr, uid, queryset, report, context=context)
    
    def load(self, cr, uid, local_objects, report, vals={}, context=None):
        if context is None: context = {}
        self.band_page_header = CubicReportBandPageHeader(cr, uid, self, vals, context=context)
        self.band_begin = CubicReportBandBegin(cr, uid, self, vals, context=context)
        self.band_detail = CubicReportBandDetail(cr, uid, self, vals, context=context)
        self.band_summary = CubicReportBandSummary(cr, uid, self, vals, context=context)
        self.band_page_footer = CubicReportBandPageFooter(cr, uid, self, vals, context=context)
        self.title = report.custom_report and _(report.report_title) or _(self._model._description)
        for field in self.band_page_footer.get_fields(cr, uid, name='subreports', context=context):
            if not field:
                continue
            table_name = field['name']
            self._table[table_name] = {}
            qs_string = field['queryset_string']%{'object':'o'}
            local_queryset = []
            for local_obj in local_objects:
                 local_queryset = eval(qs_string,{'o':local_obj})
                 if local_queryset:
                     break
            self._table[table_name]['queryset'] = local_queryset
            if not self._table[table_name]['queryset'] and qs_string[0] == '[':
                continue
            elif not self._table[table_name]['queryset']:
                qs_strings = qs_string.split('.')
                qs_string_back = '.'.join(qs_strings[:-1])
                qs_obj = False
                for local_obj in local_objects:
                    qs_obj_temp = eval(qs_string_back,{'o':local_obj})
                    if qs_obj_temp:
                        qs_obj = qs_obj_temp
                        break 
                if qs_obj:
                    qs_type = qs_obj._model.fields_get(cr, uid)[qs_strings[-1]]
                else:
                    qs_type = self._model.fields_get(cr, uid)[qs_strings[-1]]
                qs_model = self._pool.get(qs_type['relation'])
            else:
                qs_model = self._table[table_name]['queryset'][0]._model
            self._table[table_name]['model'] = qs_model
            attributes = field['attributes']
            default_mode = 'tree'
            if attributes.has_key('default_mode'):
                default_mode = attributes.get('default_mode',False)
            self._table[table_name]['default_mode'] = default_mode
            if not attributes.has_key('begin.parent'):
                attributes['begin.parent'] = {}
            attributes['begin.parent']['table_name'] = table_name
            if not attributes.has_key('detail.parent'):
                attributes['detail.parent'] = {}
            attributes['detail.parent']['table_name'] = table_name
            if not attributes.has_key('summary.parent'):
                attributes['summary.parent'] = {}
            attributes['summary.parent']['table_name'] = table_name
            # Don't use title because subreports don't support child_bands
            if not attributes.has_key('title'):
                attributes['title'] = {}
            attributes['title']['table_name'] = table_name
            if not attributes.has_key('begin'):
                attributes['begin'] = {}
            attributes['begin']['table_name'] = table_name
            if not attributes.has_key('detail'):
                attributes['detail'] = {}
            attributes['detail']['table_name'] = table_name
            if not attributes.has_key('summary'):
                attributes['summary'] = {}
            attributes['summary']['table_name'] = table_name
            context['report_custom_fields'] = field
            ctx_header = context.copy()
            ctx_header['table_name'] = table_name
            if not attributes['begin'].has_key('mode'):
                attributes['begin']['mode'] = default_mode
            # Modifiy geraldo/generators/base.py line 402 by self.render_band(child_band,current_object=current_object)
            subreport_header = CubicReportBandBegin(cr, uid, self, attributes, context=ctx_header)
            ctx_detail = context.copy()
            ctx_detail['table_name'] = table_name
            if not attributes['detail'].has_key('mode'):
                attributes['detail']['mode'] = default_mode
            subreport_detail = CubicReportBandDetail(cr, uid, self, attributes, context=ctx_detail)
            ctx_footer = context.copy()
            ctx_footer['table_name'] = table_name
            if not attributes['summary'].has_key('mode'):
                attributes['summary']['mode'] = default_mode
            subreport_footer = CubicReportBandSummary(cr, uid, self, attributes, context=ctx_footer)
            subreport = CubicSubReport(cr, uid, self, attributes, context=context,
                                       queryset_string = field['queryset_string'],
                                       band_header = subreport_header,
                                       band_detail = subreport_detail,
                                       band_footer = subreport_footer)
            self.subreports += [subreport]
        i = 1
        for field in self.band_page_footer.get_fields(cr, uid, name='groups', context=context):
            if not field:
                continue
            table_name = 'group_by.'+field['group_by']
            self._table[table_name] = {}
            attributes = field['attributes']
            default_mode = 'tree'
            if attributes.has_key('default_mode'):
                default_mode = attributes.get('default_mode',False)
            context['report_custom_fields'] = field
            ctx_header = context.copy()
            ctx_header['table_name'] = table_name
            if not attributes['begin'].has_key('mode'):
                attributes['begin']['mode'] = default_mode
            self._table[table_name]['style'] = self.band_page_footer.get_style('group_by.level_%s'%i, context=ctx_header)
            group_header = CubicReportBandBeginContent(cr, uid, self, attributes, context=ctx_header)
            ctx_footer = context.copy()
            if not attributes['summary'].has_key('mode'):
                attributes['summary']['mode'] = default_mode
            group_footer = CubicReportBandSummaryContent(cr, uid, self, attributes, context=ctx_footer)
            group = CubicReportGroup(cr, uid, self, attributes, context=context,
                                     attribute_name = field['group_by'],
                                     band_header = group_header,
                                     band_footer = group_footer)
            self.groups += [group]
            i = i + ((i<4) and 1 or 0)
        
        for k,v in vals.get('report',{}).items():
            setattr(self, k, v)
        return True
    
    def post_load(self, cr, uid, local_objects, report, context=None):
        for table in self._table:
            begin = self._table[table].get('tree_band_begin', False)
            begin_parent = self._table[table].get('tree_band_begin_parent', False)
            detail = self._table[table].get('tree_band_detail', False)
            summary = self._table[table].get('tree_band_summary', False)
            if begin:
                begin.format_widgets(cr, uid, context=context)
                begin.set_visible()
                if begin_parent:
                    begin_parent.set_visible()
            if detail:
                detail.format_widgets(cr, uid, context=context)
                detail.set_visible()
            if summary:
                summary.format_widgets(cr, uid, context=context)
                summary.set_visible()
        return True
    
    def get_attributes(s, cr, uid, pool, report, context=None):
        if report.custom_attributes:
            res = eval(report.custom_attributes_src)
        else:
            res = eval(pool.get('ir.actions.report.xml')._get_default_attributes(cr, uid, context=context))
        return res or {}