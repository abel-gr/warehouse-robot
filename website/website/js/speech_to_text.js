URL = window.URL || window.webkitURL;

var gumStream;
var rec;
var input;
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext;
var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var base64AudioFormat;
var language = "en-US";

recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);

function startRecording() {
	console.log("Record button clicked");

    var constraints = { audio: true, video:false }

	recordButton.disabled = true;
	stopButton.disabled = false;
	console.log("Enabled stop button");

	navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
		console.log("getUserMedia() success, stream created, initializing Recorder.js ...");
		audioContext = new AudioContext();
		gumStream = stream;
		input = audioContext.createMediaStreamSource(stream);
		rec = new Recorder(input,{numChannels:1})
		rec.record()
		console.log("Recording started");

	}).catch(function(err) {
		console.log("error");
    	recordButton.disabled = false;
    	stopButton.disabled = true;
	});
}

function stopRecording() {
	console.log("stopButton clicked");
	stopButton.disabled = true;
	recordButton.disabled = false;
	rec.stop();
	gumStream.getAudioTracks()[0].stop();
	rec.exportWAV(createUploadBtn);
}

function convertToBase64(blob){
    var reader = new FileReader();
    reader.readAsDataURL(blob);
    reader.onloadend = function() {
        base64data = reader.result.split(',')[1];
        console.log(base64data);
        base64AudioFormat=base64data;
        console.log("base 64 data:",base64AudioFormat);
    }
}

function createUploadBtn(blob) {
	convertToBase64(blob);
	var url = URL.createObjectURL(blob);
	var au = document.createElement('audio');
	var li = document.createElement('li');

	console.log("blob URL:",url);

	au.controls = true;
	au.src = url;
	li.appendChild(au);

	var upload = document.createElement('a');
	upload.href="#";
	upload.innerHTML = "Upload";
	upload.setAttribute('id', 'uploadButton')

	li.appendChild(upload);
	recordingsList.appendChild(li);

	document.getElementById("uploadButton").addEventListener("click", function(){
		sendOrder();
	},);
}


async function sendOrder() {
    var selectedLan = document.getElementById("language-selection");
    language = selectedLan.value;
    console.log("selected_language:",language);

    const urlSTT = 'https://europe-west1-earnest-coder-312920.cloudfunctions.net/Speech-to-Text';
    const reqSTT = {
        audio: base64AudioFormat,
        lan: language
    }
	const response = await fetch(urlSTT, {
		method: 'POST',
		body: JSON.stringify(reqSTT),
		headers: {
			'Content-Type': 'application/json',
			'Accept': 'application/json'
		}
	}).then(resSTT => resSTT.text());
    console.log(response); //AQUI TIENES EL RESULTADO DE SPEECH TO TEXT


	//AQUI PUEDES HACER OTRA LLAMADA PARA EL VERTEXIA
}