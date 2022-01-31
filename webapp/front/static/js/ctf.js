$("#user_check").click(function(){
	uploadCTF();
	document.getElementById("Loginform").reset();
	
	
});

$(".btn_disable").click(function () {
	if(!$(this).hasClass("btn_liens")){
		$(this).toggleClass("disable");
		if($(this).hasClass("change_text_disable")){
			if ($(this).hasClass("disable")) {
				$(this).text("Disable");
				} else {
				$(this).text("Enable");
			}
		}
	}
});

$("#btn_lien_page_chall").click(function(){
	location.href = "/";
  });
  $("#btn_lien_page_ctf").click(function(){
	location.href += "";
});


function uploadCTF() {
  var xhr = new XMLHttpRequest();

  
  // Start upload
  xhr.open('POST', '/uploadCTF', true);
  //xhr.setRequestHeader('Content-Type', 'multipart/form-data');
  var formData = new FormData();
  
  formData.append("url", $("#CTF_URL").val());
  formData.append("Login", $("#Login").val());
  formData.append("Pass", $("#Password").val());
  formData.append("FlagForm", $("#flag_format_input").val());


  xhr.send(formData);
  
  xhr.onreadystatechange = function (e) {
		if (xhr.readyState == 4) { 
  console.log(xhr.response);
  response = JSON.parse(xhr.response);
  document.getElementById("output").value = response["output"];
    }}


}
