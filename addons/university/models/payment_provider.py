from odoo import models, fields

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    # Campo para elegir el producto que se añadirá al carrito como descuento
    discount_product_id = fields.Many2one(
        'product.product', 
        string="Producto de Descuento",
        domain="[('sale_ok', '=', True), ('type', '=', 'service')]",
        help="Selecciona el producto que se usará para aplicar el descuento en la línea de pedido."
    )
    
    # Selección de la lógica de cálculo
    discount_type = fields.Selection([
        ('fixed', 'Importe Fijo'),
        ('percent', 'Importe Porcentual')
    ], string="Tipo de Descuento", default='percent', required=True)

    # Campos de valor
    discount_fixed_amount = fields.Float(
        string="Importe Fijo (€)", 
        help="Cantidad exacta a descontar (ej. 5.0)"
    )
    discount_percent_amount = fields.Float(
        string="Descuento (%)", 
        help="Porcentaje a descontar sobre el total (ej. 10.0)"
    )