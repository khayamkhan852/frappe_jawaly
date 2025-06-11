// Copyright (c) 2025, khayam khan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Jawaly Message", {
	refresh(frm) {
		if (frm.doc.status !== 'Sent') {
			frm.add_custom_button(__('Send Now'), () => {
				let loading = frappe.show_alert({
					message: __("Sending Message..."),
					indicator: 'green'
				}, 10);

				frappe.call({
					method: "frappe_jawaly.apis.jawaly_api.send_message",
					args: {
						jawaly_message_name: frm.doc.name,
					},
					callback: function (response) {
						loading.hide();

						if (response.message && response.message.sent === true) {
							frappe.show_alert({ message: __("Message sent successfully!"), indicator: "green" });
							frm.set_value('status', 'Sent');
						}

						if (response.message.request_code && response.message.bad_request) {
    						const error = response.message.bad_request.e?.error || {};
    						message = error.error_data?.details || error.message || 'Unknown error occurred';

							frappe.msgprint(message || __('Message could not be sent.'));

							frm.set_value('status', 'Rejected');
						}

						if (response.message && response.message.sent === false) {
							if (response.message.e.error.details) {
								frappe.msgprint(response.message.e.error.details || __('Message could not be sent.'));
							}

							frm.set_value('status', 'Rejected');
						}

						frm.save();

					},
					error: function () {
						loading.hide();
					}
				});
			});			
		}

	},	
    jawaly_template: function (frm) {
		frappe.db.get_doc('Jawaly Template', frm.doc.jawaly_template).then(template => {
			frm.set_value("body_text", template.body_text);
			frm.set_value("header_text", template.header_text);

			frm.clear_table('variables');
					
			(template.variables || []).forEach(v => {
				frm.add_child('variables', {
					variable: v.variable,
					variable_type: v.variable_type,
					reference_doctype: v.reference_doctype,
					field_name: v.field_name,
					default_value: v.default_value,
				});
			});	
			
			frm.refresh_field('variables');
		});
    },
});
