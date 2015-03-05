# -*- encoding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import netsvc

import amount_to_text_es_VE

class account_invoice(osv.Model):
    _inherit = 'account.invoice'

    def _get_amount_to_text(self, cr, uid, ids, field_names=None, arg=False,
        context={}):
        if not context:
            context = {}
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            amount_to_text = amount_to_text_es_VE.get_amount_to_text(
                self, invoice.amount_total, 'es_cheque', 'code' in invoice.\
                currency_id._columns and invoice.currency_id.code or invoice.\
                currency_id.name)
            res[invoice.id] = amount_to_text
        return res

    _columns = {
        'amount_to_text':  fields.function(_get_amount_to_text, method=True,
            type='char', size=256, string='Amount to Text', store=True,
            help='Amount of the invoice in letter'),
    }
