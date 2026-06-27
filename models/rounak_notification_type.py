# -*- coding: utf-8 -*-
"""Catalogue of notification trigger types.

Each record is one event the system can emit (quote pending, invoice overdue,
credit-limit warning, ...). Admins toggle a whole type on/off here; individual
users refine per-channel delivery via rounak.notification.preference.
"""
from odoo import api, fields, models


class RounakNotificationType(models.Model):
    _name = 'rounak.notification.type'
    _description = 'Rounak Notification Type'
    _order = 'category, sequence, name'

    name = fields.Char(required=True, translate=True)
    # Stable technical key used by code when emitting (e.g. 'quote_pending').
    code = fields.Char(required=True, index=True, help="Stable technical key used in code.")
    category = fields.Selection([
        ('sales', 'Sales & Quotations'),
        ('discount', 'Discount & Approval'),
        ('order', 'Orders & Fulfillment'),
        ('billing', 'Invoicing & Payments'),
        ('subscription', 'Subscriptions'),
        ('credit', 'Credit & Transaction Controls'),
        ('support', 'Support Tickets'),
        ('license', 'License Tickets'),
        ('security', 'Security'),
    ], required=True, default='sales')
    sequence = fields.Integer(default=10)
    # Master on/off switch for this trigger across the whole system.
    active = fields.Boolean(default=True)
    # Whether this is an internal-staff notification or customer-facing.
    audience = fields.Selection([
        ('customer', 'Customer'),
        ('internal', 'Internal Staff'),
        ('both', 'Both'),
    ], default='both', required=True)
    # Default channels suggested for new users (they can override).
    default_inapp = fields.Boolean(string='In-App by default', default=True)
    default_email = fields.Boolean(string='Email by default', default=True)
    # Optional default importance used when emitting.
    importance = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='normal', required=True)
    mail_template_id = fields.Many2one(
        'mail.template', string='Email Template',
        help="Branded template used when delivering this type by email.")
    description = fields.Text()

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Notification type code must be unique.'),
    ]

    @api.model
    def get_type(self, code):
        """Return an active type record by code, or empty recordset."""
        return self.search([('code', '=', code), ('active', '=', True)], limit=1)
