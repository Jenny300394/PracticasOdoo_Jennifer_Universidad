/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.PaymentDiscount = publicWidget.Widget.extend({
    // Usamos wrapwrap para que el JS se cargue en todas las páginas sin dar error
    selector: '#wrapwrap', 
    events: {
        'change .o_payment_option_card input[name="o_payment_radio"]': '_onPaymentMethodClick',
    },

    _onPaymentMethodClick: function (ev) {
        // Obtenemos el ID del proveedor (Odoo 19 suele usar data-provider-id)
        const $input = $(ev.currentTarget);
        const providerId = $input.data('provider-id') || $input.val();
        
        if (!providerId) return;

        console.log("¡Método de pago detectado!", providerId);

        // Usamos jsonrpc que es la forma oficial de Odoo 19 (maneja tokens automáticamente)
        jsonrpc('/shop/payment/update_discount', {
            provider_id: parseInt(providerId),
        }).then((data) => {
            if (data.status === 'success') {
                console.log("Descuento aplicado, recargando...");
                window.location.reload();
            }
        }).catch((error) => {
            console.error("Error al actualizar descuento:", error);
        });
    },
});