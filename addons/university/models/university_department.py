from odoo import models, fields, api

class Department(models.Model):
    _name = "university.department"
    _description = "Department"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True, tracking=True)
    color = fields.Integer(string="Color Index") 

    university_id = fields.Many2one(
        "university.university",
        string="University",
        required=True,
        tracking=True,
        ondelete='cascade',
    )

    manager_id = fields.Many2one(
        "university.professor",
        string="Department Manager",
        tracking=True,
        ondelete='set null', 
    )

    professor_ids = fields.One2many(
        "university.professor",
        "department_id",
        string="Professors",
    )

    professor_count = fields.Integer(
        string="Professors Count",
        compute="_compute_professor_count",
    )

    def _compute_professor_count(self):
        professor_data = self.env['university.professor'].read_group(
            [('department_id', 'in', self.ids)], 
            ['department_id'], 
            ['department_id']
        )
        mapped_data = {d['department_id'][0]: d['department_id_count'] for d in professor_data}
        for record in self:
            record.professor_count = mapped_data.get(record.id, 0)

    def action_view_professors(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Professors of {self.name}",
            "res_model": "university.professor",
            "view_mode": "list,kanban,form",
            "domain": [("department_id", "=", self.id)],
            "context": {"default_department_id": self.id},
            "target": "current",
        }