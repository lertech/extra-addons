# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 LerTech (<http://www.lertech.com.ve>).
#    Modified: Francisco Lercari <flercari@lertech.com.ve>,
#
#    Created: 2014-06-16
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
##############################################################################

{
    'name': 'Estates Venezuela',
    'version': '0.1',
    'author': ['LerTech','FJGM'],
    'category': 'Localization',
    'website': 'http://www.lertech.com.ve/',
    'license': 'GPL-3',
    'description': """
Load Estates of Venezuela
""",
    'depends': [
        'base',
    ],
    'test': [],
    'data': [
        'data/ve_states.xml',
    ],
    'active': False,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
