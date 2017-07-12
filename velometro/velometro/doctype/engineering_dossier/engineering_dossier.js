// Copyright (c) 2017, Velometro Mobility Inc and contributors
// For license information, please see license.txt

frappe.ui.form.on("Engineering Dossier", {
	refresh: function(frm) {
		// Only show the correct phases
		frm.toggle_display("top_level_design", false);
		frm.toggle_display("detailed_design", false);
		frm.toggle_display("drawing_release", false);
		frm.toggle_display("prototype_manufacturing", false);
		frm.toggle_display("production_release", false);
		switch(frm.doc.phase)
		{
			case "Production Release":
				frm.toggle_display("production_release", true);
			case "Prototyping":
				frm.toggle_display("prototype_manufacturing", true);
			case "Drawing Review & Release":
				frm.toggle_display("drawing_release", true);
			case "Detailed Design":
				frm.toggle_display("detailed_design", true);
			case "Top Level Design":
				frm.toggle_display("top_level_design", true);
		}
	},
	onload_post_render:function(frm){
		var section_list = ["Conceptual Design", "Top Level Design", "Detailed Design", "Drawing Release", "Prototyping", "Production Release"]
		var signoff_list = ["concept_so_sb", "tl_so_sb", "dd_so_sb", "dr_so_sb", "proto_so_sb", "prod_so_sb"]
		for (var i = 0; i < section_list.length;i++)
		{
			var section_head = $('.section-head').find("a").filter(function(){ return $(this).text() === section_list[i] ;}).parent()
			section_head.on("click", function(){

					var text = this.textContent;
					var index = section_list.indexOf(text);
					if ($(this).hasClass("collapsed")){
						frm.toggle_display(signoff_list[index],false);
					}else{
						frm.toggle_display(signoff_list[index],true);
					}
				
			})
		}
	},
	concept_sign_off: function(frm)
	{
		frm.set_value("concept_date",frappe.datetime.get_today());
	}

});
