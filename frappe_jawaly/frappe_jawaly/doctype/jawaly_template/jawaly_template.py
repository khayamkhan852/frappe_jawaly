# Copyright (c) 2025, khayam khan and contributors
# For license information, please see license.txt

import frappe
import re
from frappe.model.document import Document
from frappe.utils.jinja import validate_template


class JawalyTemplate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from frappe_jawaly.frappe_jawaly.doctype.jawaly_template_variable.jawaly_template_variable import JawalyTemplateVariable

		body_text: DF.LongText
		category: DF.Data | None
		enabled: DF.Check
		header_image: DF.Attach | None
		header_text: DF.LongText | None
		header_type: DF.Data | None
		jawaly_template_name: DF.Literal[None]
		jawaly_template_status: DF.Data | None
		reference_doctype: DF.Link
		template: DF.Data | None
		template_id: DF.Data | None
		template_language: DF.Data | None
		template_name: DF.Data
		template_namespace: DF.Data | None
		variables: DF.Table[JawalyTemplateVariable]
		waba_account_id: DF.Data | None
	# end: auto-generated types
	pass

@frappe.whitelist()
def get_variables(body_text, header_text=None):
	body_variables = extract_jinja_variables(body_text)
	
	if header_text:
		header_variables = extract_jinja_variables(header_text)
	else:
		header_variables = []

	return {
		"body_variables": body_variables,
		"header_variables": header_variables
	}

def extract_jinja_variables(template_str):
    """Extract all variables from {{ }} blocks"""
    return re.findall(r"{{\s*(.*?)\s*}}", template_str)