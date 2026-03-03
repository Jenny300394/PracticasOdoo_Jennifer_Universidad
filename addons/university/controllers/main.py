from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class UniversityWebsite(http.Controller):

    @http.route(['/universidad'], type='http', auth="public", website=True)
    def list_universities(self, **post):
        # Sacamos todas las universidades para que salgan en la lista de la web
        universities = request.env['university.university'].sudo().search([])
        return request.render("university.university_list_template", {
            'universities': universities
        })

    @http.route(['/profesores/<model("university.university"):univ>'], type='http', auth="public", website=True)
    def list_professors(self, univ, **post):
        # Aquí mostramos solo los profesores que son de la universidad que hemos pinchado
        return request.render("university.professor_list_template", {
            'university': univ,
            'professors': univ.professor_ids
        })

class UniversityPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        # Llamamos a lo que ya hace Odoo por defecto en el portal
        values = super()._prepare_home_portal_values(counters)
        
        # Buscamos si el usuario que ha entrado tiene ficha de estudiante
        student = request.env['university.student'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id)
        ], limit=1)

        # Si no es un estudiante, le quitamos el botón de notas para que no lo vea
        if not student:
            if 'grade_count' in values:
                del values['grade_count']
            return values

        # Si sí es un alumno, contamos sus notas para que salga el aviso en el portal
        if 'grade_count' in counters:
            values['grade_count'] = request.env['university.grade'].sudo().search_count([
                ('student_id', '=', student.id)
            ])
        return values

    @http.route(['/my/grades'], type='http', auth="user", website=True)
    def portal_my_grades(self, **kw):
        # Volvemos a buscar al estudiante para poder sacar sus cosas
        student = request.env['university.student'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id)
        ], limit=1)
        
        # Filtramos para que el alumno solo pueda ver sus notas y no las de otros
        grades = request.env['university.grade'].sudo().search([
            ('student_id', '=', student.id)
        ]) if student else []
        
        return request.render("university.portal_my_grades_template", {
            'grades': grades,
            'page_name': 'grades',
        })