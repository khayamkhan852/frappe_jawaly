# Copyright (c) 2025, khayam khan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

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