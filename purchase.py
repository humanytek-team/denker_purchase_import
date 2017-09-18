# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import UserError, RedirectWarning, ValidationError
import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    order_import_line = fields.One2many('purchase.order.import.line', 'order_id', string='Import Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)




    def action_update_imports(self):
        #print 'self.env.context.get(update_import,False): ',self.env.context.get('update_import',False)
        dict(self.env.context).update({'update_import' : True})
        #self.env.context['update_import'] = True

        #SE OBTIENEN LOS IDS DE LAS LINEAS
        line_ids = [line.id for line in self.order_line if self.order_line]
        import_purchase_line_ids = [import_line.purchase_line_id for import_line in self.order_import_line if self.order_import_line]


        import_vals = {'order_import_line': []}

        if self.order_line:
            for line in self.order_line:
                x = 0
                import_line_id = False
                #SI EXISTE YA EN IMPORT LINES, SOLO SE ACTUALIZAN LOS DATOS
                if line.id in import_purchase_line_ids:
                    import_line_id = self.env['purchase.order.import.line'].search([('purchase_line_id', '=', line.id )])[0]['id']
                    x = 1
                import_line_vals = [x, import_line_id, {
                    'name':line.name,
                    'purchase_line_id':line.id,
                    'product_qty':line.product_qty,
                    'date_planned':line.date_planned,
                    'taxes_id':line.taxes_id,
                    'product_uom':line.product_uom.id,
                    'product_id':line.product_id.id,
                    'price_unit':line.price_unit,
                    'price_subtotal':line.price_subtotal,
                    'price_total':line.price_total,
                    'price_tax':line.price_tax,
                    'order_id':line.order_id.id,
                    'account_analytic_id':line.account_analytic_id.id,
                    'analytic_tag_ids':line.analytic_tag_ids,
                    'company_id':line.company_id.id,
                    'state':line.state,
                    #'qty_invoiced':line.qty_invoiced,
                    #'qty_received':line.qty_received,
                    'partner_id':line.partner_id.id,
                    'currency_id':line.currency_id.id,
                    'date_order':line.date_order,
                }]
                import_vals['order_import_line'].append(import_line_vals)

            #SE REVISAN QUE TODOS LOS LINE_ID ESTEN EN LAS LINEAS DE IMPORT, 
            #DE LO CONTRARIO SE BORRAN LAS LINEAS DE IMPORT EXTRA
            if self.order_import_line:
                for import_purchase_line in self.order_import_line:
                    if import_purchase_line.purchase_line_id not in line_ids:
                        import_line_vals = [2, import_purchase_line.id, False]
                        import_vals['order_import_line'].append(import_line_vals)

            #self.order_import_line = import_vals['order_import_line']
            self.with_context({'update_import' : True}).write(import_vals)
        return

    @api.model
    def create(self, values):
        #print 'create'
        #print 'values: ',values
        record = super(PurchaseOrder, self).create(values)

        #if self.env.context.get('update_import',False) == False:
        record.action_update_imports()
        return record



    def write(self, values):
        #print 'purchase_write'
        #print 'values: ',values
        #print '------------------------------------------'
        record = super(PurchaseOrder, self).write(values)

        #print 'context: ',self.env.context
        if self.env.context.get('update_import',False) == False:
            self.action_update_imports()

        return record


class PurchaseOrderImportLine(models.Model):
    _name = "purchase.order.import.line"

    #NEW FIELDS
    in_date = fields.Date('Fecha de arribo')
    import_no = fields.Char('No. de Importacion')
    import_status = fields.Char('Status de Importacion')
    request_no = fields.Char('No. Pedimento')
    customs = fields.Char('Agencia Aduana')
    
    name = fields.Text(string='Description', required=True)
    purchase_line_id = fields.Integer('purchase_line_id',required=True) #id de linea de compra a la que corresponde
    #sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True)
    date_planned = fields.Datetime(string='Scheduled Date', required=True, index=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, required=True)
    #move_ids = fields.One2many('stock.move', 'purchase_line_id', string='Reservation', readonly=True, ondelete='set null', copy=False)
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))

    # price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    # price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    # price_tax = fields.Monetary(compute='_compute_amount', string='Tax', store=True)
    price_subtotal = fields.Monetary(string='Subtotal', store=True)
    price_total = fields.Monetary(tring='Total', store=True)
    price_tax = fields.Monetary(string='Tax', store=True)

    order_id = fields.Many2one('purchase.order', string='Order Reference', index=True, required=True, ondelete='cascade')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    company_id = fields.Many2one('res.company', related='order_id.company_id', string='Company', store=True, readonly=True)
    state = fields.Selection(related='order_id.state', store=True)

    #invoice_lines = fields.One2many('account.invoice.line', 'purchase_line_id', string="Bill Lines", readonly=True, copy=False)

    # Replace by invoiced Qty
    #qty_invoiced = fields.Float(compute='_compute_qty_invoiced', string="Billed Qty", digits=dp.get_precision('Product Unit of Measure'), store=True)
    #qty_received = fields.Float(compute='_compute_qty_received', string="Received Qty", digits=dp.get_precision('Product Unit of Measure'), store=True)

    #qty_invoiced = fields.Float(string="Billed Qty", digits=dp.get_precision('Product Unit of Measure'), store=True)
    #qty_received = fields.Float(string="Received Qty", digits=dp.get_precision('Product Unit of Measure'), store=True)

    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True, store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=True)
    date_order = fields.Datetime(related='order_id.date_order', string='Order Date', readonly=True)
    #procurement_ids = fields.One2many('procurement.order', 'purchase_line_id', string='Associated Procurements', copy=False)

