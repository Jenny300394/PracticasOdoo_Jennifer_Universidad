from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Student(models.Model):
    _name = "university.student"
    _description = "Student"

    # Campos básicos del alumno
    name = fields.Char(string="Name", required=True)
    partner_id = fields.Many2one("res.partner", string="Related Contact")
    user_id = fields.Many2one("res.users", string="Related User")
    
    # Ponemos el email obligatorio para que no haya fallos al enviar los informes
    email = fields.Char(string="Email", required=True)
    
    # Las fotos del alumno, una grande y la otra pequeñita que se rellena sola
    image_1920 = fields.Image(string="Image", max_width=1920, max_height=1920)
    image_128 = fields.Image(string="Image 128", related="image_1920", max_width=128, max_height=128, store=True)
    
    # A qué universidad pertenece (si se borra la universidad, se borra el alumno con cascade)
    university_id = fields.Many2one(
        "university.university", 
        string="University", 
        required=True,
        ondelete='cascade'
    )

    # --- Crear el usuario portal automáticamente ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('email') and not vals.get('user_id'):
                # 1. Creamos el usuario 
                new_user = self.env['res.users'].sudo().create({
                    'name': vals.get('name'),
                    'login': vals.get('email'),
                    'email': vals.get('email'),
                })
                
                # 2. Asignamos el grupo (CON ESCUDO DE SEGURIDAD)
                portal_group = self.env.ref('base.group_portal', raise_if_not_found=False)
                if portal_group:
                    try:
                        # Intentamos asignar el grupo. Si Odoo da el error de "Invalid Field", 
                        # lo ignoramos para que el proceso no se detenga.
                        new_user.sudo().write({'groups_id': [(4, portal_group.id)]})
                    except Exception:
                        pass
                
                # 3. Asignamos los IDs al alumno
                vals['user_id'] = new_user.id
                vals['partner_id'] = new_user.partner_id.id
                
        return super(Student, self).create(vals_list)

    # Si cambiamos la universidad del alumno, se la cambiamos también a sus matrículas automáticamente
    @api.onchange('university_id')
    def _onchange_university_id(self):
        for record in self:
            for enrollment in record.enrollment_ids:
                enrollment.university_id = record.university_id
    
    tutor_id = fields.Many2one(
        "university.professor", 
        string="Tutor",
        ondelete='set null'
    )

    # Validación para que un alumno no use un email que ya existe en otra universidad
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

    # Campos para la dirección del alumno
    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    state_id = fields.Many2one("res.country.state", string="State")
    zip = fields.Char(string="ZIP")
    country_id = fields.Many2one("res.country", string="Country")
    
    # Relaciones One2many para ver sus matrículas y sus notas
    enrollment_ids = fields.One2many("university.enrollment", "student_id", string="Enrollments")
    grade_ids = fields.One2many("university.grade", "student_id", string="Grades")
    
    # Campos que calculan los números que salen en los botones de arriba
    enrollment_count = fields.Integer(compute="_compute_counts")
    grade_count = fields.Integer(compute="_compute_counts")
    subject_count = fields.Integer(compute="_compute_counts")
    professor_count = fields.Integer(compute="_compute_counts")

    # Función para contar todo: usamos mapped para no repetir profesores ni asignaturas
    @api.depends('enrollment_ids', 'grade_ids')
    def _compute_counts(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)
            record.grade_count = len(record.grade_ids)
            record.subject_count = len(record.enrollment_ids.mapped('subject_id'))
            record.professor_count = len(record.enrollment_ids.mapped('professor_id'))

    # Acción para abrir la lista de matrículas de este alumno
    def action_view_enrollments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "university.enrollment",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
            "name": "Enrollments",
        }

    # Acción para abrir sus notas
    def action_view_grades(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "university.grade",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
            "name": "Grades",
        }

    # Acción para ver las asignaturas donde está apuntado
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

    # Acción para ver sus profesores
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

    # Esta función abre la ventana para enviar el informe por email
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

    # Envío rápido con notificación de éxito (usando JS de Odoo)
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