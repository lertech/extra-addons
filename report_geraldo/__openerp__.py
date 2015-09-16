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
    "name": "Cubic Report Engine based on Geraldo Reports",
    "version": "0.1",
    "description": """
Add Cubic Report Engine with Object Oriented Reports and Bands Support
======================================================================
Cubic Report engine is fully integrated to OpenERP, and allows make reports based on report objects, templates or JSON definitions.

Main Features
-------------
* Use objects and hierance to define your report
* Use a dictionary definition to make easy reports
* Generate reports with page header and footer, child bands, report begin and summary bands, agreggation and graphic elements
* Generate output on PDF for graphical printers (ink, laser and others)
* Generate output on RAW TXT PRN for better printing on character based printers (dot matrix)
* Generate output on CSV to export data to any spreadsheet
* The source of the report may be a browseable object or a SQL definition
* Support integrated definition of arguments to filter your Cubic Report

Main Libraries
--------------
* Geraldo Reports http://www.geraldoreports.org/
* ReportLab https://bitbucket.org/rptlab/reportlab

Installation
------------
Cubic Report engine, need the Geraldo library installed on your system, in order to install this library use the cross platform easy_install:

    $ easy_install Geraldo

Documentation
-------------
* Intro video http://youtu.be/wdz2EtLToFc
* Reference http://cubicerp.com/cubicReport

About the Author
----------------
Cubic ERP has started projects with OpenERP from 2009, and initiated as OpenERP CTP Partner from 2011. We are expert consultors with certification FEC-V7 of OpenERP, and top contributors on apps.openerp.com with more than 75 modules published and 5 modules included on ofiicial release of OpenERP.
    """,
    "author": "Cubic ERP",
    "website": "http://cubicERP.com",
    "category": "Reporting",
    "depends": ["base_report"],
    "data":[
        'ir_actions_view.xml',
        'ir_model_view.xml',
        'res_company_view.xml',
    ],
    "demo_xml": [ ],
    "js": [
    ],
    'qweb' : [
    ],
    'external_dependencies' : {
        'python' : ['geraldo'],
    },
    "active": False,
    "installable": True,
    "certificate" : "",
}
