from odoo import models, fields, api

class Subject(models.Model):
    # Nombre del modelo para las asignaturas
    _name = "university.subject"
    _description = "Subject"

    name = fields.Char(string="Name", required=True)
    
    # Si borramos la universidad, sus asignaturas ya no tiene sentido que aparezcan (por eso usamos cascade)
    university_id = fields.Many2one(
        "university.university", 
        string="University", 
        required=True,
        ondelete='cascade'
    )

    # Relación de muchos a muchos con los profesores que imparten la asignatura
    professor_ids = fields.Many2many(
        "university.professor",
        "university_professor_subject_rel",
        "subject_id",
        "professor_id",
        string="Professors",
    )
    
    # Listado de todas las matrículas hechas en esta asignatura
    enrollment_ids = fields.One2many("university.enrollment", "subject_id", string="Enrollments")

    # Campos para llevar la cuenta de cuántos hay de cada cosa
    enrollment_count = fields.Integer(string="Enrollments", compute="_compute_counts")
    student_count = fields.Integer(string="Students", compute="_compute_counts")
    professor_count = fields.Integer(string="Professors Count", compute="_compute_counts")

    # Función para calcular los contadores de los Smart Buttons
    @api.depends('enrollment_ids', 'professor_ids')
    def _compute_counts(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)
            # Con mapped sacamos los estudiantes únicos sin que se repitan
            record.student_count = len(record.enrollment_ids.mapped('student_id'))
            record.professor_count = len(record.professor_ids)

    # Botón para saltar a ver las matrículas de esta asignatura
    def action_view_enrollments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Enrollments",
            "res_model": "university.enrollment",
            "view_mode": "list,form",
            "domain": [("subject_id", "=", self.id)],
            "context": {"default_subject_id": self.id},
        }

    # Botón para ver la lista de alumnos apuntados a esta materia
    def action_view_students(self):
        self.ensure_one()
        student_ids = self.enrollment_ids.mapped('student_id').ids
        return {
            "type": "ir.actions.act_window",
            "name": "Students",
            "res_model": "university.student",
            "view_mode": "list,kanban,form",
            # Si no hay alumnos, pasamos un [0] para que no de error la ventana
            "domain": [("id", "in", student_ids or [0])],
        }

    # Botón para ver los profesores que imparten esta asignatura
    def action_view_professors(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Professors",
            "res_model": "university.professor",
            "view_mode": "list,form",
            "domain": [("id", "in", self.professor_ids.ids or [0])],
        }