# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    pick_id = fields.Integer(string='Pick Identity')

    def create_materials_list(self):
        for rec in self:
            return\
                {
                    'name': 'Materials List Wizard',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'materials.list.wizard',
                    'target': 'new',
                }
