// Copyright (c) 2025, khayam khan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Jawaly Template", {
	refresh(frm) {
        frm.add_custom_button(__('Fetch Jawaly Templates'), () => {
            let loading = frappe.show_alert({
                message: __("Fetching templates..."),
                indicator: 'green'
            }, 10);

            frappe.call({
                method: "frappe_jawaly.apis.jawaly_api.get_templates",
                callback: function (response) {
                    loading.hide();
                    if (response.message && response.message.length > 0) {
                        frm.set_df_property('jawaly_template_name', 'options', response.message);
                        frm.refresh_field('jawaly_template_name');
                        frappe.show_alert({ message: __("Templates loaded"), indicator: "green" });
                    } else {
                        frappe.msgprint(__('No templates found.'));
                    }
                },
                error: function () {
                    loading.hide();
                }
            });
        });
	},

    jawaly_template_name(frm) {
        if (frm.doc.jawaly_template_name) {
            let loading = frappe.show_alert({
                message: __("Fetching Template Details..."),
                indicator: 'green'
            }, 10);

            let body_text_v = '';
            let header_text_v = '';

            frappe.call({
                method: "frappe_jawaly.apis.jawaly_api.get_template_by_name",
                args: {
                    template_name: frm.doc.jawaly_template_name
                },
                async: false,
                callback: function (response) {
                    loading.hide();
                    
                    if (response.message) {
                        frm.set_value('template', response.message.name || '');
                        frm.set_value('category', response.message.category || '');
                        frm.set_value('template_id', response.message.id || '');
                        frm.set_value('jawaly_template_status', response.message.status || '');
                        frm.set_value('template_language', response.message.language || '');
                        frm.set_value('template_namespace', response.message.namespace || '');
                        frm.set_value('waba_account_id', response.message.waba_account_id || '');

                        response.message.components.forEach(component => {
                            if (component.type === 'BODY') {
                                body_text_v = component.text;
                                frm.set_value('body_text', body_text_v || '');
                            }
                            
                            if (component.type === 'HEADER') {
                                frm.set_value('header_type', component.format || '');
                                if (component.format !== 'IMAGE') {
                                    header_text_v = component.text;
                                    frm.set_value('header_text', header_text_v || '');
                                }
                            }

                        });

                        frm.refresh_field('template');
                        frm.refresh_field('category');
                        frm.refresh_field('template_id');
                        frm.refresh_field('jawaly_template_status');
                        frm.refresh_field('template_language');
                        frm.refresh_field('template_namespace');
                        frm.refresh_field('waba_account_id');
                        frm.refresh_field('header_type');
                        frm.refresh_field('body_text');
                        frm.refresh_field('header_text');
                        
                        frappe.show_alert({ message: __("Template details loaded"), indicator: "green" });
                    } else {
                        frappe.msgprint(__('Template not found.'));
                    }

                },
                error: function () {
                    loading.hide();
                    frappe.msgprint(__('Error fetching template details.'));
                }
            });

            frm.clear_table('variables');

            frappe.call({
				method: "frappe_jawaly.frappe_jawaly.doctype.jawaly_template.jawaly_template.get_variables",
				args: {
					body_text: body_text_v,
					header_text: header_text_v
				},
                async: false,
				callback: function (r) {
					if (!r.message) return;

					const { body_variables, header_variables } = r.message;

					(header_variables || []).forEach(v => {
						frm.add_child('variables', {
							variable: v,
							variable_type: 'Header'
						});
					});					

					(body_variables || []).forEach(v => {
						frm.add_child('variables', {
							variable: v,
							variable_type: 'Body'
						});
					});

					frm.refresh_field('variables');
				},
			});

        }
    }

});
