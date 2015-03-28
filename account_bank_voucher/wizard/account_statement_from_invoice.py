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

import time
from lxml import etree
from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_statement_from_invoice_lines(osv.osv_memory):
    _inherit = "account.statement.from.invoice.lines"

#    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
#        res = super(account_statement_from_invoice_lines, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
#        if view_type == 'form':
#            doc = etree.XML(res['arch'])
#            nodes = doc.xpath("//field[@name='line_ids']")
#            for node in nodes:
#                node.append(etree.XML("""<tree><field name="name"/></tree>"""))
#            res['arch'] = etree.tostring(doc)
#        return res

    def populate_statement(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        statement_id = context.get('statement_id', False)
        if not statement_id:
            return {'type': 'ir.actions.act_window_close'}
        data =  self.read(cr, uid, ids, context=context)[0]
        line_ids = data['line_ids']
        if not line_ids:
            return {'type': 'ir.actions.act_window_close'}

        line_obj = self.pool.get('account.move.line')
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
#        currency_obj = self.pool.get('res.currency')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        line_date = time.strftime('%Y-%m-%d')
        statement = statement_obj.browse(cr, uid, statement_id, context=context)

        # for each selected move lines
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            voucher_res = {}
            ctx = context.copy()
            #  take the date for computation of currency => use payment date
            ctx['date'] = line_date
            
            #YT 2013/01/10
            amount = line.debit or line.credit 
            sign = 1.0
            if line.credit > 0: sign = -1.0
            if line.reconcile_partial_id:
                amount = reduce(lambda y,t: (t.debit or 0.0) - (t.credit or 0.0) + y, line.reconcile_partial_id.line_partial_ids, 0.0)
            amount = sign * amount
#            if line.amount_currency:
#                amount = currency_obj.compute(cr, uid, line.currency_id.id,
#                    statement.currency.id, line.amount_currency, context=ctx)
#            elif (line.invoice and line.invoice.currency_id.id <> statement.currency.id):
#                amount = currency_obj.compute(cr, uid, line.invoice.currency_id.id,
#                    statement.currency.id, amount, context=ctx)

            context.update({'move_line_ids': [line.id],
                            'invoice_id': line.invoice.id})
            type = 'general'
            ttype = amount < 0 and 'payment' or 'receipt'
            sign = 1
            if line.journal_id.type in ('sale', 'sale_refund'):
                type = 'customer'
                ttype = 'receipt'
            elif line.journal_id.type in ('purchase', 'purhcase_refund'):
                type = 'supplier'
                ttype = 'payment'
                sign = -1
            result = voucher_obj.onchange_partner_id(cr, uid, [], partner_id=line.partner_id.id, journal_id=statement.journal_id.id, amount=sign*amount, currency_id= statement.currency.id, ttype=ttype, date=line_date, context=context)
            voucher_res = { 'type': ttype,
                            'name': line.name,
                            'partner_id': line.partner_id.id,
                            'journal_id': statement.journal_id.id,
                            'account_id': result['value'].get('account_id', statement.journal_id.default_credit_account_id.id),
                            'company_id': statement.company_id.id,
                            'currency_id': statement.currency.id,
                            'date': line.date,
                            'amount': sign*amount,
                            'payment_rate': result['value']['payment_rate'],
                            'payment_rate_currency_id': result['value']['payment_rate_currency_id'],
                            'period_id':statement.period_id.id}
            voucher_id = voucher_obj.create(cr, uid, voucher_res, context=context)

            voucher_line_dict =  {}
            for line_dict in result['value']['line_cr_ids'] + result['value']['line_dr_ids']:
                move_line = line_obj.browse(cr, uid, line_dict['move_line_id'], context)
                if line.move_id.id == move_line.move_id.id:
                    voucher_line_dict = line_dict

            if voucher_line_dict:
                voucher_line_dict.update({'voucher_id': voucher_id})
                voucher_line_obj.create(cr, uid, voucher_line_dict, context=context)
            statement_line_obj.create(cr, uid, {
                'name': line.name or '?',
                'amount': amount,
                'type': type,
                'partner_id': line.partner_id.id,
                'account_id': line.account_id.id,
                'statement_id': statement_id,
                'ref': line.ref,
                'voucher_id': voucher_id,
                'date': time.strftime('%Y-%m-%d'),
            }, context=context)
        return {'type': 'ir.actions.act_window_close'}