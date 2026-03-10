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

    # ESTA FUNCIÓN TIENE QUE ESTAR AQUÍ DENTRO (CON ESPACIOS A LA IZQUIERDA)
    @http.route(['/my/grades'], type='http', auth="user", website=True)
    def portal_my_grades(self, **kw):
        student = request.env['university.student'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        grades = request.env['university.grade'].sudo().search([('student_id', '=', student.id)]) if student else []
        
        # Usamos portal_my_grades_list que es el ID que pusiste en tu XML
        return request.render("university.portal_my_grades_list", {
            'grades': grades, 
            'page_name': 'grades'
        })

class UniversityWebsiteSale(http.Controller):
    # Añadimos csrf=False aquí abajo
    @http.route(['/shop/payment/update_discount'], type='json', auth="public", website=True, csrf=False)
    def update_payment_discount(self, provider_id=None, **post):
        order = request.website.sale_get_order()
        if not order:
            return {'status': 'error', 'message': 'Pedido no encontrado'}

        try:
            # Importante: provider_id suele llegar como entero desde el radio button
            if provider_id:
                order.sudo()._update_payment_discount(provider_id)
                return {'status': 'success'} 
            return {'status': 'error', 'message': 'ID de proveedor no válido'}
        except Exception as e:
            # Enviamos el error real para que no rompa el JSON
            return {'status': 'error', 'message': str(e)}

#Actividad 14

class UniversityApi(http.Controller):
    
    @http.route('/university/sync_product', type='json', auth='none', methods=['POST'], csrf=False)
    def sync_product(self, **post):
        # CAMBIO: Usamos 'post' directamente, es más seguro en Odoo 19
        data = post 
        token_recibido = data.get('token')

        if token_recibido != "asdfghjklqwertyuiop":
            return {
                "status": 401, 
                "error": "No autorizado",
                "message": "El token proporcionado no es válido."
            }

        name = data.get('name')
        default_code = data.get('default_code')

        product_vals = {
            'name': name,
            'type': data.get('type', 'consu'),
            'description_sale': data.get('description_sale'),
            'lst_price': data.get('lst_price', 0.0),
            'standard_price': data.get('standard_price', 0.0),
            'default_code': default_code,
        }

        # Buscamos y operamos con sudo()
        product_tmpl = request.env['product.template'].sudo()
        product = product_tmpl.search([('default_code', '=', default_code)], limit=1)

        if product:
            product.write(product_vals)
            return {"status": 200, "message": "Producto actualizado con éxito"}
        else:
            product_tmpl.create(product_vals)
            return {"status": 201, "message": "Producto creado con éxito"}