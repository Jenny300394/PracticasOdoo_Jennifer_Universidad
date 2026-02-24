/** @odoo-module **/

console.log("SISTEMA CARGADO");

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    async actionClicked(params) {
        const result = await super.actionClicked(...arguments);
        if (params && params.name === 'action_send_grades_summary_js') {
            this.env.services.notification.add("¡Send email!", {
                type: "success",
            });
        }
        return result;
    },
});