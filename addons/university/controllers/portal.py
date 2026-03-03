from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class UniversityPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        # Primero pillamos lo que ya tiene Odoo en el portal por defecto
        values = super()._prepare_home_portal_values(counters)
        
        if 'grade_count' not in values:
            # Buscamos al estudiante que está conectado ahora mismo comparando su user_id
            student = request.env['university.student'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
            
            if student:
                # Si lo encontramos, contamos cuántas notas tiene para que salga el número
                values['grade_count'] = request.env['university.grade'].sudo().search_count([('student_id', '=', student.id)])
            else:
                # Si no es un estudiante, ponemos el contador a cero
                values['grade_count'] = 0
        return values

    @http.route(['/my/grades'], type='http', auth="user", website=True)
    def portal_my_grades(self, **kw): # Ponemos **kw por si acaso la ruta trae parámetros extra
        # Buscamos otra vez al estudiante para sacar su información
        student = request.env['university.student'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        
        # Si no es un estudiante, lo mandamos fuera (al inicio del portal) por seguridad
        if not student:
            return request.redirect('/my')

        # Buscamos las notas que son solo de este estudiante
        grades = request.env['university.grade'].sudo().search([('student_id', '=', student.id)])
        
        # Mandamos los datos a la plantilla XML que creamos para ver la lista de notas
        return request.render("university.portal_my_grades_list", {
            'grades': grades,
            'page_name': 'grades',
        })