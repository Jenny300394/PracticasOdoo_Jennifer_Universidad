from odoo import models, fields, api

class Enrollment(models.Model):
    _name = "university.enrollment"
    _description = "Enrollment"
    _order = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Enrollment Code", readonly=True, copy=False, tracking=True)
    
    # Estos siguen siendo CASCADE porque si muere el alumno o la uni, la matrícula no tiene sentido.
    student_id = fields.Many2one(
        "university.student", 
        string="Student", 
        required=True, 
        ondelete='cascade'
    )
    university_id = fields.Many2one(
        "university.university", 
        string="University", 
        required=True, 
        ondelete='cascade'
    )
    
    # --- EL CAMBIO CLAVE ESTÁ AQUÍ ---
    # 1. Quitamos required=True para que Odoo permita dejarlo vacío.
    # 2. Ponemos ondelete='set null' para que la matrícula sobreviva al borrado del profesor.
    professor_id = fields.Many2one(
        "university.professor", 
        string="Professor", 
        required=False,  # <--- ESENCIAL: Si es True, Odoo no permite dejarlo vacío.
        tracking=True,
        ondelete='set null' # <--- Si borras al profe, el campo queda vacío pero la matrícula sigue viva.
    )
    
    subject_id = fields.Many2one(
        "university.subject", 
        string="Subject", 
        required=True,
        ondelete='restrict' # <--- Mejor 'restrict' para que no borren la materia si hay alumnos dentro.
    )
    
    grade_ids = fields.One2many("university.grade", "enrollment_id", string="Grades")

    # --- El resto del código se mantiene igual ---
    grade_count = fields.Integer(compute='_compute_grade_count')

    def _compute_grade_count(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids) # Corregido para que coincida con el campo

    def action_view_grades(self):
        return {
            'name': 'Calificaciones',
            'type': 'ir.actions.act_window',
            'res_model': 'university.grade',
            'view_mode': 'list,form',
            'domain': [('enrollment_id', '=', self.id)],
            'context': {'default_enrollment_id': self.id, 'default_student_id': self.student_id.id},
        }

    @api.model
    def create(self, vals):
        # Mantenemos tu lógica de secuencia...
        record = super().create(vals)
        subject = record.subject_id
        year = fields.Date.today().year
        prefix = subject.name[:3].upper() if subject.name else 'ENR'
        count = self.search_count([
            ("subject_id", "=", subject.id),
            ("name", "like", f"{prefix}/{year}/")
        ]) + 1
        record.name = f"{prefix}/{year}/{count:04d}"
        return record