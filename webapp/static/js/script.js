// File Upload
// 



// TODO LIST
// Change file search from only image to all files
// Fix csrf post


$("#file-drag").click(function () {
	$("#file-upload").click();
  });
  $("#optionsform button").click(function () {
	$(this).toggleClass("disable");
	if($(this).hasClass("change_text_disable")){
		if ($(this).hasClass("disable")) {
			$(this).text("Disable");
			} else {
			$(this).text("Enable");
		}
	}
	
  });
  function initFileUpl() {
  
  
	var fileSelect = document.getElementById('file-upload'),
	  fileDrag = document.getElementById('file-drag'),
	  submitButton = document.getElementById('submit-button');
  
	fileSelect.addEventListener('change', fileSelectHandler, false);


	var xhr = new XMLHttpRequest();
	if (xhr.upload) {
	  // File Drop
	  fileDrag.addEventListener('dragover', fileDragHover, false);
	  fileDrag.addEventListener('dragleave', fileDragHover, false);
	  fileDrag.addEventListener('drop', fileSelectHandler, false);
	}
  }
  
  function fileDragHover(e) {
	var fileDrag = document.getElementById('file-drag');
  
	e.stopPropagation();
	e.preventDefault();
  
	fileDrag.className = (e.type === 'dragover' ? 'hover' : 'modal-body file-upload');
  }
  
  function fileSelectHandler(e) {
	// Fetch FileList object
	var files = e.target.files || e.dataTransfer.files;
  
	// Cancel event and hover styling
	fileDragHover(e);
  
	// Process all File objects
	for (var i = 0, f; f = files[i]; i++) {
	  parseFile(f);
	}
  }
  
  // Output
  function output(msg) {
	// Response
	var m = document.getElementById('messages');
	m.innerHTML = msg;
  }
  
  function parseFile(file) {
	output(
	  '<strong>' + encodeURI(file.name) + '</strong>'
	);
  
	// var fileType = file.type;
	// console.log(fileType);
	var imageName = file.name;
  
	var isGood = (/\.(?=jpeg|png|bmp|gif|tiff|jpg|jfif|jpe|tif)/gi).test(imageName);
	
	document.getElementById('start').classList.add("hidden");
	document.getElementById('response').classList.remove("hidden");
	document.getElementById('notimage').classList.add("hidden");
	
	  // Thumbnail Preview
	if (isGood) {
		document.getElementById('file-image').classList.remove("hidden");
	  document.getElementById('file-image').src = URL.createObjectURL(file);
	}
  }
  
  function setProgressMaxValue(e) {
	var pBar = document.getElementById('file-progress');
  
	if (e.lengthComputable) {
	  pBar.max = e.total;
	}
  }
  
  function updateFileProgress(e) {
	var pBar = document.getElementById('file-progress');
  
	if (e.lengthComputable) {
	  pBar.value = e.loaded;
	}
  }
  
  function uploadFile(file) {
	var xhr = new XMLHttpRequest(),
	  fileInput = document.getElementById('class-roster-file'),
	  pBar = document.getElementById('file-progress');
	if (xhr.upload) {
	  // Progress bar
	  pBar.style.display = 'inline';
	  xhr.upload.addEventListener('loadstart', setProgressMaxValue, false);
	  xhr.upload.addEventListener('progress', updateFileProgress, false);
  
	  // File received / failed
	  xhr.onreadystatechange = function (e) {
		if (xhr.readyState == 4) {  // when upload is ok
		  console.log(xhr.response)
		  response = JSON.parse(xhr.response);
		  if ("File" in response){
			document.location = "/"+response['File'];
		  }
		  else if ("Error" in response){
			$("#error").text(response["Error"]);
			$("#error").slideDown();
		  }
		}
	  };
	  
	  // Start upload
	  xhr.open('POST', '/upload', true);
	  //xhr.setRequestHeader('Content-Type', 'multipart/form-data');
	  var formData = new FormData();
	  formData.append("file", file);
	  formData.append("crypto", !$("#btn_crypto").hasClass("disable"));
	  formData.append("stega", !$("#btn_stega").hasClass("disable"));
	  formData.append("btn_forensic", !$("#btn_forensic").hasClass("disable"));
	  formData.append("web", !$("#btn_web").hasClass("disable"));
	  formData.append("verbose", !$("#verbose_input").hasClass("disable"));
	  formData.append("format", $("input[name=flag_format_input]").val());
	  xhr.send(formData);
	  
	}
  }

  // Check for the various File API support.
  if (window.File && window.FileList && window.FileReader) {
	initFileUpl();
  } else {
	document.getElementById('file-drag').style.display = 'none';
  }
  
  $("#upload_button").click(function(){
	//alert("ok");
	uploadFile($("#file-upload").prop('files')[0]);
	$("#file-upload").prop('files')[0]=null;
	document.getElementById("file-upload-form").reset();
  });