# -*- coding: utf-8 -*-
{
    'name': 'Bank of Venezuelan',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'summary': 'list Bank of Venezuelan',
    'website': 'https://www.lertech.com.ve/',
    'version': '8.0.1.0',
    'description': """
Load Bank of Venezuela
""",
    'author': 'LerTech',
    'images' : [],
    'depends': [
        'base',
        'l10n_ve'
    ],
    'data': [
        'data/ve_bank.xml',
    ],
    'demo': [],
    'test': [],
}

