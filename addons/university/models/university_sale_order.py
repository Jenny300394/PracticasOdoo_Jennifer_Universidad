from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Actividad 12: Campo en Pedido de Venta
    x_notes = fields.Text(string="Notas del Ejercicio 12")

    # ESTA ES LA CLAVE: Sincroniza el cambio hacia el Albarán si lo modificas después
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'x_notes' in vals:
            for order in self:
                # Si el pedido ya tiene albaranes, les actualizamos la nota también
                if order.picking_ids:
                    order.picking_ids.write({'x_notes': vals['x_notes']})
        return res

    def _update_payment_discount(self, provider_id):
        self = self.sudo()
        self.ensure_one()
        if not provider_id:
            return False

        try:
            provider = self.env['payment.provider'].browse(int(provider_id))
            discount_product = provider.discount_product_id
            
            # 1. LIMPIEZA
            self.order_line.filtered(lambda l: l.product_id.id == discount_product.id or l.price_unit < 0).unlink()

            if not discount_product:
                return True

            # 2. CÁLCULO
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
            
            return True
        except Exception as e:
            _logger.error(str(e))
            return False

    # Asegura que al confirmar por primera vez, se lleve la nota que haya
    def _prepare_picking(self):
        res = super(SaleOrder, self)._prepare_picking()
        res['x_notes'] = self.x_notes
        return res

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    x_notes = fields.Text(string="Notas del Ejercicio 12")