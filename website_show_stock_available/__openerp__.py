# -*- coding: utf-8 -*-
{
    'name': "website_show_stock_available",

    'summary': """
        Adds text to show if product is available""",

    'description': """
        Adds some Qweb views to add text that says if product is available or not uses product.virtual_available
    """,

    'author': "Michael Hucke",
    'website': "http://www.hucke-media.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
    ],
}