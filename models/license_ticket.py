# -*- coding: utf-8 -*-
"""License ticket queue extensions: overdue flagging, quantity math,
distributor firewall, approval gates."""
from datetime import timedelta
from odoo import _, api, fields, models


class HelpdeskTicketLicense(models.Model):
    _inherit = "sh.helpdesk.ticket"

    rounak_license_type = fields.Selection(
        [
            ("professional_service", "Professional Service"),
            ("qty_increase", "Quantity Increase"),
        ],
        string="License Type",
    )
    rounak_current_qty = fields.Float(string="Current Quantity")
    rounak_increase_qty = fields.Float(string="Increase By")
    rounak_new_total_qty = fields.Float(
        string="New Total",
        compute="_compute_rounak_new_total_qty",
        store=True,
    )
    rounak_is_overdue = fields.Boolean(
        string="Overdue (>2 days)",
        compute="_compute_rounak_is_overdue",
        search="_search_rounak_is_overdue",
    )
    rounak_days_open = fields.Integer(
        string="Days Open",
        compute="_compute_rounak_is_overdue",
    )
    rounak_provisioning_approved = fields.Boolean(string="Provisioning Approved")
    rounak_close_approved = fields.Boolean(string="Close Approved")

    # Distributor fields — internal only, never exposed to customer-facing views
    rounak_distributor_id = fields.Many2one(
        "res.partner", string="Distributor (Internal)",
        groups="rounak_erp.group_rounak_licensing",
    )
    rounak_distributor_portal = fields.Char(
        string="Distributor Portal (Internal)",
        groups="rounak_erp.group_rounak_licensing",
    )
    rounak_distributor_discount = fields.Float(
        string="Distributor Discount (Internal)",
        groups="rounak_erp.group_rounak_licensing",
    )
    rounak_our_cost = fields.Monetary(
        string="Our Cost (Internal)",
        currency_field="company_currency_id",
        groups="rounak_erp.group_rounak_licensing",
    )
    company_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        store=True,
    )

    @api.depends("rounak_current_qty", "rounak_increase_qty")
    def _compute_rounak_new_total_qty(self):
        for t in self:
            t.rounak_new_total_qty = t.rounak_current_qty + t.rounak_increase_qty

    @api.depends("create_date", "stage_id")
    def _compute_rounak_is_overdue(self):
        now = fields.Datetime.now()
        for t in self:
            if t.create_date and not (hasattr(t.stage_id, 'closed') and t.stage_id.closed):
                delta = now - t.create_date
                t.rounak_days_open = delta.days
                t.rounak_is_overdue = delta > timedelta(days=2)
            else:
                t.rounak_days_open = 0
                t.rounak_is_overdue = False

    def _search_rounak_is_overdue(self, operator, value):
        cutoff = fields.Datetime.now() - timedelta(days=2)
        if (operator == "=" and value) or (operator == "!=" and not value):
            return [("create_date", "<", cutoff), ("stage_id.closed", "=", False)]
        return ["|", ("create_date", ">=", cutoff), ("stage_id.closed", "=", True)]

    def action_approve_provisioning(self):
        for t in self:
            t.rounak_provisioning_approved = True
            self.env["rounak.audit.log"].log(
                "approval",
                _("Provisioning approved for license ticket %s", t.name),
                res_model="sh.helpdesk.ticket",
                res_id=t.id,
                partner_id=t.partner_id.id if t.partner_id else False,
            )

    def action_approve_close(self):
        for t in self:
            t.rounak_close_approved = True
            self.env["rounak.audit.log"].log(
                "approval",
                _("Close approved for license ticket %s", t.name),
                res_model="sh.helpdesk.ticket",
                res_id=t.id,
                partner_id=t.partner_id.id if t.partner_id else False,
            )
