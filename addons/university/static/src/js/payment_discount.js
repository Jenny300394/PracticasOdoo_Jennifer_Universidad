/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.PaymentDiscount = publicWidget.Widget.extend({
    selector: '#payment_method', // Cambiamos el selector a uno más específico del área de pagos
    events: {
        'change input[name="o_payment_radio"]': '_onPaymentMethodClick',
    },

    async _onPaymentMethodClick(ev) {
        const input = ev.currentTarget;
        
        // Intentamos obtener el ID del proveedor
        let providerId = input.dataset.providerId || input.value;

        // Si el valor es "on" o no es un número, buscamos en el contenedor padre
        if (!providerId || isNaN(parseInt(providerId))) {
            const container = input.closest('div');
            providerId = container ? container.dataset.providerId : null;
        }

        if (!providerId || isNaN(parseInt(providerId))) {
            return; 
        }

        console.log("Aplicando descuento para Provider ID:", providerId);

        try {
            const result = await rpc('/shop/payment/update_discount', {
                provider_id: parseInt(providerId),
            });

            if (result && result.status === 'success') {
                // Solo recargamos si el servidor confirma el cambio
                // Esto evita el bucle de "conexión perdida"
                window.location.reload();
            }
        } catch (error) {
            console.error("Error en RPC de descuentos:", error);
        }
    },
});