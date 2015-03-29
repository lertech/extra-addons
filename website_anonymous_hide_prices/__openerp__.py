# -*- coding: utf-8 -*-
{
    'name': "website_anonymous_hide_prices",

    'summary': """
        Hide prices, quantity select and "add to cart" button if user is not authenticated""",

    'description': """
        Adds some Qweb views to replace sections on page which will be hidden if user ist not authenticated
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