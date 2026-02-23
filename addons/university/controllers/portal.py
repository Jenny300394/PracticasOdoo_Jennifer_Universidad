from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class UniversityPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        
        # Obligamos a Odoo a considerar 'grades' como un contador válido
        if 'grade_count' not in values:
            # Buscamos al estudiante vinculado al usuario actual
            student = request.env['university.student'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
            
            if student:
                # Contamos solo sus notas (Vinculante)
                values['grade_count'] = request.env['university.grade'].sudo().search_count([('student_id', '=', student.id)])
            else:
                # Si no es estudiante, el contador es 0 y el XML no mostrará el botón
                values['grade_count'] = 0
        return values

    @http.route(['/my/grades'], type='http', auth="user", website=True)
    def portal_my_grades(self):
        # Verificación de seguridad: solo estudiantes acceden
        student = request.env['university.student'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not student:
            return request.redirect('/my')

        # Buscamos las notas vinculadas a ese estudiante
        grades = request.env['university.grade'].sudo().search([('student_id', '=', student.id)])
        
        # IMPORTANTE: Asegúrate de que este ID coincida con el de tu <template>
        return request.render("university.portal_my_grades_template", {
            'grades': grades,
            'page_name': 'grade',
        })