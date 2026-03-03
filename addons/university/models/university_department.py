from odoo import models, fields, api

class Department(models.Model):
    # Definimos el nombre del modelo y su descripción técnica
    _name = "university.department"
    _description = "Department"
    # Heredamos el mail.thread para que el departamento tenga el chat (chatter) abajo
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # El nombre es obligatorio y el tracking=True hace que se guarden los cambios en el chat
    name = fields.Char(string="Name", required=True, tracking=True)
    color = fields.Integer(string="Color Index") 

    # Relación con la universidad. Si se borra la uni, se borran sus departamentos (cascade)
    university_id = fields.Many2one(
        "university.university",
        string="University",
        required=True,
        tracking=True,
        ondelete='cascade',
    )

    # El jefe del departamento. Si se borra el profesor, el campo se queda vacío (set null)
    manager_id = fields.Many2one(
        "university.professor",
        string="Department Manager",
        tracking=True,
        ondelete='set null', 
    )

    # Aquí sacamos la lista de todos los profesores que pertenecen a este departamento
    professor_ids = fields.One2many(
        "university.professor",
        "department_id",
        string="Professors",
    )

    # Campo calculado para saber cuántos profesores hay sin tener que contarlos a mano
    professor_count = fields.Integer(
        string="Professors Count",
        compute="_compute_professor_count",
    )

    # Esta función hace el cálculo real para contar los profesores de cada departamento
    def _compute_professor_count(self):
        professor_data = self.env['university.professor'].read_group(
            [('department_id', 'in', self.ids)], 
            ['department_id'], 
            ['department_id']
        )
        mapped_data = {d['department_id'][0]: d['department_id_count'] for d in professor_data}
        for record in self:
            record.professor_count = mapped_data.get(record.id, 0)

    # Este es el botón (Smart Button) para saltar directamente a ver los profesores
    def action_view_professors(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Professors of {self.name}",
            "res_model": "university.professor",
            "view_mode": "list,kanban,form",
            "domain": [("department_id", "=", self.id)],
            "context": {"default_department_id": self.id},
            "target": "current",
        }