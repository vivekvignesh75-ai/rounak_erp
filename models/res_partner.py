# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    rounak_credit_balance = fields.Monetary(
        string="Credit Balance Used", currency_field="currency_id",
    )
    rounak_credit_available = fields.Monetary(
        string="Credit Available",
        compute="_compute_rounak_credit_available",
        currency_field="currency_id",
    )
    rounak_transaction_blocked = fields.Boolean(string="Transaction Blocked")
    rounak_block_reason = fields.Char()
    rounak_portal_locked = fields.Boolean(string="Portal Locked")
    rounak_payment_terms_code = fields.Selection(
        [
            ("net_0", "Net 0"),
            ("net_15", "Net 15"),
            ("net_30", "Net 30"),
            ("net_45", "Net 45"),
        ],
        default="net_30",
        string="Rounak Payment Terms",
    )

    @api.depends("credit_limit", "rounak_credit_balance")
    def _compute_rounak_credit_available(self):
        for p in self:
            p.rounak_credit_available = p.credit_limit - p.rounak_credit_balance

    def action_block_transactions(self, reason=""):
        self.ensure_one()
        self.env["rounak.audit.log"].log(
            "block",
            _("Blocked transactions: %s", self.name),
            res_model="res.partner",
            res_id=self.id,
            partner_id=self.id,
            new_value=reason,
        )
        self.write({"rounak_transaction_blocked": True, "rounak_block_reason": reason})
        if self.user_ids:
            self.env["rounak.notification"].emit(
                code="transaction_blocked",
                user_ids=self.user_ids.ids,
                title=_("Account transactions blocked"),
                body=_("Reason: %s", reason or "Contact your account manager."),
                res_model="res.partner",
                res_id=self.id,
                importance="urgent",
            )

    def action_unblock_transactions(self):
        self.ensure_one()
        self.env["rounak.audit.log"].log(
            "unblock",
            _("Unblocked transactions: %s", self.name),
            res_model="res.partner",
            res_id=self.id,
            partner_id=self.id,
        )
        self.write({
            "rounak_transaction_blocked": False,
            "rounak_block_reason": False,
            "rounak_portal_locked": False,
        })
        if self.user_ids:
            self.env["rounak.notification"].emit(
                code="transaction_unblocked",
                user_ids=self.user_ids.ids,
                title=_("Account transactions unblocked"),
                body=_("Your account is now active. You can place orders again."),
                res_model="res.partner",
                res_id=self.id,
            )

    def action_lock_portal(self):
        self.ensure_one()
        self.env["rounak.audit.log"].log(
            "portal_lock",
            _("Portal locked: %s", self.name),
            res_model="res.partner",
            res_id=self.id,
            partner_id=self.id,
        )
        self.rounak_portal_locked = True

    def action_unlock_portal(self):
        self.ensure_one()
        self.env["rounak.audit.log"].log(
            "portal_unlock",
            _("Portal unlocked: %s", self.name),
            res_model="res.partner",
            res_id=self.id,
            partner_id=self.id,
        )
        self.rounak_portal_locked = False

    @api.model
    def _cron_rounak_overdue_check(self):
        threshold = int(
            self.env["rounak.control.rule"].get_float("auto_block_overdue_days", 30)
        )
        cutoff = fields.Date.subtract(fields.Date.today(), days=threshold)
        overdue_partners = self.env["account.move"].search([
            ("move_type", "=", "out_invoice"),
            ("payment_state", "not in", ("paid", "reversed")),
            ("invoice_date_due", "<", cutoff),
            ("state", "=", "posted"),
        ]).mapped("partner_id.commercial_partner_id")
        for partner in overdue_partners:
            if not partner.rounak_transaction_blocked:
                partner.action_block_transactions(
                    reason=_("Auto-blocked: invoices overdue > %s days", threshold)
                )
