============================
Improved MRP-1 Functionality
============================

Algorithm Changes
=================

Material Requirements Planning, as defined by most operations practitioners, means much more than what Odoo provides. The v9 scheduler algorithm (mostly implemented in _procure_orderpoint_confirm) has several problems:

* It should use a low-level-code for sequencing orderpoints. With the current algorithm, orderpoints are executed in the wrong order and some demand is not considered.
* It should time-phase MO/PO start dates by bucket (daily or weekly). The current algorithm schedules everything ASAP, rather than when they are needed.
* It should allow changes to independent demand, built to stock (MOs).  Currently, Odoo requires MOs to be confirmed in order to plan for the components, but then you can't delete them.
* It should be able to delete previously scheduled supply when demand has changed from the last run of the algorithm.  The current algorithm confirms MOs, and can't delete them when they are no longer needed.

These problems make it practially impossible to use the Scheduler for Make-To-Stock operations.  In short, the v9 algorithm is largely deficient in terms of providing MRP-1 functionality.

This module and its dependencies will implement real MRP.  This is MRP-1, not MRP-2, meaning that we do not consider manufacturing capacity.  We assume infinite manufacturing capacity.


Low-Level-Code
--------------

Odoo's current Scheduler considers reorder rules in the order they were created. When orderpoints are executed in the wrong order, some demand is not considered.  For example, consider the case where an orderpoint for a component is considered before that of its parent.  Say the current algorithm triggers an orderpoint for the parent, and generates an MO.  It should also trigger the orderpoint for the component and generate a PO.  But, the algorithm only considers each orderpoint once, and it has already considered the component's orderpoint and found no demand.  Therefore, the needed PO will not be created.

.. image:: http://www.asprova.jp/mrp/glossary/en/fig/mrp_188-2.jpg
   :alt: Low-Level-Code Diagram
   :target: http://www.asprova.jp/mrp/glossary/en/cat248/post-740.html

Low-Level-Coding is the industry standard. It is a fundamental concept in Material Requirements Planning.

Module mrp_llc implements the Low-Level-Code (LLC) in a simple and very efficient recursive query.  The query is stored in a database view, and associated with a new ORM model (mrp.bom.llc).  We then sort the orderpoints by LLC before executing them.


Time-Phase Buckets
------------------

The current scheduling algorithm schedules everything as soon as possible.  That is terribly inefficient in terms of inventory holding cost.  And, of course, it is also impossible to build all MOs at one time.

In mrp_time_buckets, we modify the scheduling algorithm to consider future demand, and create future supply, based on small time periods.  These small time periods are called buckets.  By default, the time buckets have size of one day.  Using time-phasing, we delay orders for components until the day they are needed.


Independent Demand
------------------

`Independent demand <https://en.wikipedia.org/wiki/Material_requirements_planning#Dependent_demand_vs_independent_demand>`_ may include the following:

* Confirmed Sales orders (customer demand)
* Manufacturing orders for finished product (make-to-stock demand)

We need to be able to change independent demand by canceling or deleting orders.  However, deleting confirmed MOs is not allowed.  We need a way to plan for make-to-stock type independent demand, and schedule supply for the raw materials.  And, we need to be able to change our plan.

The mrp_independent_mts module lets the user create manufacturing orders that are flagged as independent demand.  These special orders are considered, by the scheduling algorithm, as independent demand, even when they have not been confirmed.


Dependent Demand
----------------

In the current algorithm, stock moves are used to detect dependent demand for components of MOs.  This requires the MOs to be confirmed.  Once they are confirmed, they can't be changed or deleted.  That leaves the user with potentially hundreds of MOs that may need to be canceled when demand has changed.

The mrp_procurements_only module modifies the scheduling algorithm to create procurement orders, but not run them.  In other words, it does not create MOs and POs.  The MOs and POs are created when the user manually runs procurement orders.  This would be done in batches, at intervals, as needed.


Management Interface Changes
============================

Purchase Buyer Management Interface
-----------------------------------

The purchasing agent (buyer) needs an interface for managing procurement orders.  For this, we add a new menu item, action and tree view to Purchase > Purchase.  The list is filtered to only show items where:
* Either, the route for the product is set to Buy
* Or, the rule on the procurement order is set to Buy

Manufacturing Planner Management Interface
------------------------------------------

The production planner needs an interface for managing procurement orders.  For this, we add a new menu item, action and tree view to Purchase > Purchase.  The list is filtered to only show items where:

* Either, the route for the product is set to Manufacture
* Or, the rule on the procurement order is set to Manufacture

We also add a Due Date field to the manufacturing order.  This is to allow the production planner to inform production workers of the expected due date for manufacturing orders.
