/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

class RounakNotificationBell extends Component {
    static template = "rounak_erp.NotificationBell";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ count: 0, items: [], open: false });
        onWillStart(() => this.loadCount());
        this._pollInterval = setInterval(() => this.loadCount(), 60000);
    }

    async loadCount() {
        this.state.count = await this.orm.call(
            "rounak.notification", "get_unread_count", [],
        );
    }

    async toggleDropdown() {
        this.state.open = !this.state.open;
        if (this.state.open) {
            this.state.items = await this.orm.searchRead(
                "rounak.notification",
                [["user_id", "=", this.env.services.user.userId]],
                ["title", "body", "importance", "is_read", "create_date", "category"],
                { limit: 20, order: "create_date desc" },
            );
        }
    }

    async markAllRead() {
        await this.orm.call("rounak.notification", "mark_all_read", []);
        this.state.count = 0;
        for (const item of this.state.items) {
            item.is_read = true;
        }
    }

    async markRead(item) {
        if (!item.is_read) {
            await this.orm.call(
                "rounak.notification", "action_mark_read", [[item.id]],
            );
            item.is_read = true;
            this.state.count = Math.max(0, this.state.count - 1);
        }
    }

    openFullList() {
        this.state.open = false;
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Notifications",
            res_model: "rounak.notification",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [["user_id", "=", this.env.services.user.userId]],
            context: { search_default_unread: 1 },
        });
    }
}

registry.category("systray").add("rounak_erp.NotificationBell", {
    Component: RounakNotificationBell,
}, { sequence: 25 });
