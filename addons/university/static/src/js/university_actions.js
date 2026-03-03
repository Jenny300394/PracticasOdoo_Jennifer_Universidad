/** @odoo-module **/

// Este log sale en la consola del navegador para saber que el JS ha cargado bien
console.log("SISTEMA CARGADO");

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    async actionClicked(params) {
        // Primero dejamos que el botón haga su función normal en el servidor
        const result = await super.actionClicked(...arguments);
        
        // Si el botón que hemos pulsado es el de enviar notas...
        if (params && params.name === 'action_send_grades_summary_js') {
            // ...lanzamos un aviso verde de éxito en la esquina de la pantalla
            this.env.services.notification.add("¡Email enviado con éxito!", {
                type: "success",
            });
        }
        return result;
    },
});