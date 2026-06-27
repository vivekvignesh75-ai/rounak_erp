# -*- coding: utf-8 -*-
{
    'name': 'Rounak ERP',
    'summary': 'Rounak Computers - internal ERP: notifications, approval workflow, '
               'credit & transaction controls, audit log, role-based dashboard.',
    'description': """
Rounak ERP (rounak_erp)
=======================
Internal backend for Rounak Computers LLC (Microsoft CSP / IT managed services, Dubai UAE).

Provides the engine layer consumed by the customer portal (rounak_portal):

* Unified in-app notification model (rounak.notification) with bell/inbox, per-user
  channel preferences, mark-as-read, unread badge counts.
* Order -> fulfillment state machine (rounak.order.flow) and discount/credit/block controls.
* Admin-configurable control rules (rounak.control.rule): credit limits, discount
  thresholds, payment terms, auto-block conditions.
* Audit log (rounak.audit.log) for approvals, blocks, status changes.
* Role-based security groups: Customer / Sales / Accounts / Service / Licensing /
  Manager / Admin (record rules enforce per-company data isolation).
* Branded email templates that respect the distributor firewall.

Designed to coexist with adigielite_it_service without overriding its routes,
models, channels or third-party modules. All identifiers are namespaced `rounak_*`.
    """,
    'version': '17.0.1.0.0',
    'category': 'Services/IT',
    'license': 'LGPL-3',
    'author': 'Rounak Computers',
    'website': 'https://www.rounakcomputers.com',
    'depends': [
        'base',
        'mail',
        'web',
        'portal',
        'website',
        'sale',
        'sale_management',
        'account',
        'adigielite_it_service',
    ],
    'data': [
        'security/rounak_groups.xml',
        'security/ir.model.access.csv',
        'security/rounak_record_rules.xml',
        'data/rounak_notification_type_data.xml',
        'data/rounak_control_rule_data.xml',
        'data/mail_template_rounak_notification.xml',
        'data/rounak_cron.xml',
        'views/rounak_notification_views.xml',
        'views/rounak_notification_preference_views.xml',
        'views/rounak_control_rule_views.xml',
        'views/rounak_audit_log_views.xml',
        'views/res_partner_views.xml',
        'views/rounak_dashboard_action.xml',
        'views/license_ticket_views.xml',
        'views/res_config_settings_views.xml',
        'views/rounak_erp_menus.xml',
    ],
    'demo': [
        'demo/rounak_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rounak_erp/static/src/scss/rounak_fluent.scss',
            'rounak_erp/static/src/scss/rounak_dashboard.scss',
            'rounak_erp/static/src/js/notification_bell.js',
            'rounak_erp/static/src/js/rounak_dashboard.js',
            'rounak_erp/static/src/xml/notification_bell.xml',
            'rounak_erp/static/src/xml/rounak_dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
