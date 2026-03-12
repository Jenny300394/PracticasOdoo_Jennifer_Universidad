from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

# --- ACTIVIDADES ANTERIORES: UNIVERSIDAD Y PROFESORES ---
class UniversityWebsite(http.Controller):
    @http.route(['/universidad'], type='http', auth="public", website=True)
    def list_universities(self, **post):
        universities = request.env['university.university'].sudo().search([])
        return request.render("university.university_list_template", {'universities': universities})

    @http.route(['/profesores/<model("university.university"):univ>'], type='http', auth="public", website=True)
    def list_professors(self, univ, **post):
        return request.render("university.professor_list_template", {'university': univ, 'professors': univ.professor_ids})

# --- ACTIVIDAD 13: PORTAL DEL ESTUDIANTE ---
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
        return request.render("university.portal_my_grades_list", {
            'grades': grades, 
            'page_name': 'grades'
        })

# --- ACTIVIDAD 11: DESCUENTO POR PAGO ---
class UniversityWebsiteSale(http.Controller):
    @http.route('/shop/payment/update_discount', type='json', auth="public", website=True, csrf=False)
    def update_discount(self, provider_id, **kwargs):
        # Log para ver si llega la llamada al terminal de Docker
        print(f">>> RECIBIDA LLAMADA PARA PROVIDER: {provider_id}")
        
        if not provider_id:
            return {'status': 'error', 'message': 'ID no recibido'}

        # CORRECCIÓN AQUÍ: Obtenemos el pedido desde la sesión de forma segura
        sale_order_id = request.session.get('sale_order_id')
        if not sale_order_id:
            return {'status': 'error', 'message': 'No hay pedido activo en la sesión'}

        order = request.env['sale.order'].sudo().browse(sale_order_id)
        if not order.exists():
            return {'status': 'error', 'message': 'El pedido no existe'}

        try:
            # Llamamos a tu método en el modelo sale.order
            success = order._update_payment_discount(int(provider_id))
            return {'status': 'success' if success else 'error'}
        except Exception as e:
            print(f"ERROR CRÍTICO EN PYTHON: {str(e)}")
            return {'status': 'error', 'message': str(e)}

# --- ACTIVIDAD 14: API DE SINCRONIZACIÓN (CORRECCIÓN FINAL) ---
class UniversityApi(http.Controller):
    @http.route('/university/sync_product', type='json', auth='none', methods=['POST'], csrf=False)
    def sync_product(self, **post):
        data = request.params
        token_recibido = data.get('token')
        if token_recibido != "asdfghjklqwertyuiop":
            return {"status": 401, "error": "No autorizado"}

        # Dejamos tu env como estaba, que ya sabemos que te funciona
        env = request.env(user=2) 
        
        # EL CAMBIO ES AQUÍ: Aplicamos el contexto al modelo, no al env
        product_tmpl = env['product.template'].with_context(company_id=1, force_company=1)
        default_code = data.get('default_code')

        product_vals = {
            'name': data.get('name'),
            'type': data.get('type', 'consu'),
            'description_sale': data.get('description_sale'),
            'list_price': data.get('lst_price', 0.0), 
            'standard_price': data.get('standard_price', 0.0),
            'default_code': default_code,
            'company_id': 1, # Aseguramos que el producto sepa que es de la empresa 1
        }

        product = product_tmpl.search([('default_code', '=', default_code)], limit=1)
        if product:
            # Aquí también aseguramos que al escribir use el contexto de la empresa
            product.with_context(company_id=1, force_company=1).write(product_vals)
            return {"status": 200, "message": "Producto actualizado"}
        else:
            product_tmpl.create(product_vals)
            return {"status": 201, "message": "Producto creado"}