from odoo import models, fields, api

class Professor(models.Model):
    _name = "university.professor"
    _description = "Professor"

    name = fields.Char(string="Name", required=True)
    
    # Imagen dual: esto es lo que evita que desaparezca
    image_1920 = fields.Image(string="Image", max_width=1920, max_height=1920)
    image_128 = fields.Image(string="Image 128", related="image_1920", max_width=128, max_height=128, store=True)

    university_id = fields.Many2one("university.university", string="University", required=True)
    department_id = fields.Many2one("university.department", string="Department")
    
    department_ids = fields.Many2many(
        "university.department", "university_professor_department_rel", 
        "professor_id", "department_id", string="Departments"
    )
    
    subject_ids = fields.Many2many(
        "university.subject", "university_professor_subject_rel", 
        "professor_id", "subject_id", string="Subjects"
    )
    
    enrollment_ids = fields.One2many("university.enrollment", "professor_id", string="Enrollments")

    # Los 3 contadores que usa tu XML
    enrollment_count = fields.Integer(compute="_compute_counts")
    subject_count = fields.Integer(compute="_compute_counts")
    student_count = fields.Integer(compute="_compute_counts")

    @api.depends('enrollment_ids', 'subject_ids')
    def _compute_counts(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)
            record.subject_count = len(record.subject_ids)
            # Buscamos estudiantes únicos vinculados a sus matrículas
            record.student_count = len(record.enrollment_ids.mapped('student_id'))

    # Las 3 funciones de los botones
    def action_view_enrollments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Enrollments",
            "res_model": "university.enrollment",
            "view_mode": "list,form",
            "domain": [("professor_id", "=", self.id)],
            "context": {"default_professor_id": self.id},
        }

    def action_view_subjects(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Subjects",
            "res_model": "university.subject",
            "view_mode": "list,form",
            "domain": [("id", "in", self.subject_ids.ids)],
        }

    def action_view_students(self):
        self.ensure_one()
        student_ids = self.enrollment_ids.mapped('student_id').ids
        return {
            "type": "ir.actions.act_window",
            "name": "Students",
            "res_model": "university.student",
            "view_mode": "list,form",
            "domain": [("id", "in", student_ids)],
        }