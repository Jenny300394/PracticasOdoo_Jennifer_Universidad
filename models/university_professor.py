from odoo import models, fields

class Professor(models.Model):
    _name = "university.professor"
    _description = "Professor"

    name = fields.Char(string="Name", required=True)
    image_1920 = fields.Image(string="Image")

    university_id = fields.Many2one(
        "university.university",
        string="University",
        required=True,
    )

    department_id = fields.Many2one(
        "university.department",
        string="Department",
    )

    department_ids = fields.Many2many(
        "university.department",
        "university_professor_department_rel",
        "professor_id",
        "department_id",
        string="Departments",
    )

    subject_ids = fields.Many2many(
        "university.subject",
        "university_professor_subject_rel",
        "professor_id",
        "subject_id",
        string="Subjects",
    )

    enrollment_ids = fields.One2many(
        "university.enrollment",
        "professor_id",
        string="Enrollments",
    )

    enrollment_count = fields.Integer(
        string="Enrollments Count",
        compute="_compute_enrollment_count",
    )

    def _compute_enrollment_count(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)

    # SMARTBUTTON 
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
