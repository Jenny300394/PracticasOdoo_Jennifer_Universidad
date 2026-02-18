{
    "name": "University",
    "version": "1.0",
    "summary": "University management tutorial module",
    "description": "Module to manage universities, departments, professors, students, enrollments and grades.",
    "author": "Jennifer",
    "category": "Education",
    "depends": ["base"],
        "data": [
        "security/ir.model.access.csv",
        "views/university_views.xml",
        "views/university_menus.xml",
        "views/university_report_views.xml"
    ],

    "installable": True,
    "application": True
}
