# -*- encoding: utf-8 -*-
#
#
#    Price Adjustment Addon for OpenERP
#    Copyright (C) 2004-2009 Bubbles-IT (<http://bubbles-it.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################

#import wizard
import pooler
from openerp.tools.translate import _  # Used for translations

import time

view_form = """<?xml version="1.0"?>
<form string="%s">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
	<separator string="%s" colspan="4"/>
	<field name="category" colspan="4" height="200" nolabel="1"/>
	<field name="descend" colspan="4"/>
	<separator string="%s" colspan="4"/>
	<field name="adjust"/>
	<field name="basedon"/>
	<separator string="%s" colspan="4"/>
	<field name="amount"/><field name="plus"/>
    </group>
</form>""" % ( _("Adjust Product Prices"), _("Select Categories"), _("Select price to adjust and which to base on"), _("Price Computation") )

fields_form = {
    'category': {'string': 'Product Category', 'type': 'many2many', 'relation': 'product.category'},
    'descend': {'string': 'Also adjust child categories', 'type': 'boolean', 'default': lambda *a: False},
    'adjust': {'string': 'Adjust', 'type': 'selection', 'selection': [('standard_price', 'Cost Price'), ('list_price', 'List Price')], 'required': True, 'default': lambda *a: 'standard_price'},
    'basedon': {'string': 'Based on', 'type': 'selection', 'selection': [('standard_price', 'Cost Price'), ('list_price', 'List Price')], 'required': True, 'default': lambda *a: 'standard_price'},
    'amount': {'string': 'Base * ', 'type': 'float', 'default': lambda *a: 1.0},
    'plus': {'string': ' + ', 'type': 'float', 'default': lambda *a: 0.0},
}


class price_adjust_wizard(wizard.interface):

    def _get_sub_category(self, cr, uid, ids):
        pool = pooler.get_pool(cr.dbname)
        cat_obj = pool.get('product.category')

        res = []
        res += ids
        for id in ids:
            children = cat_obj.read(cr, uid, [id])[0]['child_id']
            res += self._get_sub_category(cr, uid, children)
        return res

    def _adjust_prices(self, cr, uid, data, context):
        form = data['form']

        # Put list of category from form here
        list_cat = form['category'][0][2]
        if form['descend']:
            # We need to get all subcategories in this list
            list_cat += self._get_sub_category(cr, uid, list_cat)
            list_cat = list(set(list_cat))

        pool = pooler.get_pool(cr.dbname)
        prod_obj = pool.get('product.product')

        prod_list = prod_obj.search(cr, uid, [('categ_id', 'in', list_cat)])

        products = prod_obj.read(cr, uid, prod_list)
        tmpl_ids = [prod['product_tmpl_id'] for prod in products]

        print """ UPDATE product_template SET %s = %s * %f + %f WHERE id IN (%s)""" % (form['adjust'], form['basedon'], form['amount'], form['plus'], ','.join([ str(t[0]) for t in tmpl_ids]))
        cr.execute(""" UPDATE product_template SET %s = %s * %f + %f WHERE id IN (%s)""" % (
            form['adjust'], form['basedon'], form['amount'], form['plus'], ','.join([str(t[0]) for t in tmpl_ids])))

        hist_obj = pool.get('price_adjust.history')
        data = {
            'user': uid,
            'categories': [(6, 0, list_cat)],
            'basedon': form['basedon'],
            'adjust': form['adjust'],
            'amount': form['amount'],
            'plus': form['plus'] or 0.0,
            'total': len(tmpl_ids),
        }
        print "Hist obj", data
        created_id = hist_obj.create(cr, uid, data)
        return {
            'domain': [('id', '=', created_id)],
            'name': _('Price Adjust History'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'price_adjust.history',
            'type': 'ir.actions.act_window',
        }

    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'form',
                'arch': view_form,
                'fields': fields_form,
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('finish', 'Ok', 'gtk-ok', True),
                ]
            }
        },
        'finish': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': _adjust_prices,
                'state': 'end',
            }
        },
    }
price_adjust_wizard('price_adjust.price_adjust_wizard')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
