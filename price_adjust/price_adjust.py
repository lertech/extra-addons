# -*- coding: utf-8 -*-
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
#############################################################################
from openerp.osv import osv
from openerp.osv import fields
import time

class price_adjust_history(osv.osv):
    _name = 'price_adjust.history'
    _description = 'Price Adjust History'
    _columns = {
        'name': fields.char('Name', size=64, required=True, select=True),
        'comment': fields.char('Comment', size=128),
        'user': fields.many2one('res.users', 'User', required=True, readonly=True),
        'date': fields.datetime('Date', readonly=True),
        'categories': fields.many2many('product.category', 'price_adjust_history_category_rel', 'history_id', 'categ_id', 'Categories Adjusted', readonly=True),
        'basedon': fields.selection([('standard_price', 'Cost price'), ('list_price', 'List price')], 'Base Price', readonly=True),
        'adjust': fields.selection([('standard_price', 'Cost price'), ('list_price', 'List price')], 'Adjusted Price', readonly=True),
        'amount': fields.float('Base * ', readonly=True),
        'plus': fields.float(' + ', readonly=True),
        'total': fields.integer('Affected', required=True, readonly=True),
    }

    _defaults = {
        'user': lambda self, cr, uid, context: uid,
        'name': lambda *a: 'ADJ' + time.strftime('%Y%m%d'),
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'amount': lambda *a: 1.0,
        'plus': lambda *a: 0.0,
    }
price_adjust_history()
