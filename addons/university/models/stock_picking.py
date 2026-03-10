from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Definimos el campo para que el XML lo reconozca
    x_notes = fields.Text(string="Notas del Pedido")

class StockMove(models.Model):
    _inherit = 'stock.move'

    # Esta función hace la "magia" de copiar la nota de la Venta al Albarán
    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()
        if self.sale_line_id and self.sale_line_id.order_id:
            res['x_notes'] = self.sale_line_id.order_id.x_notes
        return res