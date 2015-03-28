# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#     Copyright (C) 2013 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    
    _columns = {
            'is_bank_voucher': fields.boolean('Bank Voucher'),
            'bank_statement_line_ids': fields.one2many('account.bank.statement.line','voucher_id',string="Statement Lines",
                                                       readonly=True),
        }
    _defaults = {
            'is_bank_voucher': False,
        }
    
    def filter_bank_voucher_ids_by_key(self, cr, uid, ids, key, context=None):
        if context is None: context={}
        voucher_ids = []
        if context.get(key,False):
            for v in self.read(cr,uid,ids,['is_bank_voucher'],context=context):
                if not v['is_bank_voucher']:
                    voucher_ids.append(v['id'])
        else:
            voucher_ids=ids
        return voucher_ids
    
    def unlink(self, cr, uid, ids, context=None):
        return super(account_voucher, self).unlink(cr, uid, 
                        self.filter_bank_voucher_ids_by_key(cr,uid,ids,'account_bank_voucher_unlink',context=context),
                        context=context)

    def cancel_voucher(self, cr, uid, ids, context=None):
        return super(account_voucher, self).cancel_voucher(cr, uid,
                        self.filter_bank_voucher_ids_by_key(cr,uid,ids,'account_bank_voucher_button_cancel',context=context),
                        context=context)        
        

class account_bank_statement(osv.osv):
    _inherit = 'account.bank.statement'

    def button_cancel(self, cr, uid, ids, context=None):
        if context is None: context={}
        context['account_bank_voucher_button_cancel'] = True
        return super(account_bank_statement, self).button_cancel(cr, uid, ids, context=context)


class account_bank_statement_line(osv.osv):
    _inherit = 'account.bank.statement.line'
    
    def unlink(self, cr, uid, ids, context=None):
        if context is None: context={}
        context['account_bank_voucher_unlink'] = True
        return super(account_bank_statement_line, self).unlink(cr, uid, ids, context=context)