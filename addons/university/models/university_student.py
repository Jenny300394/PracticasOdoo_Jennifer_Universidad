from odoo import models, fields, api

class Student(models.Model):
    _name = "university.student"
    _description = "Student"

    # --- Campos principales ---
    name = fields.Char(string="Name", required=True)
    partner_id = fields.Many2one("res.partner", string="Related Contact")
    user_id = fields.Many2one("res.users", string="Related User", readonly=True)
    email = fields.Char(string="Email")
    image_1920 = fields.Image(string="Image")
    university_id = fields.Many2one("university.university", string="University", required=True)
    tutor_id = fields.Many2one("university.professor", string="Tutor")

    # --- Dirección ---
    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    state_id = fields.Many2one("res.country.state", string="State")
    zip = fields.Char(string="ZIP")
    country_id = fields.Many2one("res.country", string="Country")
    
    # --- Relaciones ---
    enrollment_ids = fields.One2many("university.enrollment", "student_id", string="Enrollments")
    grade_ids = fields.One2many("university.grade", "student_id", string="Grades")
    
    # --- Contadores para Smart Buttons ---
    enrollment_count = fields.Integer(compute="_compute_counts")
    grade_count = fields.Integer(compute="_compute_counts")
    subject_count = fields.Integer(compute="_compute_counts")
    professor_count = fields.Integer(compute="_compute_counts")

    def _compute_counts(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)
            record.grade_count = len(record.grade_ids)
            record.subject_count = len(record.enrollment_ids.mapped('subject_id'))
            record.professor_count = len(record.enrollment_ids.mapped('professor_id'))

    # --- Acciones de los Smart Buttons ---
    def action_view_enrollments(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "university.enrollment",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
            "name": "Enrollments",
        }

    def action_view_grades(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "university.grade",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
            "name": "Grades",
        }

    def action_view_subjects(self):
        subject_ids = self.enrollment_ids.mapped('subject_id').ids
        return {
            "type": "ir.actions.act_window",
            "res_model": "university.subject",
            "view_mode": "list,form",
            "domain": [("id", "in", subject_ids)],
            "name": "Subjects",
        }

    def action_view_professors(self):
        professor_ids = self.enrollment_ids.mapped('professor_id').ids
        return {
            "type": "ir.actions.act_window",
            "res_model": "university.professor",
            "view_mode": "list,form",
            "domain": [("id", "in", professor_ids)],
            "name": "Professors",
        }

    # --- Acción para enviar reporte por email (Wizard) ---
    def action_send_report_email(self):
        self.ensure_one()
        template = self.env.ref('university.email_template_student_report', raise_if_not_found=False)
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': {
                'default_model': 'university.student', 
                'default_res_ids': self.ids, 
                'default_template_id': template.id if template else False
            }
        }

    # --- LA FUNCIÓN QUE FALTABA ---
    def action_send_grades_summary_js(self):
        """ Envía el correo directamente sin abrir ventana """
        self.ensure_one()
        template = self.env.ref('university.email_template_student_report', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        return True