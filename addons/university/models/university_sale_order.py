from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Actividad 12
    x_notes = fields.Text(string="Notas del Ejercicio 12")

    def _update_payment_discount(self, provider_id):
        self = self.sudo()
        self.ensure_one()
        
        if not provider_id:
            return False

        try:
            provider = self.env['payment.provider'].browse(int(provider_id))
            if not provider.exists():
                return False

            discount_product = provider.discount_product_id
            
            # 1. LIMPIEZA ANTIDUPLICADOS (Por Producto)
            # Buscamos cualquier línea que use el producto de descuento, sea cual sea su precio
            if discount_product:
                lines_to_remove = self.order_line.filtered(lambda l: l.product_id.id == discount_product.id)
                if lines_to_remove:
                    lines_to_remove.unlink()
            
            # También limpiamos por si hay líneas negativas de otros intentos
            old_negative_lines = self.order_line.filtered(lambda l: l.price_unit < 0)
            if old_negative_lines:
                old_negative_lines.unlink()

            if not discount_product:
                _logger.warning("El proveedor no tiene configurado un producto de descuento.")
                return True

            # 2. CÁLCULO ROBUSTO
            # Si amount_untaxed es 0.0 (error común de sesión), sumamos las líneas actuales
            base_calculo = self.amount_untaxed
            if base_calculo <= 0:
                base_calculo = sum(line.price_subtotal for line in self.order_line)

            amount = 0.0
            if provider.discount_type == 'fixed':
                amount = -abs(provider.discount_fixed_amount)
            else:
                percent = provider.discount_percent_amount or 0.0
                amount = -(base_calculo * (percent / 100.0))

            # 3. CREACIÓN DE LÍNEA
            if amount != 0:
                self.env['sale.order.line'].create({
                    'order_id': self.id,
                    'product_id': discount_product.id,
                    'name': f"Descuento por pago: {provider.name}",
                    'product_uom_qty': 1.0,
                    'price_unit': amount,
                    'sequence': 999,
                })
            
            # 4. ACTUALIZAR NOTAS (Actividad 12)
            self.write({
                'x_notes': f"Aplicado descuento de {abs(round(amount, 2))}€ usando {provider.name}"
            })
            
            # En Odoo 19, al hacer unlink() y create(), el sistema recalcula 
            # el total al final de la transacción automáticamente.
            return True

        except Exception as e:
            _logger.error("--- ERROR EN university_sale_order.py ---")
            _logger.error(str(e))
            return False