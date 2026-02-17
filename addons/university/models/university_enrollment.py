from odoo import models, fields, api

class Enrollment(models.Model):
    _name = "university.enrollment"
    _description = "Enrollment"
    _order = "name"

    name = fields.Char(
        string="Enrollment Code",
        readonly=True,
        copy=False
    )

    student_id = fields.Many2one(
        "university.student",
        string="Student",
        required=True,
    )

    university_id = fields.Many2one(
        "university.university",
        string="University",
        required=True,
    )

    professor_id = fields.Many2one(
        "university.professor",
        string="Professor",
        required=True,
    )

    subject_id = fields.Many2one(
        "university.subject",
        string="Subject",
        required=True,
    )

    grade_ids = fields.One2many(
        "university.grade",
        "enrollment_id",
        string="Grades",
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)

        subject = record.subject_id
        year = fields.Date.today().year
        prefix = subject.name[:3].upper()

        count = self.search_count([
            ("subject_id", "=", subject.id),
            ("name", "like", f"{prefix}/{year}/")
        ]) + 1
        
        record.name = f"{prefix}/{year}/{count:04d}"

        return record
