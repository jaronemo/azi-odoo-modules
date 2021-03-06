# -*- coding: utf-8 -*-
# See __openerp__.py file for full copyright and licensing details.

from openerp import models, api
from openerp.tools import float_compare, float_round
from psycopg2 import OperationalError
import openerp


class procurement_order(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _update_llc(self, use_new_cursor=False):
        llc_obj = self.env['mrp.bom.llc']
        llc_obj.update_orderpoint_llc()
        if use_new_cursor:
            self._cr.commit()

    # override stock/procurement
    def _procure_orderpoint_confirm(self, cr, uid, use_new_cursor=False, company_id=False, context=None):
        '''
        Create procurement based on Orderpoint

        :param bool use_new_cursor: if set, use a dedicated cursor and auto-commit after processing each procurement.
            This is appropriate for batch jobs only.
        '''
        if context is None:
            context = {}
        self._update_llc(cr, uid, use_new_cursor=use_new_cursor, context=context)
        if use_new_cursor:
            cr = openerp.registry(cr.dbname).cursor()
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        procurement_obj = self.pool.get('procurement.order')
        product_obj = self.pool.get('product.product')

        dom = company_id and [('company_id', '=', company_id)] or []
        orderpoint_ids = orderpoint_obj.search(cr, uid, dom, order="location_id, llc")
        prev_ids = []
        tot_procs = []
        while orderpoint_ids:
            ids = orderpoint_ids[:1000]
            del orderpoint_ids[:1000]
            product_dict = {}
            ops_dict = {}
            ops = orderpoint_obj.browse(cr, uid, ids, context=context)

            #Calculate groups that can be executed together
            for op in ops:
                key = (op.location_id.id,)
                if not product_dict.get(key):
                    product_dict[key] = [op.product_id]
                    ops_dict[key] = [op]
                else:
                    product_dict[key] += [op.product_id]
                    ops_dict[key] += [op]

            for key in product_dict.keys():
                ctx = context.copy()
                ctx.update({'location': ops_dict[key][0].location_id.id})
                prod_qty = product_obj._product_available(cr, uid, [x.id for x in product_dict[key]],
                                                          context=ctx)
                subtract_qty = orderpoint_obj.subtract_procurements_from_orderpoints(cr, uid, [x.id for x in ops_dict[key]], context=context)
                for op in ops_dict[key]:
                    try:
                        prods = prod_qty[op.product_id.id]['virtual_available']
                        if prods is None:
                            continue
                        if float_compare(prods, op.product_min_qty, precision_rounding=op.product_uom.rounding) <= 0:
                            qty = max(op.product_min_qty, op.product_max_qty) - prods

                            # maintain qty_multiple by subtracting procurements first
                            qty -= subtract_qty[op.id]

                            reste = op.qty_multiple > 0 and qty % op.qty_multiple or 0.0
                            if float_compare(reste, 0.0, precision_rounding=op.product_uom.rounding) > 0:
                                qty += op.qty_multiple - reste

                            if float_compare(qty, 0.0, precision_rounding=op.product_uom.rounding) < 0:
                                continue

                            qty_rounded = float_round(qty, precision_rounding=op.product_uom.rounding)
                            if qty_rounded > 0:
                                proc_id = procurement_obj.create(cr, uid,
                                                                 self._prepare_orderpoint_procurement(cr, uid, op, qty_rounded, context=context),
                                                                 context=context)
                                tot_procs.append(proc_id)
                            if use_new_cursor:
                                cr.commit()
                    except OperationalError:
                        if use_new_cursor:
                            orderpoint_ids.append(op.id)
                            cr.rollback()
                            continue
                        else:
                            raise
            try:
                tot_procs.reverse()
                self.run(cr, uid, tot_procs, context=context)
                tot_procs = []
                if use_new_cursor:
                    cr.commit()
            except OperationalError:
                if use_new_cursor:
                    cr.rollback()
                    continue
                else:
                    raise

            if use_new_cursor:
                cr.commit()
            if prev_ids == ids:
                break
            else:
                prev_ids = ids

        if use_new_cursor:
            cr.commit()
            cr.close()
        return {}
