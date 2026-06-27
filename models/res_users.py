# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    rounak_notification_preference_ids = fields.One2many(
        "rounak.notification.preference", "user_id",
        string="Notification Preferences",
    )
    rounak_notification_ids = fields.One2many(
        "rounak.notification", "user_id",
        string="Notifications",
    )
    rounak_unread_count = fields.Integer(
        compute="_compute_rounak_unread_count",
        string="Unread Notifications",
    )

    def _compute_rounak_unread_count(self):
        counts = {}
        if self.ids:
            self.env.cr.execute(
                "SELECT user_id, COUNT(*) FROM rounak_notification "
                "WHERE user_id IN %s AND is_read = false GROUP BY user_id",
                (tuple(self.ids),),
            )
            counts = dict(self.env.cr.fetchall())
        for user in self:
            user.rounak_unread_count = counts.get(user.id, 0)
