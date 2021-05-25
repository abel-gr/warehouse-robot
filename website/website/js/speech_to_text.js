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

	var ul = document.getElementById('recordingsList');
	if (ul) {
		while (ul.firstChild) {
			ul.removeChild(ul.firstChild);
	} 	}
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

	$("#recordingsList").html("");

	convertToBase64(blob);
	var url = URL.createObjectURL(blob);
	var au = document.createElement('audio');
	var li = document.createElement('li');


	console.log("blob URL:",url);

	au.controls = true;
	au.src = url;
	au.setAttribute('id', 'audioSrc');
	au.style.width = "90%";

	li.style.width = "75%";

	li.appendChild(au);

	var upload = document.createElement('a');
	upload.href="#";
	upload.innerHTML = "Upload";
	upload.setAttribute('id', 'uploadButton')

	var remove = document.createElement('a');
	remove.href="#";
	remove.innerHTML = "Cancel";
	remove.setAttribute('id', 'removeButton')
	remove.style.color = 'red';

	li.appendChild(upload);
	li.appendChild(document.createTextNode (" "))
	li.appendChild(remove);
	recordingsList.appendChild(li);

	document.getElementById("uploadButton").addEventListener("click", function(){
		sendOrder();
	},);

	document.getElementById("removeButton").addEventListener("click", function(){
		li.parentNode.removeChild(li);
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
	const responseSST = await fetch(urlSTT, {
		method: 'POST',
		body: JSON.stringify(reqSTT),
		headers: {
			'Content-Type': 'application/json',
			'Accept': 'application/json'
		}
	}).then(resSTT => resSTT.text());

	var STTmsg = 'You said: ' + responseSST ;
	window.alert(STTmsg);

	const urlAI = 'https://europe-west1-earnest-coder-312920.cloudfunctions.net/Vertex-AI';	//ESTA ES LA URL DE LA API
    const reqAI = {																			//ESTE ES EL JSON QUE CONTIENE LO QUE QUIERAS PASAR A LA API
        text: responseSST,
    }
    const responseAI = await fetch(urlAI, {												//CONEXION FETCH PARA HACER EL POST
		method: 'POST',
		body: JSON.stringify(reqAI),
		headers: {
			'Content-Type': 'application/json',
			'Accept': 'application/json'
		}
	}).then(resAI => resAI.json());
    console.log(responseAI); 																//AQUI TE LLEGARA TU RESPUESTA

	saveVoiceOrderToDB(responseAI.shelf, responseAI.product_quantity);
}