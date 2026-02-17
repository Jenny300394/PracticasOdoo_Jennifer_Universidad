from odoo import models, fields, api

class University(models.Model):
    _name = "university.university"
    _description = "University"

    # BASIC FIELDS
    name = fields.Char(string="Name", required=True)
    image_1920 = fields.Image(string="Image")

    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    state_id = fields.Many2one("res.country.state", string="State")
    zip = fields.Char(string="ZIP")
    country_id = fields.Many2one("res.country", string="Country")

    director_id = fields.Many2one(
        "university.professor",
        string="Director",
    )

    # RELATIONS + COUNTERS
    enrollment_ids = fields.One2many(
        "university.enrollment",
        "university_id",
        string="Enrollments",
    )
    enrollment_count = fields.Integer(
        string="Enrollments Count",
        compute="_compute_enrollment_count",
    )

    student_ids = fields.One2many(
        "university.student",
        "university_id",
        string="Students",
    )
    student_count = fields.Integer(
        string="Students Count",
        compute="_compute_student_count",
    )

    professor_ids = fields.One2many(
        "university.professor",
        "university_id",
        string="Professors",
    )
    professor_count = fields.Integer(
        string="Professors Count",
        compute="_compute_professor_count",
    )

    department_ids = fields.One2many(
        "university.department",
        "university_id",
        string="Departments",
    )
    department_count = fields.Integer(
        string="Departments Count",
        compute="_compute_department_count",
    )

    # COMPUTE METHODS
    def _compute_enrollment_count(self):
        for record in self:
            record.enrollment_count = len(record.enrollment_ids)

    def _compute_student_count(self):
        for record in self:
            record.student_count = len(record.student_ids)

    def _compute_professor_count(self):
        for record in self:
            record.professor_count = len(record.professor_ids)

    def _compute_department_count(self):
        for record in self:
            record.department_count = len(record.department_ids)

    # SMARTBUTTON ACTIONS
    def action_view_students(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Students",
            "res_model": "university.student",
            "view_mode": "list,kanban,form",
            "domain": [("university_id", "=", self.id)],
            "context": {"default_university_id": self.id},
        }

    def action_view_professors(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Professors",
            "res_model": "university.professor",
            "view_mode": "list,kanban,form",
            "domain": [("university_id", "=", self.id)],
            "context": {"default_university_id": self.id},
        }

    def action_view_departments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Departments",
            "res_model": "university.department",
            "view_mode": "list,kanban,form",
            "domain": [("university_id", "=", self.id)],
            "context": {"default_university_id": self.id},
        }

    def action_view_enrollments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Enrollments",
            "res_model": "university.enrollment",
            "view_mode": "list,kanban,form",
            "domain": [("university_id", "=", self.id)],
            "context": {"default_university_id": self.id},
        }

    def action_view_subjects(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Subjects",
            "res_model": "university.subject",
            "view_mode": "list,kanban,form",
            "domain": [("university_id", "=", self.id)],
            "context": {"default_university_id": self.id},
        }

    def action_view_grades(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Grades",
            "res_model": "university.grade",
            "view_mode": "list,form",
            "domain": [("student_id.university_id", "=", self.id)],
        }
