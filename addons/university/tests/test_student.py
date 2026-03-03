from odoo.tests.common import TransactionCase

class TestStudent(TransactionCase):
    def test_01_student_values(self):
        # Esta prueba sirve para ver si los datos del alumno se guardan bien en la base de datos
        
        # Primero creamos una universidad de prueba rápida
        uni = self.env['university.university'].create({'name': 'Uni Test'})
        
        # Registramos un alumno nuevo vinculado a esa universidad
        student = self.env['university.student'].create({
            'name': 'Jennifer Test',
            'university_id': uni.id,
            'email': 'test@test.com'
        })
        
        # Comprobamos que el nombre y el email guardados coincidan con lo que hemos puesto
        self.assertEqual(student.name, 'Jennifer Test')
        self.assertEqual(student.email, 'test@test.com')