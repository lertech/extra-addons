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

class res_company(osv.osv):
        
    def _get_default_cubic_report(self, cr, uid, context=None):
        return """# company : Company browse object
# cm: Centimeters
[
{'type':'label', 'text':company.name, 'height':0.5*cm},
{'type':'label', 'text':company.street, 'height':0.5*cm},
{'type':'label', 'text':company.street2, 'height':0.5*cm},
{'type':'label', 'text':'%s, %s'%(company.city, company.state_id.name), 'height':0.5*cm},
{'type':'label', 'text':company.country_id.name, 'height':0.5*cm},
]"""

    def _get_cubic_report(self, cr, uid, report_id, context=None):
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        if company.custom_cubic_report:
            res = company.custom_cubic_report_src
        else:
            res = self._get_default_cubic_report(cr, uid, context=context)
        return res
    
    _name = "res.company"
    _inherit = "res.company"
    
    _columns = {
            'custom_cubic_report_layout': fields.selection([('1','One column'),
                                               ('2','Two Columns'),
                                               ('6','Six Columns'),
                                               ('8','Eight Columns'),],'Default Form Layout'),
            'custom_cubic_report': fields.boolean('Customize Cubic Report'),
            'custom_cubic_report_src': fields.text('Customized Cubic Report'),
        }
    _defaults = {
            'custom_cubic_report_layout': '1',
            'custom_cubic_report': False,
            'custom_cubic_report_src': _get_default_cubic_report,
        }