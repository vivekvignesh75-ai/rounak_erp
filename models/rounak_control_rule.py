# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RounakControlRule(models.Model):
    _name = "rounak.control.rule"
    _description = "Rounak Control Rule"
    _order = "category, sequence"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    category = fields.Selection(
        [
            ("credit", "Credit Limit"),
            ("discount", "Discount Approval"),
            ("block", "Transaction Block"),
            ("payment", "Payment Terms"),
        ],
        required=True,
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    value_float = fields.Float(help="Numeric threshold value")
    value_char = fields.Char(help="Text value or configuration string")
    description = fields.Text()

    _sql_constraints = [
        ("code_uniq", "unique(code)", "Control rule code must be unique."),
    ]

    @api.model
    def get_value(self, code, default=None):
        rule = self.search([("code", "=", code), ("active", "=", True)], limit=1)
        if not rule:
            return default
        return rule.value_float or rule.value_char or default

    @api.model
    def get_float(self, code, default=0.0):
        rule = self.search([("code", "=", code), ("active", "=", True)], limit=1)
        return rule.value_float if rule else default
