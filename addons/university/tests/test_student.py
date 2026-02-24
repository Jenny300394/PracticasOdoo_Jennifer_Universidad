
from odoo.tests.common import TransactionCase

class TestStudent(TransactionCase):
    def test_01_student_values(self):
        """Prueba que los valores del estudiante se guarden correctamente"""
        uni = self.env['university.university'].create({'name': 'Uni Test'})
        student = self.env['university.student'].create({
            'name': 'Jennifer Test',
            'university_id': uni.id,
            'email': 'test@test.com'
        })
        self.assertEqual(student.name, 'Jennifer Test')
        self.assertEqual(student.email, 'test@test.com')