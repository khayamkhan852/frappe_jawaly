# Copyright (c) 2025, khayam khan and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CreateJawalyTemplateVariable(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		example_value: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		variable: DF.Data
	# end: auto-generated types
	pass
