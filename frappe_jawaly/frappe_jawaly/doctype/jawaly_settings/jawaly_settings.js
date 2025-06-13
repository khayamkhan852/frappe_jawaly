// Copyright (c) 2025, khayam khan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Jawaly Settings", {
	refresh(frm) {
        frm.add_custom_button(__('Fetch Account Details'), () => {
            let loading = frappe.show_alert({
                message: __("Fetching Details..."),
                indicator: 'green'
            }, 10);

            frappe.call({
                method: "frappe_jawaly.apis.jawaly_api.fetch_account_details",
                callback: function (response) {
                    loading.hide();
                    if (response.message) {
                        frappe.show_alert({ message: __("Account details fetched successfully!"), indicator: "green" });

                        (response.message.item.data || []).forEach(v => {
                            frm.set_value('whatsapp_number_id', v.id || '');
                            frm.set_value('whatsapp_number', v.phone || '');
                            frm.set_value('expired_at', frappe.datetime.str_to_obj(v.expired_at) || '');
					    });	

                        frm.save();
                    } else {
                        frappe.msgprint(__('No account details found.'));
                    }
                },
                error: function () {
                    loading.hide();
                    frappe.msgprint(__('Failed to fetch account details. Please check the API configuration or network.'));
                }
            });
        });
	},
});
