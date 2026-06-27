# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RounakAuditLog(models.Model):
    _name = "rounak.audit.log"
    _description = "Rounak Audit Log"
    _order = "create_date desc"
    _rec_name = "summary"

    user_id = fields.Many2one(
        "res.users", required=True, default=lambda self: self.env.uid,
    )
    action = fields.Selection(
        [
            ("approval", "Approval"),
            ("rejection", "Rejection"),
            ("block", "Transaction Block"),
            ("unblock", "Transaction Unblock"),
            ("credit_change", "Credit Limit Change"),
            ("discount_request", "Discount Request"),
            ("discount_approve", "Discount Approved"),
            ("discount_reject", "Discount Rejected"),
            ("status_change", "Status Change"),
            ("portal_lock", "Portal Lock"),
            ("portal_unlock", "Portal Unlock"),
            ("config_change", "Configuration Change"),
        ],
        required=True,
    )
    summary = fields.Char(required=True)
    detail = fields.Text()
    res_model = fields.Char(index=True)
    res_id = fields.Integer(index=True)
    old_value = fields.Char()
    new_value = fields.Char()
    partner_id = fields.Many2one("res.partner", index=True)

    @api.model
    def log(
        self,
        action,
        summary,
        res_model=False,
        res_id=False,
        old_value=False,
        new_value=False,
        partner_id=False,
        detail=False,
    ):
        return self.sudo().create(
            {
                "user_id": self.env.uid,
                "action": action,
                "summary": summary,
                "res_model": res_model,
                "res_id": res_id,
                "old_value": str(old_value) if old_value is not False else False,
                "new_value": str(new_value) if new_value is not False else False,
                "partner_id": partner_id,
                "detail": detail,
            }
        )
