from odoo import models, fields, api

class Subject(models.Model):
    _name = "university.subject"
    _description = "Subject"

    name = fields.Char(string="Name", required=True)
    university_id = fields.Many2one("university.university", string="University", required=True)

    # Relaciones
    professor_ids = fields.Many2many(
        "university.professor",
        "university_professor_subject_rel",
        "subject_id",
        "professor_id",
        string="Professors",
    )
    enrollment_ids = fields.One2many("university.enrollment", "subject_id", string="Enrollments")

    # Contadores para Smart Buttons
    enrollment_count = fields.Integer(string="Enrollments", compute="_compute_counts")
    student_count = fields.Integer(string="Students", compute="_compute_counts")
    professor_count = fields.Integer(string="Professors Count", compute="_compute_counts")

    @api.depends('enrollment_ids', 'professor_ids')
    def _compute_counts(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)
            # Alumnos únicos: usamos set() o mapped().ids para contar IDs reales
            record.student_count = len(record.enrollment_ids.mapped('student_id'))
            record.professor_count = len(record.professor_ids)

    # Acción del botón de matrículas
    def action_view_enrollments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Enrollments",
            "res_model": "university.enrollment",
            "view_mode": "list,form",
            "domain": [("subject_id", "=", self.id)],
            "context": {"default_subject_id": self.id},
        }

    # Acción del botón de alumnos
    def action_view_students(self):
        self.ensure_one()
        student_ids = self.enrollment_ids.mapped('student_id').ids
        return {
            "type": "ir.actions.act_window",
            "name": "Students",
            "res_model": "university.student",
            "view_mode": "list,kanban,form",
            # Filtramos por los IDs de estudiantes encontrados o pasamos 0 para lista vacía
            "domain": [("id", "in", student_ids or [0])],
        }

    # Acción del botón de profesores (Por si lo usas en el XML)
    def action_view_professors(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Professors",
            "res_model": "university.professor",
            "view_mode": "list,form",
            "domain": [("id", "in", self.professor_ids.ids or [0])],
        }