/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

class RounakInternalDashboard extends Component {
    static template = "rounak_erp.InternalDashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            kpis: {},
            alerts: [],
            loading: true,
        });
        onWillStart(() => this.loadData());
    }

    async loadData() {
        const [
            pendingQuotes,
            openOrders,
            dueInvoices,
            overdueInvoices,
            openTickets,
            pendingApprovals,
            blockedPartners,
            recentAudit,
        ] = await Promise.all([
            this.orm.searchCount("sale.order", [["state", "in", ["draft", "sent"]]]),
            this.orm.searchCount("sale.order", [["state", "=", "sale"]]),
            this.orm.searchCount("account.move", [
                ["move_type", "=", "out_invoice"],
                ["state", "=", "posted"],
                ["payment_state", "not in", ["paid", "reversed"]],
            ]),
            this.orm.searchCount("account.move", [
                ["move_type", "=", "out_invoice"],
                ["state", "=", "posted"],
                ["payment_state", "not in", ["paid", "reversed"]],
                ["invoice_date_due", "<", new Date().toISOString().split("T")[0]],
            ]),
            this.orm.searchCount("sh.helpdesk.ticket", [
                ["stage_id.closed", "=", false],
            ]),
            this.orm.searchCount("discount.request", [
                ["state", "=", "pending"],
            ]).catch(() => 0),
            this.orm.searchCount("res.partner", [
                ["rounak_transaction_blocked", "=", true],
            ]),
            this.orm.searchRead(
                "rounak.audit.log",
                [],
                ["create_date", "action", "summary", "user_id"],
                { limit: 8, order: "create_date desc" },
            ),
        ]);

        this.state.kpis = {
            pendingQuotes,
            openOrders,
            dueInvoices,
            overdueInvoices,
            openTickets,
            pendingApprovals,
            blockedPartners,
        };

        this.state.alerts = [];
        if (overdueInvoices > 0)
            this.state.alerts.push({ type: "danger", text: `${overdueInvoices} overdue invoice(s)` });
        if (pendingApprovals > 0)
            this.state.alerts.push({ type: "warning", text: `${pendingApprovals} discount approval(s) pending` });
        if (blockedPartners > 0)
            this.state.alerts.push({ type: "danger", text: `${blockedPartners} partner(s) with blocked transactions` });
        if (pendingQuotes > 0)
            this.state.alerts.push({ type: "info", text: `${pendingQuotes} quotation(s) awaiting response` });

        this.state.recentAudit = recentAudit;
        this.state.loading = false;
    }

    openAction(model, domain, name) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: name,
            res_model: model,
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: domain,
        });
    }

    openOverdueInvoices() {
        this.openAction("account.move", [
            ["move_type", "=", "out_invoice"],
            ["state", "=", "posted"],
            ["payment_state", "not in", ["paid", "reversed"]],
            ["invoice_date_due", "<", new Date().toISOString().split("T")[0]],
        ], "Overdue Invoices");
    }

    openPendingQuotes() {
        this.openAction("sale.order", [
            ["state", "in", ["draft", "sent"]],
        ], "Pending Quotations");
    }

    openOpenTickets() {
        this.openAction("sh.helpdesk.ticket", [
            ["stage_id.closed", "=", false],
        ], "Open Tickets");
    }

    openBlockedPartners() {
        this.openAction("res.partner", [
            ["rounak_transaction_blocked", "=", true],
        ], "Blocked Partners");
    }
}

registry.category("actions").add("rounak_erp.internal_dashboard", RounakInternalDashboard);
