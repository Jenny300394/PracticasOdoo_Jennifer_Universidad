from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Professor(models.Model):
    _name = "university.professor"
    _description = "Professor"

    # --- CAMBIO 1: El email ahora es obligatorio ---
    name = fields.Char(string="Name", required=True)
    email = fields.Char(string="Email", required=True) # <--- Añadido required=True
    
    image_1920 = fields.Image(string="Image", max_width=1920, max_height=1920)
    image_128 = fields.Image(string="Image 128", related="image_1920", max_width=128, max_height=128, store=True)

    university_id = fields.Many2one(
        "university.university", 
        string="University", 
        required=True,
        ondelete='cascade'
    )

    # --- CAMBIO 2: Quitamos 'name_unique' ---
    # Así permitimos que dos personas se llamen igual si tienen emails distintos.
    _sql_constraints = [
        ('email_unique', 'unique(email)', '¡Error! Este email ya pertenece a un profesor en el sistema.'),
    ]

    @api.constrains('email')
    def _check_unique_professor_globally(self):
        for record in self:
            # --- CAMBIO 3: Usamos .sudo() ---
            # Esto es lo que permite buscar en todas las universidades a la vez.
            existing = self.sudo().search([
                ('id', '!=', record.id),
                ('email', '=', record.email)
            ], limit=1)
            
            if existing:
                raise ValidationError(
                    f"¡Detección de duplicado! El profesor con email {record.email} "
                    f"ya está registrado en la universidad: {existing.university_id.name}."
                )

    # El resto de tu código (Relaciones, Contadores y Acciones) se queda EXACTAMENTE IGUAL
    department_id = fields.Many2one("university.department", string="Primary Department")
    department_ids = fields.Many2many(
        "university.department", "university_professor_department_rel", 
        "professor_id", "department_id", string="Secondary Departments"
    )
    subject_ids = fields.Many2many(
        "university.subject", "university_professor_subject_rel", 
        "professor_id", "subject_id", string="Subjects"
    )
    enrollment_ids = fields.One2many("university.enrollment", "professor_id", string="Enrollments")

    enrollment_count = fields.Integer(compute="_compute_counts", string="Enrollment Count", store=True)
    subject_count = fields.Integer(compute="_compute_counts", string="Subject Count", store=True)
    student_count = fields.Integer(compute="_compute_counts", string="Student Count", store=True)

    @api.depends('enrollment_ids', 'subject_ids', 'enrollment_ids.student_id')
    def _compute_counts(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)
            record.subject_count = len(record.subject_ids)
            record.student_count = len(record.enrollment_ids.mapped('student_id'))

    def action_view_enrollments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Enrollments",
            "res_model": "university.enrollment",
            "view_mode": "list,form",
            "domain": [("professor_id", "=", self.id)],
            "context": {"default_professor_id": self.id},
        }

    def action_view_subjects(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Subjects",
            "res_model": "university.subject",
            "view_mode": "list,form",
            "domain": [("id", "in", self.subject_ids.ids)],
        }

    def action_view_students(self):
        self.ensure_one()
        student_ids = self.enrollment_ids.mapped('student_id').ids
        return {
            "type": "ir.actions.act_window",
            "name": "Students",
            "res_model": "university.student",
            "view_mode": "list,form",
            "domain": [("id", "in", student_ids)],
        }