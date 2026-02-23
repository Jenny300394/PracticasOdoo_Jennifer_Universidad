from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class UniversityWebsite(http.Controller):

    @http.route(['/universidad'], type='http', auth="public", website=True)
    def list_universities(self, **post):
        universities = request.env['university.university'].sudo().search([])
        return request.render("university.university_list_template", {
            'universities': universities
        })

    @http.route(['/profesores/<model("university.university"):univ>'], type='http', auth="public", website=True)
    def list_professors(self, univ, **post):
        return request.render("university.professor_list_template", {
            'university': univ,
            'professors': univ.professor_ids
        })

class UniversityPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        
        # Buscamos si el usuario actual tiene un perfil de estudiante vinculado
        student = request.env['university.student'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id)
        ], limit=1)

        # Si NO es un estudiante vinculado, ocultamos el menú de notas
        if not student:
            if 'grade_count' in values:
                del values['grade_count']
            return values

        # Si es un alumno, contamos sus notas
        if 'grade_count' in counters:
            values['grade_count'] = request.env['university.grade'].sudo().search_count([
                ('student_id', '=', student.id)
            ])
        return values

    @http.route(['/my/grades'], type='http', auth="user", website=True)
    def portal_my_grades(self, **kw):
        student = request.env['university.student'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id)
        ], limit=1)
        
        # Seguridad extra para que solo vea sus propias notas
        grades = request.env['university.grade'].sudo().search([
            ('student_id', '=', student.id)
        ]) if student else []
        
        return request.render("university.portal_my_grades_template", {
            'grades': grades,
            'page_name': 'grades',
        })