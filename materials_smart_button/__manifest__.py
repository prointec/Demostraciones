# -*- coding: utf-8 -*-
{
    'name': "Materials Smart Button",
    'summary':
        """
            This module is built to create the new requirements related to adding
            the smart button and its functionality on the Sale Order.
        """,

    'author': "Fazal Ur Rahman",
    'category': 'Extra Tools',
    'version': '14.0.0.1',

    'depends': ['base', 'sale'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'wizards/wizards.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'auto_install': False,
    'installable': True,
}
