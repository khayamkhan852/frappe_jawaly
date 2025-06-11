# Copyright (c) 2025, khayam khan and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class JawalyMessageVariable(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		default_value: DF.Data | None
		field_name: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		variable: DF.Data
		variable_type: DF.Literal["Body", "Header"]
	# end: auto-generated types
	pass
