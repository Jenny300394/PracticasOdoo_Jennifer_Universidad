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
    
    # --- Relaciones y Cuentas ---
    enrollment_ids = fields.One2many("university.enrollment", "student_id", string="Enrollments")
    grade_ids = fields.One2many("university.grade", "student_id", string="Grades")
    
    enrollment_count = fields.Integer(string="Enrollments Count", compute="_compute_enrollment_count")
    grade_count = fields.Integer(string="Grades Count", compute="_compute_grade_count")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # 1. Crear el Partner (Contacto)
            if not vals.get('partner_id'):
                partner = self.env['res.partner'].sudo().create({
                    'name': vals.get('name'),
                    'email': vals.get('email'),
                })
                vals['partner_id'] = partner.id

            # 2. Gestionar el Usuario
            login = vals.get('email') or vals.get('name').replace(" ", ".").lower()
            user = self.env['res.users'].sudo().search([('login', '=', login)], limit=1)
            
            if not user:
                user = self.env['res.users'].sudo().create({
                    'name': vals.get('name'),
                    'login': login,
                    'partner_id': vals.get('partner_id'),
                    'email': vals.get('email'),
                })
                
                # 3. Forzar grupo Portal
                try:
                    group_portal = self.env.ref('base.group_portal')
                    user.sudo().write({
                        'groups_id': [(6, 0, [group_portal.id])]
                    })
                except Exception:
                    pass
            
            vals['user_id'] = user.id
            
        return super(Student, self).create(vals_list)

    # --- Campos Computados ---
    def _compute_enrollment_count(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)

    def _compute_grade_count(self):
        for record in self:
            record.grade_count = len(record.grade_ids)

    # --- Acciones (Botones) ---
    def action_view_enrollments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window", 
            "res_model": "university.enrollment", 
            "view_mode": "list,form", 
            "domain": [("student_id", "=", self.id)]
        }

    def action_view_grades(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window", 
            "res_model": "university.grade", 
            "view_mode": "list,form", 
            "domain": [("student_id", "=", self.id)]
        }

    def action_send_report_email(self):
        self.ensure_one()
        try:
            template = self.env.ref('university.email_template_student_report')
            template_id = template.id
        except:
            template_id = False

        return {
            'type': 'ir.actions.act_window', 
            'view_mode': 'form', 
            'res_model': 'mail.compose.message', 
            'target': 'new', 
            'context': {
                'default_model': 'university.student', 
                'default_res_ids': self.ids,
                'default_template_id': template_id,
            }
        }

    # ESTA FUNCIÓN AHORA ESTÁ BIEN ALINEADA
    def action_send_grades_summary_js(self):
        """ Sends the email directly and confirms success to the JS controller """
        self.ensure_one()
        try:
            template = self.env.ref('university.email_template_student_report')
            if template:
                template.send_mail(self.id, force_send=True)
                return True
        except Exception:
            return False
        return False