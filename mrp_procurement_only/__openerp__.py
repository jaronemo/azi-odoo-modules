# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP Module
#
# Author: Scott Saunders. Copyright Asphalt Zipper, Inc.
# Contributors: Matt Taylor
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
##############################################################################

{
    "name": "MRP Procurements Only",
    "version": "0.1",
    "summary": "Only generate Procurement Orders.",
    "category": "Manufacturing",
    "author": "scosist",
    "website": "http://www.github.com/asphaltzipper/azi-odoo-modules",
    'description': """
        Separate MO/RFQ generation from Procurement Order generation.

        Note: this module is not compatible with the Calendars on Orderpoints (stock_calendar) module.
    """,
    "depends": ["mrp", "purchase", "mrp_time_bucket"],
    "data" : [
        'security/security.xml',
        'security/ir.model.access.csv',
        'mrp_procurement_only_view.xml',
        'wizard/procurement_run_view.xml',
    ],
    "demo": [],
    "test":[],
    "js":[],
    "css":[],
    "installable": True,
    "auto_install": False,
}
