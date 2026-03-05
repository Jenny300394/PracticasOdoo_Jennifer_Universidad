from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _update_payment_discount(self, provider_id):
        self.ensure_one()
        # 1. Buscamos el proveedor usando los campos que definiste
        provider = self.env['payment.provider'].sudo().browse(int(provider_id))
        
        # 2. Borramos descuentos anteriores para que no se acumulen
        # (Buscamos por el producto que tiene el proveedor configurado)
        if provider.discount_product_id:
            self.order_line.filtered(
                lambda l: l.product_id.id == provider.discount_product_id.id
            ).sudo().unlink()

        # 3. Si el proveedor no existe o no tiene producto, no hacemos nada
        if not provider.exists() or not provider.discount_product_id:
            return

        # 4. LÓGICA DEL EJERCICIO: Cálculo según tus campos
        amount = 0.0
        if provider.discount_type == 'fixed':
            # Si elegiste "Importe Fijo"
            amount = -provider.discount_fixed_amount
        elif provider.discount_type == 'percent':
            # Si elegiste "Importe Porcentual" (calculado sobre el total sin IVA)
            amount = -(self.amount_untaxed * (provider.discount_percent_amount / 100.0))

        # 5. Si el importe es distinto de cero, creamos la línea
        if amount != 0:
            self.env['sale.order.line'].sudo().create({
                'order_id': self.id,
                'product_id': provider.discount_product_id.id,
                'name': f"Descuento: {provider.name}",
                'product_uom_qty': 1,
                'price_unit': amount,
                'sequence': 999, # Para que salga abajo en el carrito
            })
            
            # 6. Recalcular totales para que la web vea el cambio
            self.sudo()._amount_all()