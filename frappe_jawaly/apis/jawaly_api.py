import frappe
from frappe import _
import requests
import json
from frappe.utils import get_url

@frappe.whitelist()
def fetch_account_details():
    settings = frappe.get_single("Jawaly Settings")

    if not (settings.api_key and settings.api_secret and settings.base_url):
        frappe.throw("Missing API Key, Secret, WhatsApp Number ID, or Base URL in Jawaly Settings.")

    url = f"{settings.base_url}/list-projects"

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

    return data

@frappe.whitelist()
def get_templates():
    settings = frappe.get_single("Jawaly Settings")

    if not (settings.api_key and settings.api_secret and settings.whatsapp_number_id and settings.base_url):
        frappe.throw("Missing API Key, Secret, WhatsApp Number ID, or Base URL in Jawaly Settings.")

    base_url = f"{settings.base_url.rstrip('/')}/templates/{settings.whatsapp_number_id}"
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

    url = f"{settings.base_url}/templates/{settings.whatsapp_number_id}?name={template_name}"

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

    url = f"{settings.base_url}/{settings.whatsapp_number_id}"

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
                "code": template.template_language or 'en',
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
    
@frappe.whitelist()    
def send_template_to_jawaly(create_jawaly_template_name):
    if not create_jawaly_template_name:
        frappe.throw(_("Jawaly Template is required."))

    settings = frappe.get_single("Jawaly Settings")

    if not (settings.api_key and settings.api_secret and settings.whatsapp_number_id and settings.base_url):
        frappe.throw("Missing API Key, Secret, WhatsApp Number ID, or Base URL in Jawaly Settings.")
    
    create_jawaly_template = frappe.get_doc("Create Jawaly Template", create_jawaly_template_name)
    
    if not create_jawaly_template:
        frappe.throw(_("Jawaly Template not found."))

    url = f"{settings.base_url}/{settings.whatsapp_number_id}"

    components = []

    # Body component
    if not create_jawaly_template.body_message:
        frappe.throw(_("Body message is required."))

    body_component = {
        "type": "BODY",
        "text": create_jawaly_template.body_message or "this is test body message"
    }

    if create_jawaly_template.body_variable_values:
        example_values = [[row.example_value for row in create_jawaly_template.body_variable_values]]

        body_component["example"] = {
            "body_text": example_values
        } 

    components.append(body_component)

    # Header component
    if create_jawaly_template.header_type != "WITHOUT":
        header_component = {
            "type": "HEADER",
            "format": create_jawaly_template.header_type,
        }

        if create_jawaly_template.header_type == "TEXT":
            header_component["text"] = create_jawaly_template.header_text or "this is test header text"
            if create_jawaly_template.header_variables:
                header_example_values = [row.example_value for row in create_jawaly_template.header_variables]
                header_component["example"] = {
                    "header_text": header_example_values
                }
        else:
            header_component["example"] = {
                "header_handle": [get_url(create_jawaly_template.header_attachement)]
            }    

        components.append(header_component)

    # Footer component 
    if create_jawaly_template.footer_text:
        footer_component = {
            "type": "FOOTER",
            "text": create_jawaly_template.footer_text or "this is test footer message"
        }
        components.append(footer_component)

    # buttons component
    if create_jawaly_template.reply_buttons or create_jawaly_template.phone_button_text or create_jawaly_template.button_one_text or create_jawaly_template.button_two_text:
        buttons = []

        if create_jawaly_template.reply_buttons:
            for reply_button in create_jawaly_template.reply_buttons:
                buttons.append({
                    "type": "QUICK_REPLY",
                    "text": reply_button.reply_button_text or "Reply Button"
                })

        if create_jawaly_template.phone_button_text and create_jawaly_template.phone_number:
            buttons.append({
                "type": "PHONE_NUMBER",
                "text": create_jawaly_template.phone_button_text or "Call Us",
                "phone_number": create_jawaly_template.phone_number
            })

        if create_jawaly_template.button_one_text and create_jawaly_template.button_one_url:
            if not create_jawaly_template.button_one_url.startswith("http"):
                frappe.throw(_("Button One URL must start with 'http://' or 'https://'."))

            url_one_component = {
                "type": "URL",
                "text": create_jawaly_template.button_one_text or "URL Button",
                "url": create_jawaly_template.button_one_url
            }

            if create_jawaly_template.url_one_example:
                if not create_jawaly_template.url_one_example.startswith("http"):
                    frappe.throw(_("Button One Example URL must start with 'http://' or 'https://'."))
                url_one_component["example"] = [create_jawaly_template.url_one_example]
            
            buttons.append(url_one_component)

        if create_jawaly_template.button_two_text and create_jawaly_template.button_two_url:
            if not create_jawaly_template.button_two_url.startswith("http"):
                frappe.throw(_("Button Two URL must start with 'http://' or 'https://'."))

            url_two_component = {
                "type": "URL",
                "text": create_jawaly_template.button_two_text or "URL Button",
                "url": create_jawaly_template.button_two_url
            }

            if create_jawaly_template.url_two_example:
                if not create_jawaly_template.url_two_example.startswith("http"):
                    frappe.throw(_("Button One Example URL must start with 'http://' or 'https://'."))
                url_two_component["example"] = [create_jawaly_template.url_two_example]
            
            buttons.append(url_two_component)

        if buttons:
            buttons_component = {
               "type": "BUTTONS",
               "buttons": buttons
            }

            components.append(buttons_component)

    params = {
        "name": create_jawaly_template.template_name,
        "category": create_jawaly_template.category,
        "language": create_jawaly_template.language_code or "en",
        "components": components
    }

    if create_jawaly_template.category == "MARKETING":
        params["marketing_template_type"] = create_jawaly_template.marketing_template_type    

    payload = {
        "path": "templates/add",
        "params": params
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
        create_jawaly_template.status = "Rejected"
        create_jawaly_template.save()       
        return {
            "request_code": e.response.status_code,
            "bad_request": json.loads(e.response.text)
        }
    except Exception as e:
        create_jawaly_template.status = "Rejected"
        create_jawaly_template.save()        
        frappe.throw("Failed to connect to 4Jawaly API.")

    if response.status_code != 200:
        frappe.throw(f"API Error {response.status_code}: {data.get('message')}")
    
    create_jawaly_template.status = "Sent"
    create_jawaly_template.save()

    return data