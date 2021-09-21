from werkzeug.wrappers import Response

import frappe
from frappe import _

@frappe.whitelist()
def get_brands():
	brands = frappe.db.get_list('Brand', pluck='name')
	return brands

@frappe.whitelist()
def get_brand_items(brand):
	r = frappe.db.sql('''SELECT DISTINCT i.item_code FROM `tabItem` i 
		INNER JOIN `tabBin` b ON i.item_code = b.item_code 
		AND b.actual_qty > 0.0
		AND i.brand = '{0}' '''.format(brand), as_list=True)
	items = [row[0] for row in r]
	return items

@frappe.whitelist()
def get_stock_details(brand, item, qty):
	frappe.get_doc({
		'doctype': 'Stock Report Log',
		'brand': brand,
		'item': item,
		'qty': qty
	}).insert(ignore_permissions=True)

	warehouse = frappe.db.get_list('Warehouse', filters={'show_on_portal': 1}, pluck='name')
	bins = frappe.db.get_list('Bin', filters={'item_code': item, 'warehouse': ['in', warehouse]}, fields=['item_code', 'actual_qty', 'warehouse'])
	columns = [_('Warehouse'), _('Required Stock Status')]
	data = []
	if len(bins) == 1:
		if bins[0].actual_qty == frappe.utils.flt(0): 
			return {'columns': columns, 'data' : data}

	for row in bins:
		stock_status = ''
		if row.actual_qty >= frappe.utils.flt(qty):
			stock_status = _('Available')
		elif row.actual_qty == frappe.utils.flt(0): 
			stock_status = _('Not Available')
		else:
			stock_status = _('Not Enough ( {0} Units )').format(row.actual_qty)
		data.append([row.warehouse, stock_status])
	response = {
		'columns': columns,
		'data' : data
	}
	return response