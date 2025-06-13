$(document).on('app_ready', function () {
	// waiting for page to load completely
	frappe.router.on("change", () => {
		var route = frappe.get_route();
		if (route && route[0] == "Form") {
			frappe.ui.form.on(route[1], {
				refresh: function (frm) {
					frm.page.add_menu_item(__("Send Through Jawaly Whatsapp"), function () {
						var reference_doctype = frm.doctype;
						var reference_name = frm.docname;
						var dialog = new frappe.ui.Dialog({
							'fields': [
								{ 'fieldname': 'ht', 'fieldtype': 'HTML' },
								{ 'label': 'Select Jawaly Template', 'fieldname': 'jawaly_template', 'reqd': 1, 'fieldtype': 'Link', 'options': 'Jawaly Template' },
                                { "label": "Contact", "fieldname": "contact", "fieldtype": "Link", "link_filters": "[[\"Contact\",\"phone\",\"is\",\"set\"]]", "options": "Contact", change() {
                                    let contact_name = dialog.get_value('contact');
                                    if (contact_name) {
                                        frappe.call({
                                            method: 'frappe.client.get_value',
                                            args: {
                                                doctype: 'Contact',
                                                filters: { name: contact_name },
                                                fieldname: ['phone']
                                            },
                                            callback: function (r) {
                                                if (r.message) {
                                                    dialog.set_value('send_to', r.message.phone);
                                                } else {
                                                    dialog.set_value('send_to', '');
                                                    frappe.msgprint('phone not found for the selected contact.');
                                                }
                                            }
                                        });
                                    } else {
                                        d.set_value('send_to', '');
                                    }
                                }},
                                { 'label': 'Send To', 'fieldname': 'send_to', 'reqd': 1, 'fieldtype': 'Data' },

                            ],
							'primary_action_label': 'Send Message',
							'title': 'Send Jawaly Whatsapp Message',
							primary_action: function () {
								var values = dialog.get_values();
								if (values) {
									frappe.call({
										method: "frappe_jawaly.frappe_jawaly.doctype.jawaly_message.jawaly_message.save_jawaly_message",
										args: {
											template: values.jawaly_template,
                                            send_to: values.send_to,
											contact: values.contact,
											reference_doctype: reference_doctype,
											reference_name: reference_name
										},
										freeze: true,
                                        async: false,
										callback: (response) => {
                                            if (response.message && response.message.sent === true) {
                                                frappe.show_alert({ message: __("Message sent successfully!"), indicator: "green" });
                                            }

                                            if (response.message.request_code && response.message.bad_request) {
                                                const error = response.message.bad_request.e?.error || {};
                                                message = error.error_data?.details || error.message || 'Unknown error occurred';

                                                frappe.msgprint(message || __('Message could not be sent.'));
                                            }

                                            if (response.message && response.message.sent === false) {
                                                if (response.message.e.error.details) {
                                                    frappe.msgprint(response.message.e.error.details || __('Message could not be sent.'));
                                                }
                                            } 

                                            dialog.hide();
										},
                                        error: function () {
                                            frappe.msgprint(__('Error sending message.'));
                                            dialog.hide();
                                        }
									});
								}

							},
							no_submit_on_enter: true,
						});

                        let jawaly_template = dialog.fields_dict.jawaly_template;
	                    if (jawaly_template) {
	                        jawaly_template.get_query = function() {
	                            return {
	                                filters: { "reference_doctype": frm.doc.doctype },
	                                doctype: "Jawaly Template"
	                            };
	                        };
	                        jawaly_template.refresh();
	                    }
                        dialog.show();
					});
				}
			});
		};
	})
});