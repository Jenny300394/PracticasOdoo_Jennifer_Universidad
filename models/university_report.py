from odoo import models, fields, tools

class UniversityReport(models.Model):
    _name = 'university.report'
    _description = 'University Report'
    _auto = False  

    university_name = fields.Char(string="University")
    department_name = fields.Char(string="Department")
    professor_name = fields.Char(string="Professor")
    student_name = fields.Char(string="Student")
    subject_name = fields.Char(string="Subject")
    average_grade = fields.Float(string="Average Grade")

    def init(self):
        tools.drop_view_if_exists(self._cr, 'university_report')
        self._cr.execute("""
            CREATE VIEW university_report AS (
                SELECT
                    row_number() OVER () AS id,
                    u.name AS university_name,
                    d.name AS department_name,
                    p.name AS professor_name,
                    s.name AS student_name,
                    sub.name AS subject_name,
                    AVG(g.grade) AS average_grade
                FROM university_grade g
                JOIN university_enrollment e ON g.enrollment_id = e.id
                JOIN university_student s ON e.student_id = s.id
                JOIN university_professor p ON e.professor_id = p.id
                JOIN university_subject sub ON e.subject_id = sub.id
                JOIN university_department d ON p.department_id = d.id
                JOIN university_university u ON s.university_id = u.id
                GROUP BY u.name, d.name, p.name, s.name, sub.name
            )
        """)
