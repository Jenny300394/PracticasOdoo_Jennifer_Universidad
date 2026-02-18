from odoo import models, fields

class Subject(models.Model):
    _name = "university.subject"
    _description = "Subject"

    name = fields.Char(string="Name", required=True)

    university_id = fields.Many2one(
        "university.university",
        string="University",
        required=True,
    )

    professor_ids = fields.Many2many(
        "university.professor",
        "university_professor_subject_rel",
        "subject_id",
        "professor_id",
        string="Professors",
    )

    enrollment_ids = fields.One2many(
        "university.enrollment",
        "subject_id",
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
            "domain": [("subject_id", "=", self.id)],
            "context": {"default_subject_id": self.id},
        }
