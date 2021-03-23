# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MaterialsListModel(models.Model):
    _name = 'materials.list.model'
    _description = 'Materials List Model'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    to_consume = fields.Integer('To Consume', default=0, required=True)
    order_id = fields.Many2one('sale.order', string='Order', readonly=True, default=lambda self: self.env.context.get('active_id'))


class MaterialsListWizard(models.TransientModel):
    _name = 'materials.list.wizard'
    _description = 'Add Materials List'

    @api.depends('materials_list_id')
    def _compute_pick_state(self):
        for rec in self:
            order = self.env['sale.order'].search([('id', '=', self.env.context.get('active_id'))])
            pick = self.env['stock.picking'].search([('id', '=', order.pick_id)])

            if pick:
                if pick.state in ['draft', 'waiting', 'confirmed', 'assigned']:
                    rec.state = 'draft'
                elif pick.state == 'done':
                    rec.state = 'confirm'
            else:
                rec.state = 'draft'

    @api.model
    def get_materials_list(self):
        return self.env['materials.list.model'].search([('order_id', '=', self.env.context.get('active_id'))]).ids

    @api.model
    def get_default_location(self):
        order = self.env['sale.order'].search([('id', '=', self.env.context.get('active_id'))])
        pick = self.env['stock.picking'].search([('id', '=', order.pick_id)])

        if pick:
            return pick.location_id.id
        else:
            return None

    materials_list_id = fields.Many2many('materials.list.model', string='Materials List', default=get_materials_list)
    location_id = fields.Many2one('stock.location', string='Stock Location', required=True, default=get_default_location, domain="[('usage', 'in', ['internal'])]")

    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], string='State', compute='_compute_pick_state')

    def save_material_list(self):
        for rec in self:
            order_id = self.env.context.get('active_id')
            order = self.env['sale.order'].search([('id', '=', order_id)])

            pick = self.env['stock.picking'].search([('id', '=', order.pick_id)])

            if not pick:
                moves_list = [(5, 0, 0)]

                for object in rec.materials_list_id:
                    move_values = \
                        {
                            'name': object.product_id.name,
                            'location_id': rec.location_id.id,
                            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                            'product_id': object.product_id.id,
                            'product_uom': object.product_id.product_tmpl_id.uom_id.id,
                            'product_uom_qty': object.to_consume,
                        }
                    moves_list.append((0, 0, move_values))

                picking_type_object = self.env['stock.picking.type'].search([('default_location_src_id', '=', rec.location_id.id), ('sequence_code', '=', 'OUT')])

                if not picking_type_object:
                    picking_type_object = self.env['stock.picking.type'].search([('default_location_src_id', '=', rec.location_id.location_id.id), ('sequence_code', '=', 'OUT')])

                if not picking_type_object:
                    picking_type_object = self.env['stock.picking.type'].search([('warehouse_id', '=', order.warehouse_id.id), ('sequence_code', '=', 'OUT')])

                stock_picking_values = \
                    {
                        'location_id': rec.location_id.id,
                        'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                        'picking_type_id': picking_type_object.id,
                        'state': 'assigned',
                        'partner_id': order.partner_id.id,
                        'company_id': self.env.company.id,
                        'origin': order.name,
                    }

                pick = self.env['stock.picking'].create(stock_picking_values)
                pick.move_ids_without_package = moves_list
                order.pick_id = pick.id
            else:
                moves_list = [(5, 0, 0)]

                for object in rec.materials_list_id:
                    move_values = \
                        {
                            'name': object.product_id.name,
                            'location_id': rec.location_id.id,
                            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                            'product_id': object.product_id.id,
                            'product_uom': object.product_id.product_tmpl_id.uom_id.id,
                            'product_uom_qty': object.to_consume,
                        }
                    moves_list.append((0, 0, move_values))

                stock_picking_values = \
                    {
                        'location_id': rec.location_id.id,
                        'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                        'state': 'assigned',
                        'partner_id': order.partner_id.id,
                        'company_id': self.env.company.id,
                        'origin': order.name,
                    }

                pick.write(stock_picking_values)
                pick.move_ids_without_package = moves_list
