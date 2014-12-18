# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP Module
#    
#    Copyright (C) 2014 Asphalt Zipper, Inc.
#    Author scosist
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _

class stock_warehouse_orderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'
    _order = 'product_llc'

    product_llc = fields.Integer(string='Product LLC', store=True, related='product_id.low_level_code', readonly=True)
    #product_llc = fields.Related('product_id', 'low_level_code', type='integer', string='Product LLC', store={'product.product': (lambda self, ids: self.env['stock.warehouse.orderpoint'].search([('product_id', 'in', ids)]), ['low_level_code'], 10),})


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
