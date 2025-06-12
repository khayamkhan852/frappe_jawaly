import frappe
from frappe import _
import requests
import json
from frappe.utils import get_url

@frappe.whitelist()
def get_templates():
    settings = frappe.get_single("Jawaly Settings")

    if not (settings.api_key and settings.api_secret and settings.whatsapp_number_id and settings.base_url):
        frappe.throw("Missing API Key, Secret, WhatsApp Number ID, or Base URL in Jawaly Settings.")

    base_url = f"{settings.base_url.rstrip('/')}/whatsapp/templates/{settings.whatsapp_number_id}"
    templates = []

    next_url = base_url

    while next_url:
        try:
            response = requests.get(
                next_url,
                auth=(settings.api_key, settings.get_password('api_secret')),
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.HTTPError as e:
            frappe.throw(e.response.text )
        except Exception as e:
            frappe.throw("Failed to fetch templates from 4Jawaly.")

        if response.status_code != 200:
            frappe.throw(f"API Error {response.status_code}: {data.get('message')}")

        page_data = data.get("paginate", {}).get("data", [])
        for template in page_data:
            name = template.get("name") or template.get("id")
            if name:
                templates.append(name)

        next_url = data.get("paginate", {}).get("next_page_url") 

    return templates


@frappe.whitelist()
def get_template_by_name(template_name):
    if not template_name:
        frappe.throw(_("Template name is required."))

    settings = frappe.get_single("Jawaly Settings")

    if not (settings.api_key and settings.api_secret and settings.whatsapp_number_id and settings.base_url):
        frappe.throw("Missing API Key, Secret, WhatsApp Number ID, or Base URL in Jawaly Settings.")

    url = f"{settings.base_url}whatsapp/templates/{settings.whatsapp_number_id}?name={template_name}"

    try:
        response = requests.get(
            url,
            auth=(settings.api_key, settings.get_password('api_secret')),
            headers={
                "Accept": "application/json"
            }
        )  

        data = response.json()
    except requests.exceptions.HTTPError as e:
        frappe.throw(e.response.text )
    except Exception as e:
        frappe.throw("Failed to connect to 4Jawaly API.")

    if response.status_code != 200:
        frappe.throw(f"API Error {response.status_code}: {data.get('message')}")

    # Look for the specific template by name
    for template in data.get("paginate", {}).get("data", []):
        if template.get("name") == template_name:
            return {
                "id": template.get("id"),
                "name": template.get("name"),
                "components": template.get("components"),
                "category": template.get("category"),
                "status": template.get("status"),
                "language": template.get("language"),
                "namespace": template.get("namespace"),
                "waba_account_id": template.get("waba_account_id"),
            }

    frappe.throw(f"Template '{template_name}' not found.")

@frappe.whitelist()
def send_message(jawaly_message_name):
    if not jawaly_message_name:
        frappe.throw(_("Jawaly Message is required."))

    settings = frappe.get_single("Jawaly Settings")

    if not (settings.api_key and settings.api_secret and settings.whatsapp_number_id and settings.base_url):
        frappe.throw("Missing API Key, Secret, WhatsApp Number ID, or Base URL in Jawaly Settings.")

    if not (settings.language_policy):
        frappe.throw("Missing Language Policy in Jawaly Settings.")

    jawaly_message = frappe.get_doc("Jawaly Message", jawaly_message_name)
    
    if not jawaly_message:
        frappe.throw(_("Jawaly Message not found."))

    template = frappe.get_doc("Jawaly Template", jawaly_message.jawaly_template)

    url = f"{settings.base_url}whatsapp/{settings.whatsapp_number_id}"

    params = []
    header_params = []
    body_params = []

    for variable in jawaly_message.variables:
        value = variable.default_value or ""

        if template.reference_doctype and jawaly_message.reference_name and variable.field_name:
            doc = frappe.get_doc(template.reference_doctype, jawaly_message.reference_name)
            value = doc.get(variable.field_name)

        param = {
            "type": "text",
            "text": str(value)
        }

        if variable.variable_type == "Header" and template.header_type == "TEXT":
            header_params.append(param)
        elif variable.variable_type == "Body":
            body_params.append(param)

    if header_params:
        params.append({
            "type": "header",
            "parameters": header_params
        })

    if template.header_type == "IMAGE":
        image_param = {
            "type": "header",
            "parameters": [{
                "type": "image",
                "image": {
                    "link": get_url(template.header_image) 
                }
            }]
        }
        
        params.append(image_param)     

    if body_params:
        params.append({
            "type": "body",
            "parameters": body_params
        }) 

    payload = {
        "path": "message/template",
        "params": {
            "phone": jawaly_message.send_to,
            "template": template.template,
            "language": {
                "policy": settings.language_policy,
                "code": template.template_language or settings.language_code,
            },
            "namespace": template.template_namespace,
            "params": params
        }
    }

    try:
        response = requests.post(
            url,
            	auth=(settings.api_key, settings.get_password('api_secret')),
            	headers={"Accept": "application/json"},
            	json=payload 
        	)
        
        response.raise_for_status()
			
        data = response.json()
    except requests.exceptions.HTTPError as e:
        jawaly_message.status = "Rejected"
        jawaly_message.save()        
        return {
            "request_code": e.response.status_code,
            "bad_request": json.loads(e.response.text)
        }
    except Exception as e:
        jawaly_message.status = "Rejected"
        jawaly_message.save()        
        frappe.throw("Failed to connect to 4Jawaly API.")

    if response.status_code != 200:
        frappe.throw(f"API Error {response.status_code}: {data.get('message')}")
    
    jawaly_message.status = "Sent"
    jawaly_message.save()

    return data
    