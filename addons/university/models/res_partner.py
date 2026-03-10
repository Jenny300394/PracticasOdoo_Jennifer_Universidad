from odoo import models, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, vals):
        # 1. Identificamos el ID del contacto de la empresa (EL ÚNICO QUE QUEREMOS PROTEGER)
        company_partner_id = self.env.company.partner_id.id
        
        # 2. Revisamos los contactos que estamos intentando guardar (self)
        for record in self:
            # SI EL CONTACTO ES EL DE LA EMPRESA...
            if record.id == company_partner_id:
                # ...Y EL USUARIO NO ES DE "AJUSTES" (base.group_system)
                if not self.env.user.has_group('base.group_system'):
                    raise UserError(_(
                        "Seguridad Ejercicio 13: El contacto de la compañía principal "
                        "solo puede ser editado por usuarios con permiso de 'Ajustes'."
                    ))
        
        # 3. Si no es el de la empresa, o si tiene permiso, Odoo sigue normal
        return super(ResPartner, self).write(vals)