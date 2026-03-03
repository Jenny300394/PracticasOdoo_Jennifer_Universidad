from odoo import models, fields, api

class Subject(models.Model):
    _name = "university.subject"
    _description = "Subject"

    name = fields.Char(string="Name", required=True)
    
    # ÚNICO SITIO CON CASCADE: La asignatura pertenece a la institución.
    university_id = fields.Many2one(
        "university.university", 
        string="University", 
        required=True,
        ondelete='cascade'
    )

    # RELACIONES (Aquí NO se toca el ondelete)
    professor_ids = fields.Many2many(
        "university.professor",
        "university_professor_subject_rel",
        "subject_id",
        "professor_id",
        string="Professors",
    )
    # One2many: Jamás poner ondelete aquí, es lo que rompe el sistema.
    enrollment_ids = fields.One2many("university.enrollment", "subject_id", string="Enrollments")

    # --- El resto de tu lógica de contadores y acciones se mantiene igual ---
    enrollment_count = fields.Integer(string="Enrollments", compute="_compute_counts")
    student_count = fields.Integer(string="Students", compute="_compute_counts")
    professor_count = fields.Integer(string="Professors Count", compute="_compute_counts")

    @api.depends('enrollment_ids', 'professor_ids')
    def _compute_counts(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)
            record.student_count = len(record.enrollment_ids.mapped('student_id'))
            record.professor_count = len(record.professor_ids)

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

    def action_view_students(self):
        self.ensure_one()
        student_ids = self.enrollment_ids.mapped('student_id').ids
        return {
            "type": "ir.actions.act_window",
            "name": "Students",
            "res_model": "university.student",
            "view_mode": "list,kanban,form",
            "domain": [("id", "in", student_ids or [0])],
        }

    def action_view_professors(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Professors",
            "res_model": "university.professor",
            "view_mode": "list,form",
            "domain": [("id", "in", self.professor_ids.ids or [0])],
        }