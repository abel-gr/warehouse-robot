// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
var firebaseConfig = {
	apiKey: "AIzaSyCf0lFsEDrCVJ69hDs0CUt1XYsAnKYmMi4",
	authDomain: "warehousewaiter.firebaseapp.com",
	databaseURL: "https://warehousewaiter-default-rtdb.europe-west1.firebasedatabase.app",
	projectId: "warehousewaiter",
	storageBucket: "warehousewaiter.appspot.com",
	messagingSenderId: "218777444604",
	appId: "1:218777444604:web:4c055bcdd83c10c9117779",
	measurementId: "G-D6L3NYX1X9"
};
// Initialize Firebase
firebase.initializeApp(firebaseConfig);
firebase.analytics();


URL = window.URL || window.webkitURL;

var gumStream;
var rec;
var input;
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext
var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");

recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);

function startRecording() {
	console.log("recordButton clicked");

    var constraints = { audio: true, video:false }

	recordButton.disabled = true;
	stopButton.disabled = false;
	console.log("enable stop");

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
	rec.exportWAV(createUploadLink);
}

function createUploadLink(blob) {

	var url = URL.createObjectURL(blob);
	var au = document.createElement('audio');
	var li = document.createElement('li');
	var link = document.createElement('a');
	var filename = new Date().toISOString();

	au.controls = true;
	au.src = url;

	li.appendChild(au);

	var upload = document.createElement('a');
	upload.href="#";
	upload.innerHTML = "Upload";
	upload.addEventListener("click", function(event){
		  var xhr=new XMLHttpRequest();
		  xhr.onload=function(e) {
		      if(this.readyState === 4) {
		          console.log("Server returned: ",e.target.responseText);
		      }
		  };
		  var fd=new FormData();
		  fd.append("audio_data",blob, filename);
		  xhr.open("POST","upload.php",true);
		  // TODO: cambiar el upload.php para hacerlo con firebase
		  xhr.send(fd);
	})

	li.appendChild(upload)//add the upload link to li

	recordingsList.appendChild(li);
}