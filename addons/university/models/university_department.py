from odoo import models, fields

class Department(models.Model):
    _name = "university.department"
    _description = "Department"

    name = fields.Char(string="Name", required=True)

    university_id = fields.Many2one(
        "university.university",
        string="University",
        required=True,
    )

    manager_id = fields.Many2one(
        "university.professor",
        string="Department Manager",
    )

    professor_ids = fields.One2many(
        "university.professor",
        "department_id",
        string="Professors",
    )

    # SMARTBUTTON 
    professor_count = fields.Integer(
        string="Professors Count",
        compute="_compute_professor_count",
    )

    def _compute_professor_count(self):
        for record in self:
            record.professor_count = len(record.professor_ids)

    # SMARTBUTTON 
    def action_view_professors(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Professors",
            "res_model": "university.professor",
            "view_mode": "list,kanban,form",
            "domain": [("department_id", "=", self.id)],
            "context": {"default_department_id": self.id},
        }
