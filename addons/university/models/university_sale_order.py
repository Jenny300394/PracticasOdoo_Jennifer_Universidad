from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # REQUERIMIENTO EJERCICIO 12: Campo de notas que viajará al albarán
    x_notes = fields.Text(string="Notas del Ejercicio 12")

    def _update_payment_discount(self, provider_id):
        self.ensure_one()
        # 1. Buscamos el proveedor
        provider = self.env['payment.provider'].sudo().browse(int(provider_id))
        
        # 2. Borramos descuentos anteriores para que no se acumulen
        if provider.discount_product_id:
            self.order_line.filtered(
                lambda l: l.product_id.id == provider.discount_product_id.id
            ).sudo().unlink()

        # 3. Validaciones básicas
        if not provider.exists() or not provider.discount_product_id:
            return

        # 4. LÓGICA DEL EJERCICIO: Cálculo según el tipo de descuento
        amount = 0.0
        if provider.discount_type == 'fixed':
            amount = -provider.discount_fixed_amount
        elif provider.discount_type == 'percent':
            # Calculado sobre el total sin IVA (amount_untaxed)
            amount = -(self.amount_untaxed * (provider.discount_percent_amount / 100.0))

        # 5. Creamos la línea de descuento
        if amount != 0:
            self.env['sale.order.line'].sudo().create({
                'order_id': self.id,
                'product_id': provider.discount_product_id.id,
                'name': f"Descuento: {provider.name}",
                'product_uom_qty': 1,
                'price_unit': amount,
                'sequence': 999,
            })
            
            # 6. Recalcular totales
            self.sudo()._amount_all()