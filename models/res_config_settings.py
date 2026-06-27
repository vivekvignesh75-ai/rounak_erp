# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    rounak_default_credit_limit = fields.Float(
        string="Default Customer Credit Limit (AED)",
        config_parameter="rounak_erp.default_credit_limit",
        default=50000.0,
    )
    rounak_auto_block_overdue_days = fields.Integer(
        string="Auto-block after overdue days",
        config_parameter="rounak_erp.auto_block_overdue_days",
        default=30,
        help="Block new transactions when a customer has invoices overdue by this many days.",
    )
    rounak_discount_auto_threshold = fields.Float(
        string="Auto-approve discount up to (%)",
        config_parameter="rounak_erp.discount_auto_threshold",
        default=17.0,
        help="Discounts at or below this % are auto-approved by Account Manager.",
    )
    rounak_discount_escalation_threshold = fields.Float(
        string="Escalation discount above (%)",
        config_parameter="rounak_erp.discount_escalation_threshold",
        default=17.0,
        help="Discounts above this % require Manager approval.",
    )
    rounak_notifications_enabled = fields.Boolean(
        string="Enable Rounak Notifications",
        config_parameter="rounak_erp.notifications_enabled",
        default=True,
    )
    rounak_email_notifications = fields.Boolean(
        string="Send email notifications",
        config_parameter="rounak_erp.email_notifications",
        default=True,
    )
