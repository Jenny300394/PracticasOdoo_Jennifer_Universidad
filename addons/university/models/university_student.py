from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Student(models.Model):
    _name = "university.student"
    _description = "Student"

    # --- CAMPOS PRINCIPALES ---
    name = fields.Char(string="Name", required=True)
    partner_id = fields.Many2one("res.partner", string="Related Contact")
    user_id = fields.Many2one("res.users", string="Related User", readonly=True)
    
    # Email obligatorio para diferenciar alumnos y para el Ejercicio 10
    email = fields.Char(string="Email", required=True)
    
    # Manejo de imágenes (Ejercicio 3)
    image_1920 = fields.Image(string="Image", max_width=1920, max_height=1920)
    image_128 = fields.Image(string="Image 128", related="image_1920", max_width=128, max_height=128, store=True)
    
    # Universidad (Ejercicio 1)
    university_id = fields.Many2one(
        "university.university", 
        string="University", 
        required=True,
        ondelete='cascade'
    )

    # --- LÓGICA DE HERENCIA DE UNIVERSIDAD (Para evitar errores de validación) ---
    @api.onchange('university_id')
    def _onchange_university_id(self):
        """Asigna la universidad del alumno a sus líneas de matrícula automáticamente"""
        for record in self:
            for enrollment in record.enrollment_ids:
                enrollment.university_id = record.university_id
    
    tutor_id = fields.Many2one(
        "university.professor", 
        string="Tutor",
        ondelete='set null'
    )

    # --- VALIDACIÓN PARA EVITAR DOBLE MATRÍCULA ---
    @api.constrains('email')
    def _check_unique_student_email(self):
        for record in self:
            if record.email:
                duplicate = self.sudo().search([
                    ('id', '!=', record.id),
                    ('email', '=', record.email)
                ], limit=1)
                
                if duplicate:
                    raise ValidationError(
                        f"El alumno con email '{record.email}' ya está matriculado en: "
                        f"{duplicate.university_id.name}. No puede estar en dos universidades."
                    )

    # --- DIRECCIÓN (Ejercicio 1) ---
    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    state_id = fields.Many2one("res.country.state", string="State")
    zip = fields.Char(string="ZIP")
    country_id = fields.Many2one("res.country", string="Country")
    
    # --- RELACIONES ---
    enrollment_ids = fields.One2many("university.enrollment", "student_id", string="Enrollments")
    grade_ids = fields.One2many("university.grade", "student_id", string="Grades")
    
    # --- CONTADORES (Ejercicio 2) ---
    enrollment_count = fields.Integer(compute="_compute_counts")
    grade_count = fields.Integer(compute="_compute_counts")
    subject_count = fields.Integer(compute="_compute_counts")
    professor_count = fields.Integer(compute="_compute_counts")

    @api.depends('enrollment_ids', 'grade_ids')
    def _compute_counts(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)
            record.grade_count = len(record.grade_ids)
            record.subject_count = len(record.enrollment_ids.mapped('subject_id'))
            record.professor_count = len(record.enrollment_ids.mapped('professor_id'))

    # --- ACCIONES DE SMART BUTTONS (Ejercicio 2) ---
    def action_view_enrollments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "university.enrollment",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
            "name": "Enrollments",
        }

    def action_view_grades(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "university.grade",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
            "name": "Grades",
        }

    def action_view_subjects(self):
        self.ensure_one()
        subject_ids = self.enrollment_ids.mapped('subject_id').ids
        return {
            "type": "ir.actions.act_window",
            "res_model": "university.subject",
            "view_mode": "list,form",
            "domain": [("id", "in", subject_ids)],
            "name": "Subjects",
        }

    def action_view_professors(self):
        self.ensure_one()
        professor_ids = self.enrollment_ids.mapped('professor_id').ids
        return {
            "type": "ir.actions.act_window",
            "res_model": "university.professor",
            "view_mode": "list,form",
            "domain": [("id", "in", professor_ids)],
            "name": "Professors",
        }

    # --- ENVÍO DE EMAIL (Ejercicio 6 y 10) ---
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

    # WIDGET JS (Ejercicio 10)
    def action_send_grades_summary_js(self):
        self.ensure_one()
        template = self.env.ref('university.email_template_student_report', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '¡Enviado!',
                    'message': 'El resumen de notas ha sido enviado correctamente.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        return True