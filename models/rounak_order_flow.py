# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


FLOW_STATES = [
    ("cart", "Cart"),
    ("payment_pending", "Payment Pending"),
    ("payment_done", "Payment Received"),
    ("in_progress", "In Progress"),
    ("so_created", "Sales Order Created"),
    ("internal_verify", "Internal Verification"),
    ("vendor_approval", "Vendor Approval"),
    ("fulfillment", "Fulfillment"),
    ("activated", "Service Activated"),
    ("invoiced", "Invoiced"),
    ("done", "Done"),
    ("cancelled", "Cancelled"),
]


class RounakOrderFlow(models.Model):
    _name = "rounak.order.flow"
    _description = "Rounak Order Flow"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(required=True, default="/", readonly=True, copy=False)
    partner_id = fields.Many2one("res.partner", required=True, tracking=True)
    sale_order_id = fields.Many2one("sale.order", tracking=True, copy=False)
    invoice_id = fields.Many2one("account.move", tracking=True, copy=False)
    state = fields.Selection(FLOW_STATES, default="cart", required=True, tracking=True)

    discount_request_id = fields.Many2one("discount.request", copy=False)
    requires_vendor_approval = fields.Boolean()
    helpdesk_ticket_id = fields.Many2one("sh.helpdesk.ticket", copy=False)

    amount_total = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id,
    )
    note = fields.Text()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("rounak.order.flow") or "/"
                )
        return super().create(vals_list)

    # ── State transitions ────────────────────────────────────────────

    def _check_credit(self):
        self.ensure_one()
        partner = self.partner_id.commercial_partner_id
        if partner.rounak_transaction_blocked:
            raise UserError(
                _("Transactions are blocked for %s. Reason: %s")
                % (partner.name, partner.rounak_block_reason or "N/A")
            )
        if self.amount_total and partner.credit_limit:
            if partner.rounak_credit_balance + self.amount_total > partner.credit_limit:
                raise UserError(
                    _(
                        "Order AED %(amount)s exceeds credit available "
                        "(AED %(avail)s) for %(partner)s.",
                        amount=self.amount_total,
                        avail=partner.rounak_credit_available,
                        partner=partner.name,
                    )
                )

    def action_submit_payment(self):
        self._check_credit()
        self.write({"state": "payment_pending"})
        self._emit("order_payment_pending")

    def action_confirm_payment(self):
        self.write({"state": "payment_done"})
        self._emit("order_payment_done")
        self._log("status_change", "Payment confirmed", old_value="payment_pending", new_value="payment_done")

    def action_start_processing(self):
        self.write({"state": "in_progress"})
        self._emit("order_in_progress")

    def action_create_so(self):
        self.write({"state": "so_created"})
        self._emit("order_so_created")
        self._log("status_change", "Sales order created", new_value="so_created")

    def action_verify(self):
        self.write({"state": "internal_verify"})
        self._log("status_change", "Internal verification started")

    def action_request_vendor_approval(self):
        self.write({"state": "vendor_approval"})
        self._emit("vendor_approval_needed")
        self._log("status_change", "Vendor approval requested")

    def action_approve_vendor(self):
        self.write({"state": "fulfillment"})
        self._log("approval", "Vendor approved")

    def action_fulfill(self):
        self.write({"state": "fulfillment"})
        self._emit("order_fulfillment")

    def action_activate(self):
        self.write({"state": "activated"})
        self._emit("service_activated")
        self._log("status_change", "Service activated")

    def action_generate_invoice(self):
        self.write({"state": "invoiced"})
        self._emit("invoice_generated")
        self._log("status_change", "Invoice generated")

    def action_done(self):
        self.write({"state": "done"})
        self._log("status_change", "Order completed")

    def action_cancel(self):
        self.write({"state": "cancelled"})
        self._log("status_change", "Order cancelled")

    # ── Helpers ──────────────────────────────────────────────────────

    def _emit(self, code):
        self.ensure_one()
        user_ids = self.partner_id.user_ids[:1].ids
        if user_ids:
            self.env["rounak.notification"].emit(
                code=code,
                user_ids=user_ids,
                title=_("Order %s update", self.name),
                body=_(
                    "Your order status changed to: %s",
                    dict(FLOW_STATES).get(self.state, self.state),
                ),
                res_model=self._name,
                res_id=self.id,
            )

    def _log(self, action, summary, old_value=False, new_value=False):
        self.ensure_one()
        self.env["rounak.audit.log"].log(
            action=action,
            summary="%s — %s" % (self.name, summary),
            res_model=self._name,
            res_id=self.id,
            partner_id=self.partner_id.id,
            old_value=old_value,
            new_value=new_value,
        )
