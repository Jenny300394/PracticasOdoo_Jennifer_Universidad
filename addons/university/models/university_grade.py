from odoo import models, fields, api

class Grade(models.Model):
    # Nombre técnico del modelo y cómo queremos que se vea en los listados
    _name = "university.grade"
    _description = "Grade"
    _rec_name = "display_name"

    # Relación con el alumno. Si se borra el alumno, su nota desaparece (cascade)
    student_id = fields.Many2one(
        "university.student", 
        string="Student", 
        required=True,
        ondelete='cascade'
    )
    
    # Relación con la matrícula específica. También desaparece si se borra la matrícula
    enrollment_id = fields.Many2one(
        "university.enrollment", 
        string="Enrollment", 
        required=True,
        ondelete='cascade'
    )
    
    # Esta función sirve para que no se mezclen matrículas de alumnos distintos
    @api.onchange('student_id')
    def _onchange_student_id(self):
        for record in self:
            if record.student_id:
                # Si el alumno no coincide con el de la matrícula, limpiamos el campo
                if record.enrollment_id and record.enrollment_id.student_id != record.student_id:
                    record.enrollment_id = False
            else:
                # Si no hay alumno, tampoco puede haber matrícula seleccionada
                record.enrollment_id = False

    # El campo de la nota numérica
    grade = fields.Float(string="Grade", required=True)
    
    # Nombre que se mostrará en el sistema (ej. "Jennifer - PRO/2026/0001")
    display_name = fields.Char(compute="_compute_display_name", store=True)

    # Aquí formamos el nombre combinando el alumno y su matrícula
    @api.depends('student_id.name', 'enrollment_id.name')
    def _compute_display_name(self):
        for record in self:
            s_name = record.student_id.name or 'Nuevo'
            e_name = record.enrollment_id.name or 'Sin Matrícula'
            record.display_name = f"{s_name} - {e_name}"

    # Botón inteligente para saltar rápidamente a ver la ficha de la matrícula
    def action_view_enrollment(self):
        self.ensure_one() # Esto asegura que solo estamos pinchando en un registro
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'university.enrollment',
            'view_mode': 'form',
            'res_id': self.enrollment_id.id,
            'target': 'current',
        }