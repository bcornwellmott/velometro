// Copyright (c) 2017, Velometro Mobility Inc and contributors
// For license information, please see license.txt
$.getScript("https://apis.google.com/js/api.js?onload=loadPicker", function() {
   //alert("Script loaded but not necessarily executed.");
});
$.getScript("https://apis.google.com/js/client.js", function() {
   //alert("Script loaded but not necessarily executed.");
});

frappe.ui.form.on('Procedure', {
	onload: function(frm) {

	},
	refresh: function(frm) {
		if (frm.doc.docstatus == 0) {
			frm.add_custom_button(__('Load from Google Drive'), function(doc){
				loadPicker();
			}, __('Document'));
			frm.add_custom_button(__('Manual Entry'), function(doc){
				var cbs = [];
				cbs.push({fieldname: 'content', label: __('HTML Content'),fieldtype: 'Long Text', 'default': frm.doc.content});
				frappe.prompt(cbs,
					function (values) {	
						frm.doc.content = values['content'];			
						frm.save();
						return;
					},					
				 __('Manual Entry'),__('Document'));
			}, __('Document'));
			
			
		}
		$(cur_frm.fields_dict['document'].wrapper).html(frm.doc.content);
	}
});

// The Browser API key obtained from the Google API Console.
// Replace with your own Browser API key, or your own key.
var developerKey = 'AIzaSyASR3XuKYzZe123rzbJ55YpvZCACsmd15g';

// The Client ID obtained from the Google API Console. Replace with your own Client ID.
var clientId = "510637802385-n9di1epq7gkgagvhmduk0hl1ra9r4nu8.apps.googleusercontent.com"

// Replace with your own project number from console.developers.google.com.
// See "Project number" under "IAM & Admin" > "Settings"
var appId = "510637802385";

// Scope to use to access user's Drive items.
var scope = ['https://www.googleapis.com/auth/drive'];

var pickerApiLoaded = false;
var oauthToken;

// Use the Google API Loader script to load the google.picker script.
function loadPicker() {
  gapi.load('auth', {'callback': onAuthApiLoad});
  gapi.load('picker', {'callback': onPickerApiLoad});
  gapi.client.load('drive', 'v2');
}

function onAuthApiLoad() {
  window.gapi.auth.authorize(
	  {
		'client_id': clientId,
		'scope': scope,
		'immediate': false
	  },
	  handleAuthResult);
}

function onPickerApiLoad() {
  pickerApiLoaded = true;
  createPicker();
}

function handleAuthResult(authResult) {
  if (authResult && !authResult.error) {
	oauthToken = authResult.access_token;
	createPicker();
  }
}

// Create and render a Picker object for searching images.
function createPicker() {
  if (pickerApiLoaded && oauthToken) {
	var view = new google.picker.View(google.picker.ViewId.DOCS);
	view.setMimeTypes("application/vnd.google-apps.document");
	var picker = new google.picker.PickerBuilder()
		.enableFeature(google.picker.Feature.NAV_HIDDEN)
		.enableFeature(google.picker.Feature.MULTISELECT_ENABLED)
		.setAppId(appId)
		.setOAuthToken(oauthToken)
		.addView(view)
		.addView(view)
		.addView(new google.picker.DocsUploadView())
		.setDeveloperKey(developerKey)
		.setCallback(pickerCallback)
		.build();
	 picker.setVisible(true);
  }
}

// A simple callback implementation.
function pickerCallback(data) {
	if (data.action == google.picker.Action.PICKED) {
		var id= data.docs[0].id;
		var rev = 1;
		var drive = window.gapi.client.drive;

		drive.revisions.update({
			fileId: id,
			revisionId: rev  
			}, {
			published: true,
			publishAuto: true
			}).then(function() {
				debugger;
				var iframe = [
				  '<center><iframe ',
				  'src="https://docs.google.com/document/d/',
				  id,
				  '/pub?embedded=true" width="800" height="1200"></iframe></center>'
				].join('');

				cur_frm.set_value('content',iframe);
				});
	}
}
