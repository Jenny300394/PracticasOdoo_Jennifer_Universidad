from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class UniversityWebsite(http.Controller):
    @http.route(['/universidad'], type='http', auth="public", website=True)
    def list_universities(self, **post):
        universities = request.env['university.university'].sudo().search([])
        return request.render("university.university_list_template", {'universities': universities})

    @http.route(['/profesores/<model("university.university"):univ>'], type='http', auth="public", website=True)
    def list_professors(self, univ, **post):
        return request.render("university.professor_list_template", {'university': univ, 'professors': univ.professor_ids})

class UniversityPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        student = request.env['university.student'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        if not student:
            if 'grade_count' in values: del values['grade_count']
            return values
        if 'grade_count' in counters:
            values['grade_count'] = request.env['university.grade'].sudo().search_count([('student_id', '=', student.id)])
        return values

    @http.route(['/my/grades'], type='http', auth="user", website=True)
    def portal_my_grades(self, **kw):
        student = request.env['university.student'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        grades = request.env['university.grade'].sudo().search([('student_id', '=', student.id)]) if student else []
        return request.render("university.portal_my_grades_template", {'grades': grades, 'page_name': 'grades'})

# --- ESTO SOLUCIONA TU PROBLEMA ---
class UniversityWebsiteSale(http.Controller):
    @http.route(['/shop/payment/update_discount'], type='json', auth="public", website=True)
    def update_payment_discount(self, provider_id=None, **post):
        # 1. Buscamos el pedido actual. Si no existe, lo creamos.
        order = request.website.sale_get_order(force_create=True)
        
        if order:
            # 2. Obligamos a Odoo a guardar el pedido en la base de datos
            # Le ponemos el cliente actual para que salga en "Pedidos sin pagar"
            order.sudo().write({
                'partner_id': request.env.user.partner_id.id,
                'origin': 'Descuento Web Aplicado'
            })
            
            # 3. Llamamos a tu lógica de Python
            if provider_id:
                order.sudo()._update_payment_discount(provider_id)
            
            # 4. Forzamos el recalculo de impuestos y totales
            order.sudo()._amount_all()
            request.env.cr.commit()
            
            print(f">>> PEDIDO ACTUALIZADO Y VISIBLE: {order.name}")
            return True
        return False