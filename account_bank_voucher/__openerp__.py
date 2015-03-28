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
{
    "name": "Bank and Cash Statement with Vouchers",
    "version": "1.0",
    "description": """
Manage the bank/cash reconciliation with account vouchers (payments and receipts)
=================================================================================

The management of treasury require integrate the payments of customers and suppliers to bank statements, allowing real bank reconciliations.

Key Features
------------
* Add button on bank statement to add vouchers
* Integrate the account vouchers with the bank statements
* Optimize the payments and receipts in treasury management
* Fix some features on bank statements to enable the bank reconciliation

    """,
    "author": "Cubic ERP",
    "website": "http://cubicERP.com",
    "category": "Financial",
    "depends": [
        "account",
        "account_voucher",
        ],
    "data":[
        "wizard/bank_statement_populate_view.xml",
        "account_view.xml",
        "wizard/account_statement_from_invoice_view.xml",
	    ],
    "demo_xml": [],
    "active": False,
    "installable": True,
    "certificate" : "",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: