from odoo import http
from odoo.http import request

class UniversityWebsite(http.Controller):

    @http.route(['/universidad'], type='http', auth="public", website=True)
    def list_universities(self, **post):
        # Buscamos todas las universidades
        universities = request.env['university.university'].sudo().search([])
        return request.render("university.university_list_template", {
            'universities': universities
        })

    @http.route(['/profesores/<model("university.university"):univ>'], type='http', auth="public", website=True)
    def list_professors(self, univ, **post):
        # Mostramos los profesores de LA universidad seleccionada
        return request.render("university.professor_list_template", {
            'university': univ,
            'professors': univ.professor_ids
        })