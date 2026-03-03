from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Professor(models.Model):
    _name = "university.professor"
    _description = "Professor"

    # El nombre y el email son obligatorios para poder registrar al profesor
    name = fields.Char(string="Name", required=True)
    email = fields.Char(string="Email", required=True)
    
    # Campos para las fotos
    image_1920 = fields.Image(string="Image", max_width=1920, max_height=1920)
    image_128 = fields.Image(string="Image 128", related="image_1920", max_width=128, max_height=128, store=True)

    # Universidad a la que pertenece el profesor
    university_id = fields.Many2one(
        "university.university", 
        string="University", 
        required=True,
        ondelete='cascade'
    )

    # Restricción SQL para que no se repitan los emails en la base de datos
    _sql_constraints = [
        ('email_unique', 'unique(email)', '¡Error! Este email ya pertenece a un profesor en el sistema.'),
    ]

    # Validación extra para avisar si el profesor ya existe en otra universidad
    @api.constrains('email')
    def _check_unique_professor_globally(self):
        for record in self:
            # Usamos .sudo() para que Odoo busque en todas las universidades, no solo en la actual
            existing = self.sudo().search([
                ('id', '!=', record.id),
                ('email', '=', record.email)
            ], limit=1)
            
            if existing:
                raise ValidationError(
                    f"¡Detección de duplicado! El profesor con email {record.email} "
                    f"ya está registrado en la universidad: {existing.university_id.name}."
                )

    # Relaciones con departamentos y asignaturas (usamos Many2many)
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

    # Campos para contar matrículas, asignaturas y alumnos
    enrollment_count = fields.Integer(compute="_compute_counts", string="Enrollment Count", store=True)
    subject_count = fields.Integer(compute="_compute_counts", string="Subject Count", store=True)
    student_count = fields.Integer(compute="_compute_counts", string="Student Count", store=True)

    # Función que hace los cálculos de los contadores
    @api.depends('enrollment_ids', 'subject_ids', 'enrollment_ids.student_id')
    def _compute_counts(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)
            record.subject_count = len(record.subject_ids)
            # Con mapped sacamos los alumnos únicos de todas sus matrículas
            record.student_count = len(record.enrollment_ids.mapped('student_id'))

    # Botón para ver las matrículas de este profesor
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

    # Botón para ver las asignaturas que imparte
    def action_view_subjects(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Subjects",
            "res_model": "university.subject",
            "view_mode": "list,form",
            "domain": [("id", "in", self.subject_ids.ids)],
        }

    # Botón para ver la lista de sus alumnos
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