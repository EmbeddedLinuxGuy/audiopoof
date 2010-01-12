
var audiopoof = [];
audiopoof.SERVICES = true;

var audiopoofWS = {};
	audiopoofWS.URL = "/services";
    //audiopoofWS.serviceAccountURL = "/services/user/account";
    //audiopoofWS.serviceMessagingStationURL = "/services/messaging/station";
    //audiopoofWS.serviceMessagingUserURL = "/services/messaging/user";
	//audiopoofWS.serviceMessagingStationURL = "/php/getStationMessagesSimulator.php";
	//audiopoofWS.serviceNewMessagingStationURL = "/php/getNewStationMessagesSimulator.php";
	//audiopoofWS.serviceSubmitMessagingStationURL = "/php/submitStationMessageSimulator.php";
    //audiopoofWS.serviceSubmitMessagingStationURL = "/services/messaging/station";
    //audiopoofWS.serviceNewMessagingStationURL = "/services/messaging/station";
    //audiopoofWS.serviceContentRetrieveURL     = "/services/content/retrieve";
    //audiopoofWS.serviceContentUploadURL       = "/services/content/upload";
    //audiopoofWS.serviceContentStationURL       = "/services/content/station";
	//audiopoofWS.serviceContentPhotoURL		= "/services/user/upload/photo";
    //audiopoofWS.serviceVoteURL       = "/services/gaming/vote";
	//audiopoofWS.serviceRocketURL       = "/services/gaming/rocket";
	//audiopoofWS.serviceBombURL       = "/services/gaming/bomb";
    //audiopoofWS.serviceDeviceURL       = "/services/station/device";


// Common function used by all pages that wish to communicate with
// the Jelli web services. 
//
// Pass:
//
// package    : which web service package contains the action processor for the requested action.
// json-data  : data object (which minimally needs to contain the action property).
// successsCB : this callback is called on success and will be passed the result reponse object that 
//              comes back from the server.
// failureCB  : called when either the server fails or the Ajax call failes.  Any Ajax errors will be 
//              converted into a classic "unexpected error" as the client can't do anything different 
//              between Ajax or server errors (i.e. it's an 'oops! page.').
// 
audiopoofWS.serviceCall = function(thisPackage, json_data, successCB, failureCB) {

   //jelli.DEBUGGING = true;

   var url = "";
    
   // Map the package to it's corresponding service URL.
   //
   switch (thisPackage) {

     	case "audiopoof":
		   url = audiopoofWS.URL;
		break;


		
	//	case "device":
	//		url =	audiopoofWS.serviceDeviceURL;
	//	break;

		default:
		//	alert("audiopoofWS: no URL found for package: " + package); // Should never happen!
		return;
   }


   json_data["valid"] = undefined; // Remove this temporary property...

   var json_text = JSON.stringify(json_data);

	if (audiopoof.SERVICES) {
	   trace("Request Object: " + json_text);

	var xmr = $.post(url, { data: json_text },
	  	function(data, stat) {
	         //trace("Ajax success callback: " + xmr.responseText);
	         if (data.result) successCB(data);
	         else             failureCB(data);
         
	        // jelli.DEBUGGING = true;
	      }, "json");


/*
	   var xmr = $.ajax({
	      url     : url, 
	      data    : 'data='+json_text,
	      type    : "POST",
	      dataType: "json",

	      success: function(data, stat) {
	         //trace("Ajax success callback: " + xmr.responseText);
	         if (data.result) successCB(data);
	         else             failureCB(data);
         
	        // jelli.DEBUGGING = true;
	      },
	      error: function(xhr, stat, err) {
	         trace("AJAX error callback: " + stat + " - response text : " + xhr.responseText);

	         var syntheticResponse = {result: false, reasonMap: {error:"unexpectedError"}};
	         failureCB(syntheticResponse);

	         //jelli.DEBUGGING = true;
	      }
	   });
*/
	}
}
