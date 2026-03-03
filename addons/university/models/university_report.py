from odoo import models, fields, tools

class UniversityReport(models.Model):
    _name = 'university.report'
    _description = 'University Report'
    _auto = False  
from odoo import models, fields, tools

class UniversityReport(models.Model):
    # Definimos el nombre del informe
    _name = 'university.report'
    _description = 'University Report'
    # Ponemos _auto = False porque no queremos que Odoo cree una tabla normal, sino una vista SQL
    _auto = False  

    # Todos los campos son readonly porque los datos vienen directamente de la base de datos
    university_name = fields.Char(string="University", readonly=True)
    department_name = fields.Char(string="Department", readonly=True)
    professor_name = fields.Char(string="Professor", readonly=True)
    student_name = fields.Char(string="Student", readonly=True)
    subject_name = fields.Char(string="Subject", readonly=True)
    
    # Este campo es especial: group_operator="avg" le dice a Odoo que haga la media automáticamente
    average_grade = fields.Float(string="Average Grade", readonly=True, group_operator="avg")

    def init(self):
        # Esta función se ejecuta al instalar/actualizar para crear la vista en la base de datos
        tools.drop_view_if_exists(self.env.cr, self._table)
        
        # Aquí escribimos la consulta SQL que junta todas las tablas 
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    g.id AS id,
                    u.name AS university_name,
                    d.name AS department_name,
                    p.name AS professor_name,
                    s.name AS student_name,
                    sub.name AS subject_name,
                    g.grade AS average_grade
                FROM university_grade g
                -- Usamos LEFT JOIN para enganchar las tablas aunque falte algún dato
                LEFT JOIN university_enrollment e ON g.enrollment_id = e.id
                LEFT JOIN university_student s ON e.student_id = s.id
                LEFT JOIN university_university u ON s.university_id = u.id
                LEFT JOIN university_professor p ON e.professor_id = p.id
                LEFT JOIN university_subject sub ON e.subject_id = sub.id
                LEFT JOIN university_department d ON p.department_id = d.id
            )
        """ % self._table)
    university_name = fields.Char(string="University", readonly=True)
    department_name = fields.Char(string="Department", readonly=True)
    professor_name = fields.Char(string="Professor", readonly=True)
    student_name = fields.Char(string="Student", readonly=True)
    subject_name = fields.Char(string="Subject", readonly=True)
    # Importante: group_operator="avg" hace que Odoo calcule la media en el pivote
    average_grade = fields.Float(string="Average Grade", readonly=True, group_operator="avg")

    def init(self):
        # Usamos self._table para asegurar que el nombre sea el que Odoo espera
        tools.drop_view_if_exists(self.env.cr, self._table)
        
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    g.id AS id,
                    u.name AS university_name,
                    d.name AS department_name,
                    p.name AS professor_name,
                    s.name AS student_name,
                    sub.name AS subject_name,
                    g.grade AS average_grade
                FROM university_grade g
                LEFT JOIN university_enrollment e ON g.enrollment_id = e.id
                LEFT JOIN university_student s ON e.student_id = s.id
                LEFT JOIN university_university u ON s.university_id = u.id
                LEFT JOIN university_professor p ON e.professor_id = p.id
                LEFT JOIN university_subject sub ON e.subject_id = sub.id
                LEFT JOIN university_department d ON p.department_id = d.id
            )
        """ % self._table)