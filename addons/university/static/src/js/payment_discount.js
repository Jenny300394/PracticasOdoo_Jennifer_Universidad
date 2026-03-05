/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PaymentDiscount = publicWidget.Widget.extend({
    selector: '#payment_method', 
    events: {
        'click input[name="o_payment_radio"]': '_onPaymentMethodClick',
    },

    _onPaymentMethodClick: function (ev) {
        const providerId = $(ev.currentTarget).data('provider-id') || $(ev.currentTarget).val();
        
        console.log("¡CLICK DETECTADO! Enviando ID:", providerId); 

        // En lugar de usar rpc service, usamos el fetch nativo que nunca falla
        // Enviamos la petición al controlador de Python que ya creamos
        fetch('/shop/payment/update_discount', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                params: {
                    provider_id: providerId,
                }
            }),
        }).then(response => {
            if (response.ok) {
                console.log("Python ejecutado con éxito, recargando...");
                window.location.reload();
            }
        }).catch(error => {
            console.error("Error en la conexión:", error);
        });
    },
});