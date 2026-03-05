from odoo import models, fields

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    # Campo para elegir el producto "Descuento por pago"
    discount_product_id = fields.Many2one(
        'product.product', 
        string="Producto de Descuento",
        domain="[('sale_ok', '=', True)]"
    )
    
    # Desplegable para elegir si es Fijo (5€) o Porcentaje (10%)
    discount_type = fields.Selection([
        ('fixed', 'Importe Fijo'),
        ('percent', 'Importe Porcentual')
    ], string="Tipo de Descuento", default='percent')

    # Los cuadritos para escribir el número
    discount_fixed_amount = fields.Float(string="Importe Fijo (Euros)")
    discount_percent_amount = fields.Float(string="Importe Porcentual (%)")