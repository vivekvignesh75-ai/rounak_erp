# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RounakNotification(models.Model):
    _name = "rounak.notification"
    _description = "Rounak Notification"
    _order = "create_date desc"

    user_id = fields.Many2one(
        "res.users", required=True, ondelete="cascade", index=True,
    )
    type_id = fields.Many2one(
        "rounak.notification.type", required=True, ondelete="restrict",
    )
    title = fields.Char(required=True)
    body = fields.Html(sanitize=True)
    importance = fields.Selection(
        [("low", "Low"), ("normal", "Normal"), ("high", "High"), ("urgent", "Urgent")],
        default="normal",
    )
    is_read = fields.Boolean(default=False, index=True)
    read_date = fields.Datetime()
    res_model = fields.Char(help="Related document model")
    res_id = fields.Many2oneReference(model_field="res_model", help="Related document ID")
    category = fields.Selection(related="type_id.category", store=True, readonly=True)

    # ── Actions ──────────────────────────────────────────────────────

    def action_mark_read(self):
        self.filtered(lambda n: not n.is_read).write(
            {"is_read": True, "read_date": fields.Datetime.now()}
        )

    def action_mark_unread(self):
        self.write({"is_read": False, "read_date": False})

    @api.model
    def mark_all_read(self, user_id=None):
        uid = user_id or self.env.uid
        unread = self.search([("user_id", "=", uid), ("is_read", "=", False)])
        unread.action_mark_read()
        return len(unread)

    @api.model
    def get_unread_count(self, user_id=None):
        uid = user_id or self.env.uid
        return self.search_count([("user_id", "=", uid), ("is_read", "=", False)])

    # ── Emitter (called by business logic throughout the system) ─────

    @api.model
    def emit(self, code, user_ids, title, body="", res_model=False, res_id=False, importance=False):
        ntype = self.env["rounak.notification.type"].get_type(code)
        if not ntype:
            return self.browse()

        created = self.browse()
        for uid in user_ids:
            rec = self.create({
                "user_id": uid,
                "type_id": ntype.id,
                "title": title,
                "body": body,
                "importance": importance or ntype.importance,
                "res_model": res_model,
                "res_id": res_id,
            })
            created |= rec

            pref = self.env["rounak.notification.preference"].sudo().search(
                [("user_id", "=", uid), ("type_id", "=", ntype.id)], limit=1,
            )
            send_email = pref.email if pref else ntype.default_email
            if send_email and ntype.mail_template_id:
                ntype.mail_template_id.send_mail(rec.id, force_send=False)

        return created
