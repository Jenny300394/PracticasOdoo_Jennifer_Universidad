from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Student(models.Model):
    _name = "university.student"
    _description = "Student"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # --- Campos principales ---
    name = fields.Char(string="Name", required=True, tracking=True)
    partner_id = fields.Many2one("res.partner", string="Related Contact", ondelete='restrict')
    user_id = fields.Many2one("res.users", string="Related User", readonly=True)
    
    email = fields.Char(string="Email", tracking=True)
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
    
    enrollment_count = fields.Integer(string="Enrollments Count", compute="_compute_enrollment_count")
    grade_count = fields.Integer(string="Grades Count", compute="_compute_grade_count")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # 1. Asegurar el Partner
            if not vals.get('partner_id'):
                partner = self.env['res.partner'].sudo().create({
                    'name': vals.get('name'),
                    'email': vals.get('email'),
                })
                vals['partner_id'] = partner.id
            else:
                partner = self.env['res.partner'].sudo().browse(vals['partner_id'])

            # 2. Gestionar el Usuario
            login = vals.get('email') or vals.get('name').replace(" ", ".").lower()
            user = self.env['res.users'].sudo().search([('login', '=', login)], limit=1)
            
            if not user:
                # Solo usamos el wizard si el partner NO tiene usuario todavía
                # Esto evita el error de "Already has portal access"
                wizard = self.env['portal.wizard'].sudo().create({
                    'partner_ids': [(4, partner.id)]
                })
                # El wizard crea el usuario y le asigna el grupo portal automáticamente
                wizard.user_ids.action_grant_access()
                
                # Buscamos el usuario recién creado para guardarlo en el estudiante
                user = self.env['res.users'].sudo().search([('partner_id', '=', partner.id)], limit=1)
            
            if user:
                vals['user_id'] = user.id
            
        return super(Student, self).create(vals_list)

    # --- Resto de métodos (Computados y Acciones) ---
    @api.depends('enrollment_ids')
    def _compute_enrollment_count(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)

    @api.depends('grade_ids')
    def _compute_grade_count(self):
        for record in self:
            record.grade_count = len(record.grade_ids)

    def action_view_enrollments(self):
        self.ensure_one()
        return {
            "name": "Inscripciones",
            "type": "ir.actions.act_window", 
            "res_model": "university.enrollment", 
            "view_mode": "list,form", 
            "domain": [("student_id", "=", self.id)],
            "context": {'default_student_id': self.id}
        }

    def action_view_grades(self):
        self.ensure_one()
        return {
            "name": "Calificaciones",
            "type": "ir.actions.act_window", 
            "res_model": "university.grade", 
            "view_mode": "list,form", 
            "domain": [("student_id", "=", self.id)],
            "context": {'default_student_id': self.id}
        }

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
                'default_template_id': template.id if template else False,
            }
        }