# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Vauxoo C.A.           
#    Planified by: Nhomar Hernandez
#    Audited by: Vauxoo C.A.
#    Modified: Francisco Lercari (<flercari@lertech.com.ve>)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

{
    "name" : "City of Venezuela",
    "version" : "1.1",
    "author" : "LerTech",
    "category" : "Localization/Venezuela",
    "description": """
        Load City of Venezuela
    """,
    "website" : "http://www.lertech.com.ve",
    "depends" : [
            "base",
        ],
    "demo" : [],
    "data" : [
        'res_city_view.xml',
        'partner_address_view.xml',
        'security/city_security.xml',
        'security/ir.model.access.csv',
    ],
    "installable" : True,
    "active" : False,
}
