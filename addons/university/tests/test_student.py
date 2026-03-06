from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestUniversity(TransactionCase):

    def setUp(self):
        """Preparamos los datos básicos para todas las pruebas"""
        super(TestUniversity, self).setUp()
        
        # 1. Universidad
        self.uni = self.env['university.university'].create({
            'name': 'Universidad de Jennifer'
        })
        
        # 2. Estudiante
        self.student = self.env['university.student'].create({
            'name': 'Jennifer Test',
            'university_id': self.uni.id,
            'email': 'jennifer@test.com'
        })
        
        # 3. Asignatura
        self.subject = self.env['university.subject'].create({
            'name': 'Programación Odoo',
            'university_id': self.uni.id
        })

    def test_01_student_values(self):
        """¿Se guardan los datos básicos?"""
        self.assertEqual(self.student.name, 'Jennifer Test')
        self.assertEqual(self.student.email, 'jennifer@test.com')

    def test_02_enrollment_count(self):
        """¿El contador de matrículas sube al matricular?"""
        self.env['university.enrollment'].create({
            'student_id': self.student.id,
            'subject_id': self.subject.id,
            'university_id': self.uni.id,
        })
        self.student._compute_counts()
        self.assertEqual(self.student.enrollment_count, 1)

    def test_03_grade_logic(self):
        """¿Se vinculan bien las calificaciones y el display_name?"""
        enrollment = self.env['university.enrollment'].create({
            'student_id': self.student.id,
            'subject_id': self.subject.id,
            'university_id': self.uni.id,
        })
        
        grade_rec = self.env['university.grade'].create({
            'student_id': self.student.id,
            'enrollment_id': enrollment.id,
            'grade': 8.5
        })
        
        self.assertEqual(grade_rec.grade, 8.5)
        # Verificamos que el display_name se calculó (ej: "Jennifer Test - MATRICULA-XXX")
        self.assertIn('Jennifer Test', grade_rec.display_name)

    def test_04_grade_security(self):
        """¿Bloquea notas mayores a 10? (Validación de rango)"""
        enrollment = self.env['university.enrollment'].create({
            'student_id': self.student.id,
            'subject_id': self.subject.id,
            'university_id': self.uni.id,
        })
        
        with self.assertRaises(ValidationError):
            self.env['university.grade'].create({
                'student_id': self.student.id,
                'enrollment_id': enrollment.id,
                'grade': 15.0
            })

    def test_05_cascade_delete(self):
        """INTEGRIDAD: Si borro al alumno, ¿desaparecen sus notas? (ondelete='cascade')"""
        enrollment = self.env['university.enrollment'].create({
            'student_id': self.student.id,
            'subject_id': self.subject.id,
            'university_id': self.uni.id,
        })
        grade_rec = self.env['university.grade'].create({
            'student_id': self.student.id,
            'enrollment_id': enrollment.id,
            'grade': 7.0
        })
        grade_id = grade_rec.id
        
        # Borramos al alumno
        self.student.unlink()
        
        # Buscamos la nota por ID para ver si todavía existe
        remaining_grade = self.env['university.grade'].search([('id', '=', grade_id)])
        self.assertFalse(remaining_grade, "La nota debería haberse borrado automáticamente (Cascade)")

    def test_06_student_email_change(self):
        """¿Se actualiza correctamente el email del alumno?"""
        self.student.write({'email': 'nuevo_email@jennifer.com'})
        self.assertEqual(self.student.email, 'nuevo_email@jennifer.com')
#comando para terminal y ver si funcionan test docker compose run --rm odoo -u university -d University_completa --test-enable --stop-after-init