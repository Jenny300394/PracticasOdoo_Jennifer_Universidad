from odoo import models, fields, api

class Grade(models.Model):
    _name = "university.grade"
    _description = "Grade"
    _rec_name = "display_name"

    # RELACIONES MANY2ONE CON CASCADE
    student_id = fields.Many2one(
        "university.student", 
        string="Student", 
        required=True,
        ondelete='cascade'
    )
    
    enrollment_id = fields.Many2one(
        "university.enrollment", 
        string="Enrollment", 
        required=True,
        ondelete='cascade'
    )
    
    # --- LOGICA DE LIMPIEZA AUTOMÁTICA ---
    @api.onchange('student_id')
    def _onchange_student_id(self):
        """
        Si el usuario cambia el estudiante, borramos la matrícula seleccionada 
        para que no se quede una matrícula que no le pertenece.
        """
        for record in self:
            if record.student_id:
                # Si la matrícula actual no es de este estudiante, la vaciamos
                if record.enrollment_id and record.enrollment_id.student_id != record.student_id:
                    record.enrollment_id = False
            else:
                record.enrollment_id = False

    grade = fields.Float(string="Grade", required=True)
    display_name = fields.Char(compute="_compute_display_name", store=True)

    @api.depends('student_id.name', 'enrollment_id.name')
    def _compute_display_name(self):
        for record in self:
            s_name = record.student_id.name or 'Nuevo'
            e_name = record.enrollment_id.name or 'Sin Matrícula'
            record.display_name = f"{s_name} - {e_name}"

    # --- SMART BUTTON ---
    def action_view_enrollment(self):
        self.ensure_one() # Buena práctica añadir esto en botones
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'university.enrollment',
            'view_mode': 'form',
            'res_id': self.enrollment_id.id,
            'target': 'current',
        }