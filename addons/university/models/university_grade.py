from odoo import models, fields, api

class Grade(models.Model):
    _name = "university.grade"
    _description = "Grade"
    _rec_name = "display_name"

    student_id = fields.Many2one("university.student", string="Student", required=True)
    enrollment_id = fields.Many2one("university.enrollment", string="Enrollment", required=True)
    grade = fields.Float(string="Grade", required=True)
    display_name = fields.Char(compute="_compute_display_name")

    @api.depends('student_id', 'enrollment_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.student_id.name or ''} - {record.enrollment_id.name or ''}"

    # --- NUEVO PARA SMART BUTTON ---
    def action_view_enrollment(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'university.enrollment',
            'view_mode': 'form',
            'res_id': self.enrollment_id.id,
            'target': 'current',
        }
    # -------------------------------