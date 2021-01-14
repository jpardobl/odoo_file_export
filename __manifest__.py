# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Octupus Odoo File Export Module',
    'version': '0.1',
    'author': 'jpardo@octupus.es',
    'category': 'Customizations',
    'summary': 'Upload files from Odoo to multiple cloud file services',
    'description': """
Upload files from Odoo to multiple cloud file services
    """,
    'depends': ['mail'],
    'data': [
        'views/google_drive.xml',
        'views/settings.xml',
        'security/ir.model.access.csv'
    ],

    'demo': [],
    'installable': True,
    'auto_install': False
}
