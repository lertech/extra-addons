# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#              Julio Serna (julio@vauxoo.com)
#              Isaac Lopez (isaac@vauxoo.com)
#    Modified: Francisco Lercari (<flercari@lertech.com.ve>)
############################################################################
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
    "name" : "City",
    "version" : "1.1",
    "author" : "LerTech",
    "category" : "Localization/Venezuela",
    "description" : """
            This module creates the city model similar to states model and adds the field city_id on res partner.
            module create by Vauxoo and modified by LerTech for Venezuelan localization.
    """,
    "website" : "http://www.lertech.com.ve/",
    "license" : "AGPL-3",
    "depends" : [
            "base",
        ],
    "demo" : [],
    "data" : [
        'view/res_city.xml',
        'view/partner_address.xml',
        'security/city_security.xml',
        'security/ir.model.access.csv',
    ],
    "installable" : True,
    "active" : False,
}
