from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class UniversityPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        # 1. Llamamos a la función original de Odoo
        values = super()._prepare_home_portal_values(counters)
        
        # 2. Solo calculamos si el portal nos pide el contador de notas
        if 'grade_count' in counters:
            # Buscamos al estudiante vinculado al usuario actual
            student = request.env['university.student'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if student:
                # Contamos las notas de este estudiante específico
                count = request.env['university.grade'].sudo().search_count([
                    ('student_id', '=', student.id)
                ])
                values['grade_count'] = count
            else:
                # Si no es estudiante (ej. es un administrador), mostramos 0
                values['grade_count'] = 0
                
        return values

    @http.route(['/my/grades'], type='http', auth="user", website=True)
    def portal_my_grades(self, **kw):
        # 3. Verificamos quién es el estudiante logueado
        student = request.env['university.student'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        # 4. Si el usuario no tiene ficha de estudiante, lo devolvemos al portal principal
        if not student:
            return request.redirect('/my')

        # 5. Buscamos todas las notas del alumno
        # Ordenamos por fecha o ID para que el alumno vea lo más reciente primero
        grades = request.env['university.grade'].sudo().search([
            ('student_id', '=', student.id)
        ], order="id desc")
        
        # 6. Renderizamos la plantilla (Asegúrate de que el ID coincida con tu XML)
        return request.render("university.portal_my_grades_list", {
            'grades': grades,
            'page_name': 'grades', # Esto sirve para resaltar el menú en el portal
        })