from odoo import models, fields

class Student(models.Model):
    _name = "university.student"
    _description = "Student"

    name = fields.Char(string="Name", required=True)
    # Campo clave para el Ejercicio 8: Conecta al estudiante con el usuario del portal
    partner_id = fields.Many2one("res.partner", string="Related Contact", help="The contact associated with this student for website portal access.")
    
    email = fields.Char(string="Email")
    image_1920 = fields.Image(string="Image")

    university_id = fields.Many2one("university.university", string="University", required=True)
    tutor_id = fields.Many2one("university.professor", string="Tutor")

    # Dirección
    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    state_id = fields.Many2one("res.country.state", string="State")
    zip = fields.Char(string="ZIP")
    country_id = fields.Many2one("res.country", string="Country")

    # Relaciones para historial
    enrollment_ids = fields.One2many("university.enrollment", "student_id", string="Enrollments")
    grade_ids = fields.One2many("university.grade", "student_id", string="Grades")

    # Campos computados para Smart Buttons
    enrollment_count = fields.Integer(string="Enrollments Count", compute="_compute_enrollment_count")
    grade_count = fields.Integer(string="Grades Count", compute="_compute_grade_count")

    def _compute_enrollment_count(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)

    def _compute_grade_count(self):
        for record in self:
            record.grade_count = len(record.grade_ids)

    # ACCIÓN EJERCICIO 6: Enviar reporte por Email
    def action_send_report_email(self):
        self.ensure_one()
        template_id = self.env.ref('university.email_template_student_report').id
        ctx = {
            'default_model': 'university.student',
            'default_res_ids': self.ids,
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    # Acciones para Smart Buttons
    def action_view_enrollments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window", 
            "name": "Enrollments", 
            "res_model": "university.enrollment", 
            "view_mode": "list,form", 
            "domain": [("student_id", "=", self.id)], 
            "context": {"default_student_id": self.id}
        }

    def action_view_grades(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window", 
            "name": "Grades", 
            "res_model": "university.grade", 
            "view_mode": "list,form", 
            "domain": [("student_id", "=", self.id)], 
            "context": {"default_student_id": self.id}
        }