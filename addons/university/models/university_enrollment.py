from odoo import models, fields, api

class Enrollment(models.Model):
    # Definimos el nombre del modelo y que se ordene por el nombre de matrícula
    _name = "university.enrollment"
    _description = "Enrollment"
    _order = "name"
    # Añadimos el chatter para poder escribir notas y ver el historial
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # El código de matrícula se genera solo, por eso es readonly
    name = fields.Char(string="Enrollment Code", readonly=True, copy=False, tracking=True)

    # Relación con el alumno. Si se borra el alumno, se borra su matrícula (cascade)
    student_id = fields.Many2one(
        "university.student", 
        string="Student", 
        required=True, 
        ondelete='cascade'
    )
    # Relación con la universidad a la que pertenece esta matrícula
    university_id = fields.Many2one(
        "university.university", 
        string="University", 
        required=True, 
        ondelete='cascade'
    )
    
    # El profesor que da la clase. Si el profesor se va, la matrícula sigue existiendo
    professor_id = fields.Many2one(
        "university.professor", 
        string="Professor", 
        required=False, 
        tracking=True,
        ondelete='set null' 
    )
    
    # La asignatura de la matrícula. 'restrict' no deja borrar la asignatura si hay gente matriculada
    subject_id = fields.Many2one(
        "university.subject", 
        string="Subject", 
        required=True,
        ondelete='restrict' 
    )
    
    # Listado de notas que tiene esta matrícula específica
    grade_ids = fields.One2many("university.grade", "enrollment_id", string="Grades")

    # Contador para saber cuántas notas hay puestas
    grade_count = fields.Integer(compute='_compute_grade_count')

    # Función para calcular el número de notas vinculadas
    def _compute_grade_count(self):
        for record in self:
            record.grade_count = len(record.grade_ids) 

    # Botón para ir directamente a las notas de esta matrícula
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
        # Cuando creamos la matrícula, generamos un código automático tipo ASIG/2026/0001
        record = super().create(vals)
        subject = record.subject_id
        year = fields.Date.today().year
        # Cogemos las 3 primeras letras de la asignatura para el código
        prefix = subject.name[:3].upper() if subject.name else 'ENR'
        # Contamos cuántas hay de esa asignatura este año para poner el número siguiente
        count = self.search_count([
            ("subject_id", "=", subject.id),
            ("name", "like", f"{prefix}/{year}/")
        ]) + 1
        # Formateamos el código final
        record.name = f"{prefix}/{year}/{count:04d}"
        return record