from odoo import models, fields

class Student(models.Model):
    _name = "university.student"
    _description = "Student"

    name = fields.Char(string="Name", required=True)
    image_1920 = fields.Image(string="Image")

    university_id = fields.Many2one(
        "university.university",
        string="University",
        required=True,
    )

    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    state_id = fields.Many2one("res.country.state", string="State")
    zip = fields.Char(string="ZIP")
    country_id = fields.Many2one("res.country", string="Country")

    tutor_id = fields.Many2one(
        "university.professor",
        string="Tutor",
    )

    enrollment_ids = fields.One2many(
        "university.enrollment",
        "student_id",
        string="Enrollments",
    )

    grade_ids = fields.One2many(
        "university.grade",
        "student_id",
        string="Grades",
    )

    enrollment_count = fields.Integer(
        string="Enrollments",
        compute="_compute_enrollment_count"
    )

    grade_count = fields.Integer(
        string="Grades",
        compute="_compute_grade_count"
    )

    def _compute_enrollment_count(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)

    def _compute_grade_count(self):
        for record in self:
            record.grade_count = len(record.grade_ids)

    # SMARTBUTTON 
    def action_view_enrollments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Enrollments",
            "res_model": "university.enrollment",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
            "context": {"default_student_id": self.id},
        }

    def action_view_grades(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Grades",
            "res_model": "university.grade",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
            "context": {"default_student_id": self.id},
        }
