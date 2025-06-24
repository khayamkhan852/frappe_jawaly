// Copyright (c) 2025, khayam khan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Create Jawaly Template", {
    refresh: function(frm) {
		if (frm.doc.status !== 'Sent') {
			frm.add_custom_button(__('Send To 4Jawaly Now'), () => {
				let loading = frappe.show_alert({
					message: __("Sending Message..."),
					indicator: 'green'
				}, 10);

				frappe.call({
					method: "frappe_jawaly.apis.jawaly_api.send_template_to_jawaly",
					args: {
						create_jawaly_template_name: frm.doc.name,
					},
					callback: function (response) {
						loading.hide();

						if (response.message && response.message.sent === true) {
							frappe.show_alert({ message: __("Template Sent Successfully!"), indicator: "green" });
						}

                        console.log(response.message);

						if (response.message.request_code && response.message.bad_request) {
                            let bad_requestt = response.message.bad_request;
    						const error = bad_requestt.e?.error || {};
    						message = error.error_data?.details || error.message || bad_requestt.e.meta.developer_message || 'Unknown error occurred';

							frappe.msgprint(message || __('Template could not be sent.'));
						}

						if (response.message && response.message.sent === false) {
							if (response.message.e.error.details) {
								frappe.msgprint(response.message.e.error.details || __('Template could not be sent.'));
							}
						}
						frm.reload_doc()
					},
					error: function () {
						loading.hide();
						frm.reload_doc()
					}
				});
			});			
		}        
    },        
    template_name: function(frm) {
        frm.doc.template_name = frm.doc.template_name.replace(/ /g, '_').toLowerCase();
        frm.refresh_field('template_name');
    },
    header_text: function(frm) {
        if (frm.doc.header_text && frm.doc.header_text.length > 60) {
            frm.doc.header_text = frm.doc.header_text.substring(0, 60);
            frm.refresh_field('header_text');
        }
    },
    body_message: function(frm) {
        if (frm.doc.body_message.length > 1024) {
            frm.doc.body_message = frm.doc.body_message.substring(0, 1024);
            frm.refresh_field('body_message');
        }
    },
    footer_text: function(frm) {
        if (frm.doc.footer_text && frm.doc.footer_text.length > 60) {
            frm.doc.footer_text = frm.doc.footer_text.substring(0, 60);
            frm.refresh_field('footer_text');
        }
    },
    phone_button_text: function(frm) {
        if (frm.doc.phone_button_text && frm.doc.phone_button_text.length > 25) {
            frm.doc.phone_button_text = frm.doc.phone_button_text.substring(0, 25);
            frm.refresh_field('phone_button_text');
        }
    },
    button_one_text: function(frm) {
        if (frm.doc.button_one_text && frm.doc.button_one_text.length > 25) {
            frm.doc.button_one_text = frm.doc.button_one_text.substring(0, 25);
            frm.refresh_field('button_one_text');
        }
    },
    button_two_text: function(frm) {
        if (frm.doc.button_two_text && frm.doc.button_two_text.length > 25) {
            frm.doc.button_two_text = frm.doc.button_two_text.substring(0, 25);
            frm.refresh_field('button_two_text');
        }
    }        

});

frappe.ui.form.on("Jawaly Template Reply Button", {
    reply_button_text: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.reply_button_text && row.reply_button_text.length > 25) {
            row.reply_button_text = row.reply_button_text.substring(0, 25);
            frm.refresh_field("reply_button_text");
        }
    },
    reply_buttons_add: function(frm) {
        if (frm.doc.reply_buttons.length >= 7) {
            frm.set_df_property('reply_buttons', 'cannot_add_rows', true);
        }
    },
    reply_buttons_remove: function(frm) {
        if (frm.doc.reply_buttons.length < 7) {
            frm.set_df_property('reply_buttons', 'cannot_add_rows', false);
        }
    }    
});

frappe.ui.form.on("Create Jawaly Template Variable", {
    header_variables_add: function(frm) {
        if (frm.doc.header_variables.length >= 1) {
            frm.set_df_property('header_variables', 'cannot_add_rows', true);
        }
    },
    header_variables_remove: function(frm) {
        if (frm.doc.header_variables.length < 1) {
            frm.set_df_property('header_variables', 'cannot_add_rows', false);
        }
    }    
});
