# -*- coding: utf-8 -*-
"""Extend discount.request with counter-offer flow and notification hooks."""
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DiscountRequest(models.Model):
    _inherit = "discount.request"

    counter_offer_pct = fields.Float(string="Counter-Offer (%)")
    counter_offer_reason = fields.Text(string="Counter-Offer Reason")
    counter_offer_state = fields.Selection(
        [
            ("none", "No Counter-Offer"),
            ("offered", "Counter-Offer Sent"),
            ("accepted", "Customer Accepted"),
            ("declined", "Customer Declined"),
        ],
        default="none",
        string="Counter-Offer Status",
    )

    def action_counter_offer(self):
        for rec in self:
            if not rec.counter_offer_pct:
                raise UserError(_("Please enter a counter-offer percentage."))
            rec.write({
                "counter_offer_state": "offered",
                "state": "pending",
            })
            self.env["rounak.audit.log"].log(
                "discount_request",
                _("Counter-offer %s%% on %s (was %s%%)",
                  rec.counter_offer_pct, rec.sale_order_id.name, rec.requested_discount_pct),
                res_model="discount.request",
                res_id=rec.id,
                partner_id=rec.partner_id.id,
                old_value=rec.requested_discount_pct,
                new_value=rec.counter_offer_pct,
            )
            customer_users = rec.partner_id.user_ids or rec.sale_order_id.partner_id.user_ids
            if customer_users:
                self.env["rounak.notification"].emit(
                    code="discount_requested",
                    user_ids=customer_users[:1].ids,
                    title=_("Counter-offer on %s", rec.sale_order_id.name),
                    body=_(
                        "Your %s%% discount request received a counter-offer of %s%%. "
                        "Reason: %s",
                        rec.requested_discount_pct,
                        rec.counter_offer_pct,
                        rec.counter_offer_reason or "N/A",
                    ),
                    res_model="discount.request",
                    res_id=rec.id,
                )

    def action_customer_accept_counter(self):
        for rec in self:
            if rec.counter_offer_state != "offered":
                continue
            rec.write({"counter_offer_state": "accepted", "state": "approved"})
            rec._sync_sale_order_state()
            self.env["rounak.audit.log"].log(
                "discount_approve",
                _("Customer accepted counter-offer %s%% on %s",
                  rec.counter_offer_pct, rec.sale_order_id.name),
                res_model="discount.request",
                res_id=rec.id,
                partner_id=rec.partner_id.id,
            )
            self.env["rounak.notification"].emit(
                code="discount_approved",
                user_ids=rec.user_id.ids if rec.user_id else [],
                title=_("Counter-offer accepted: %s", rec.sale_order_id.name),
                body=_("Customer accepted %s%% counter-offer.", rec.counter_offer_pct),
                res_model="discount.request",
                res_id=rec.id,
            )

    def action_customer_decline_counter(self):
        for rec in self:
            if rec.counter_offer_state != "offered":
                continue
            rec.write({"counter_offer_state": "declined"})
            self.env["rounak.audit.log"].log(
                "discount_reject",
                _("Customer declined counter-offer on %s", rec.sale_order_id.name),
                res_model="discount.request",
                res_id=rec.id,
                partner_id=rec.partner_id.id,
            )
            self.env["rounak.notification"].emit(
                code="discount_rejected",
                user_ids=rec.user_id.ids if rec.user_id else [],
                title=_("Counter-offer declined: %s", rec.sale_order_id.name),
                body=_("Customer declined the %s%% counter-offer. Original price retained.",
                       rec.counter_offer_pct),
                res_model="discount.request",
                res_id=rec.id,
            )

    def action_approve(self):
        res = super().action_approve()
        for rec in self.filtered(lambda r: r.state == "approved"):
            self.env["rounak.audit.log"].log(
                "discount_approve",
                _("Discount %s%% approved on %s", rec.requested_discount_pct,
                  rec.sale_order_id.name if rec.sale_order_id else rec.partner_id.name),
                res_model="discount.request",
                res_id=rec.id,
                partner_id=rec.partner_id.id,
            )
            customer_users = rec.partner_id.user_ids or (
                rec.sale_order_id.partner_id.user_ids if rec.sale_order_id else self.env["res.users"]
            )
            if customer_users:
                self.env["rounak.notification"].emit(
                    code="discount_approved",
                    user_ids=customer_users[:1].ids,
                    title=_("Discount approved on %s",
                            rec.sale_order_id.name if rec.sale_order_id else "your account"),
                    body=_("Your %s%% discount request has been approved.", rec.requested_discount_pct),
                    res_model="discount.request",
                    res_id=rec.id,
                )
        return res

    def action_reject(self):
        res = super().action_reject()
        for rec in self.filtered(lambda r: r.state == "rejected"):
            self.env["rounak.audit.log"].log(
                "discount_reject",
                _("Discount %s%% rejected on %s", rec.requested_discount_pct,
                  rec.sale_order_id.name if rec.sale_order_id else rec.partner_id.name),
                res_model="discount.request",
                res_id=rec.id,
                partner_id=rec.partner_id.id,
            )
            customer_users = rec.partner_id.user_ids or (
                rec.sale_order_id.partner_id.user_ids if rec.sale_order_id else self.env["res.users"]
            )
            if customer_users:
                self.env["rounak.notification"].emit(
                    code="discount_rejected",
                    user_ids=customer_users[:1].ids,
                    title=_("Discount request declined"),
                    body=_("Your %s%% discount request was declined. Reason: %s",
                           rec.requested_discount_pct, rec.manager_reason or "N/A"),
                    res_model="discount.request",
                    res_id=rec.id,
                )
        return res
