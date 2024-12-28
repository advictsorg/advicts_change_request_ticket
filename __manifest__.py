# -*- coding: utf-8 -*-
# Copyright 2024  Advicts LTD.
# Part of Advicts. See LICENSE file for full copyright and licensing details.
{
    'name': "Advicts Change Request Ticket",
    'description': """
       Change Request Ticket Management
    """,
    'summary': """ Change Request Ticket Management""",
    'version': "1.0",
    'author': 'Advicts LTD.',
    'company': 'Advicts LTD.',
    'maintainer': 'Advicts LTD.',
    'website': "https://www.advicts.com",
    'category': 'Services',
    'depends': ['mail', 'advicts_advance_helpdesk', 'contacts'],
    'data': [
        # security
        'security/ir.model.access.csv',
        'security/security.xml',
        # data
        'data/sequence.xml',
        'data/templates.xml',

        # Views
        'views/wizard.xml',
        'views/assets.xml',
        'views/change_request.xml',
        'views/res_config_view.xml',
        # Menus
        'views/menus.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'advicts_change_request_ticket/static/src/xml/template.xml',
            'advicts_change_request_ticket/static/src/css/style.scss',
            'advicts_change_request_ticket/static/src/js/lib/moment.min.js',
            'advicts_change_request_ticket/static/src/js/lib/apexcharts.js',
            'advicts_change_request_ticket/static/src/js/cr_dashboard.js',
            # 'advicts_change_request_ticket/static/src/js/change_request.js',
        ],
        'web.assets_frontend': [
            'advicts_change_request_ticket/static/src/css/theme.css',
            'advicts_change_request_ticket/static/src/js/cr.js',
            'advicts_change_request_ticket/static/src/js/custom.js',
            'advicts_change_request_ticket/static/src/js/bootstrap-multiselect.js',
        ],
    },
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
