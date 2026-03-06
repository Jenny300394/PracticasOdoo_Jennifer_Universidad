from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestUniversity(TransactionCase):

    def setUp(self):
        """Preparamos los datos básicos para todas las pruebas"""
        super(TestUniversity, self).setUp()
        
        # 1. Creamos la Universidad
        self.uni = self.env['university.university'].create({
            'name': 'Universidad de Jennifer'
        })
        
        # 2. Creamos un Estudiante
        self.student = self.env['university.student'].create({
            'name': 'Jennifer Test',
            'university_id': self.uni.id,
            'email': 'jennifer@test.com'
        })
        
        # 3. Creamos una Asignatura
        self.subject = self.env['university.subject'].create({
            'name': 'Programación Odoo',
            'university_id': self.uni.id
        })

    def test_01_student_values(self):
        """TEST DE DATOS: ¿Se guardan los datos básicos?"""
        self.assertEqual(self.student.name, 'Jennifer Test')
        self.assertEqual(self.student.email, 'jennifer@test.com')

    def test_02_enrollment_count(self):
        """TEST DE LÓGICA: ¿El contador de matrículas sube al matricular?"""
        # AÑADIDO: university_id para cumplir con el NotNull
        self.env['university.enrollment'].create({
            'student_id': self.student.id,
            'subject_id': self.subject.id,
            'university_id': self.uni.id,
        })
        
        # Forzamos el recálculo
        self.student._compute_counts()
        
        # Verificamos que ahora el contador sea 1
        self.assertEqual(self.student.enrollment_count, 1, "El contador debería haber subido a 1")

    def test_03_grade_logic(self):
        """TEST DE NOTAS: ¿Se vinculan bien las calificaciones?"""
        # AÑADIDO: university_id
        enrollment = self.env['university.enrollment'].create({
            'student_id': self.student.id,
            'subject_id': self.subject.id,
            'university_id': self.uni.id,
        })
        
        # Creamos una nota
        grade_rec = self.env['university.grade'].create({
            'student_id': self.student.id,
            'enrollment_id': enrollment.id,
            'grade': 8.5
        })
        
        # Verificamos que la nota guardada sea la correcta
        self.assertEqual(grade_rec.grade, 8.5)

    def test_04_grade_security(self):
        """TEST DE SEGURIDAD: ¿Bloquea notas mayores a 10?"""
        # AÑADIDO: university_id
        enrollment = self.env['university.enrollment'].create({
            'student_id': self.student.id,
            'subject_id': self.subject.id,
            'university_id': self.uni.id,
        })
        
        # Intentamos crear una nota de 15.0 
        with self.assertRaises(ValidationError):
            self.env['university.grade'].create({
                'student_id': self.student.id,
                'enrollment_id': enrollment.id,
                'grade': 15.0
            })
#comando para terminal y ver si funcionan test docker compose run --rm odoo -u university -d University_completa --test-enable --stop-after-init