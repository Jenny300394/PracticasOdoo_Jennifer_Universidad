/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { _t } from "@web/core/l10n/translation";

patch(FormController.prototype, {
    async _onButtonClicked(params) {
        const result = await super._onButtonClicked(...arguments);
        if (params.name === 'action_send_grades_summary_js') {
            this.env.services.notification.add(
                _t("Email has been sent successfully."),
                {
                    title: _t("Success"),
                    type: "success",
                    sticky: false,
                }
            );
        }
        return result;
    }
});