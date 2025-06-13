# Copyright (c) 2025, khayam khan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe_jawaly.apis.jawaly_api import send_message

class JawalyMessage(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from frappe_jawaly.frappe_jawaly.doctype.jawaly_message_variable.jawaly_message_variable import JawalyMessageVariable

		body_text: DF.LongText
		contact: DF.Link | None
		header_text: DF.TextEditor | None
		jawaly_template: DF.Link
		reference_doctype: DF.Link | None
		reference_name: DF.DynamicLink | None
		send_to: DF.Data
		status: DF.Literal["Unsent", "Sent", "Rejected"]
		variables: DF.Table[JawalyMessageVariable]
	# end: auto-generated types
	def validate(self):
		pass

@frappe.whitelist()
def save_jawaly_message(template, send_to, contact=None, reference_doctype=None, reference_name=None):
	template_doc = frappe.get_doc("Jawaly Template", template)

	if reference_doctype != template_doc.reference_doctype:
		frappe.throw(f"Reference Doctype mismatch: Expected '{template_doc.reference_doctype}', but found '{reference_doctype}'. Please verify the selected template.")

	message = frappe.get_doc({
		"doctype": "Jawaly Message",
		"jawaly_template": template_doc.name,
		"contact": contact,
		"status": "Unsent",
		"send_to": send_to,
		"reference_doctype": template_doc.reference_doctype,
		"reference_name": reference_name,
		"header_text": template_doc.header_text,
		"body_text": template_doc.body_text,
		"variables": [
			{
				"variable": variable.variable,
				"default_value": variable.default_value,
				"field_name": variable.field_name,
				"variable_type": variable.variable_type
			} for variable in template_doc.variables
		]
	}).insert(ignore_permissions=True)

	return send_message(jawaly_message_name=message.name)
