{
    "name": "University",
    "version": "1.0",
    "summary": "University management tutorial module",
    "description": "Module to manage universities, departments, professors, students, enrollments and grades.",
    "author": "Jennifer",
    "category": "Education",
    "depends": [
        "base", 
        "mail", 
        "website", 
        "portal", 
        "website_sale", 
        "payment",
        "sale_management", 
        "stock"            
    ],
  "data": [
        "security/ir.model.access.csv",
        "views/university_views.xml",             
        "views/university_menus.xml",            
        "views/student_report_template.xml",     
        "views/university_report_views.xml",      
        "views/university_mail_templates.xml", 
        "views/university_website_templates.xml", 
        "views/university_portal_templates.xml",
        "views/payment_provider_views.xml", 
        "views/website_sale_templates.xml", 
        "views/stock_picking_views.xml", 
        "views/sale_order_views.xml",
        "views/university_reports_inherit.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "university/static/src/js/payment_discount.js"
        ]
    },
    "demo": [
        "demo/university_demo.xml"
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3"
}