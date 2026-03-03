from odoo import models, fields, api

class Enrollment(models.Model):
    _name = "university.enrollment"
    _description = "Enrollment"
    _order = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Enrollment Code", readonly=True, copy=False, tracking=True)

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
    
    professor_id = fields.Many2one(
        "university.professor", 
        string="Professor", 
        required=False, 
        tracking=True,
        ondelete='set null' 
    )
    
    subject_id = fields.Many2one(
        "university.subject", 
        string="Subject", 
        required=True,
        ondelete='restrict' 
    )
    
    grade_ids = fields.One2many("university.grade", "enrollment_id", string="Grades")

    grade_count = fields.Integer(compute='_compute_grade_count')

    def _compute_grade_count(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids) 

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