# Copyright (c) 2025, khayam khan and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class JawalySettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		api_key: DF.Data | None
		api_secret: DF.Password | None
		base_url: DF.Data | None
		expired_at: DF.Date | None
		language_policy: DF.Data | None
		whatsapp_number: DF.Data | None
		whatsapp_number_id: DF.Data | None
	# end: auto-generated types
	pass
