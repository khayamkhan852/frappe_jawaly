# Copyright (c) 2025, khayam khan and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CreateJawalyTemplate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from frappe_jawaly.frappe_jawaly.doctype.create_jawaly_template_variable.create_jawaly_template_variable import CreateJawalyTemplateVariable
		from frappe_jawaly.frappe_jawaly.doctype.jawaly_template_reply_button.jawaly_template_reply_button import JawalyTemplateReplyButton

		allow_meta_to_change_the_category: DF.Check
		body_message: DF.LongText
		body_variable_values: DF.Table[CreateJawalyTemplateVariable]
		button_one_text: DF.Data | None
		button_one_url: DF.Data | None
		button_two_text: DF.Data | None
		button_two_url: DF.Data | None
		category: DF.Link
		footer_text: DF.Text | None
		header_attachement: DF.Attach | None
		header_text: DF.Text | None
		header_type: DF.Literal["WITHOUT", "TEXT", "IMAGE", "FILE", "VIDEO"]
		header_variables: DF.Table[CreateJawalyTemplateVariable]
		language_code: DF.Data | None
		marketing_template_type: DF.Link | None
		message_language: DF.Link
		phone_button_text: DF.Data | None
		phone_number: DF.Phone | None
		reply_buttons: DF.Table[JawalyTemplateReplyButton]
		status: DF.Literal["Not Sent", "Sent", "Rejected"]
		template_name: DF.Data
		url_one_example: DF.Data | None
		url_two_example: DF.Data | None
	# end: auto-generated types

	def before_naming(self):
		self.template_name = self.template_name.replace(' ', '_').lower()

	def validate(self):
		if len(self.body_message) > 1024:
			self.body_message = self.body_message[:1024]

		if self.header_text and len(self.header_text) > 60:
			self.header_text = self.header_text[:60]

		if self.footer_text and len(self.footer_text) > 60:
			self.footer_text = self.footer_text[:60]	

		if self.phone_button_text and len(self.phone_button_text) > 25:
			self.phone_button_text = self.footer_text[:25]	

		if self.button_one_text and len(self.button_one_text) > 25:
			self.button_one_text = self.footer_text[:25]	

		if self.button_two_text and len(self.button_two_text) > 25:
			self.button_two_text = self.footer_text[:25]

		if self.button_one_url and not self.button_one_url.startswith("http"):
			frappe.throw(_("Button One URL must start with 'http://' or 'https://'."))

		if self.button_two_url and not self.button_two_url.startswith("http"):
			frappe.throw(_("Button Two URL must start with 'http://' or 'https://'."))

		if self.url_one_example and not self.url_one_example.startswith("http"):
			frappe.throw(_("URL One Example must start with 'http://' or 'https://'."))

		if self.url_two_example and not self.url_two_example.startswith("http"):
			frappe.throw(_("URL Two Example must start with 'http://' or 'https://'."))
