from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class UniversityPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        
        if 'grade_count' not in values:
            # Buscamos al estudiante vinculado al usuario actual
            student = request.env['university.student'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
            
            if student:
                values['grade_count'] = request.env['university.grade'].sudo().search_count([('student_id', '=', student.id)])
            else:
                values['grade_count'] = 0
        return values

    @http.route(['/my/grades'], type='http', auth="user", website=True)
    def portal_my_grades(self, **kw): # Añadido **kw para evitar errores de ruta
        student = request.env['university.student'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not student:
            return request.redirect('/my')

        grades = request.env['university.grade'].sudo().search([('student_id', '=', student.id)])
        
        # CORRECCIÓN CLAVE: El nombre debe ser portal_my_grades_list para que coincida con tu XML
        return request.render("university.portal_my_grades_list", {
            'grades': grades,
            'page_name': 'grades',
        })