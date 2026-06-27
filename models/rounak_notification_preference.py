# -*- coding: utf-8 -*-
from odoo import fields, models


class RounakNotificationPreference(models.Model):
    _name = "rounak.notification.preference"
    _description = "Rounak Notification Preference"
    _rec_name = "type_id"

    user_id = fields.Many2one(
        "res.users", required=True, ondelete="cascade", index=True,
    )
    type_id = fields.Many2one(
        "rounak.notification.type", required=True, ondelete="cascade",
    )
    inapp = fields.Boolean(string="In-App", default=True)
    email = fields.Boolean(string="Email", default=True)

    _sql_constraints = [
        (
            "user_type_uniq",
            "unique(user_id, type_id)",
            "One preference per user per notification type.",
        ),
    ]
