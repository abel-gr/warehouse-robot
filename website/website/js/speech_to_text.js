var audio_context;
var recorder;
var audio_stream;
var base64AudioFormat;
var url;
var language = "en-US";

function Initialize() {
    try {
        window.AudioContext = window.AudioContext || window.webkitAudioContext;
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
        window.URL = window.URL || window.webkitURL;

        audio_context = new AudioContext;
        console.log('Audio context is ready!');
        console.log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
    } catch (e) {
        alert('No web audio support in this browser!');
    }
}


function startRecording() {
    navigator.getUserMedia({ audio: true }, function (stream) {
        audio_stream = stream;

        var input = audio_context.createMediaStreamSource(stream);
        console.log('Media stream succesfully created',input);

        recorder = new Recorder(input,{numChannels:1});
        console.log('Recorder initialised',recorder);

        recorder && recorder.record();
        console.log('Recording...');

        document.getElementById("recordButton").disabled = true;
        document.getElementById("stopButton").disabled = false;
    }, function (e) {
        console.error('No live audio input: ' + e);
    });
	setTimeout( function(){
        console.log("before 1");
        stopRecordInterval();
      }  , 10000 );
}


function stopRecordInterval(){
    var _AudioFormat = "audio/wav";
    stopRecording(function(AudioBLOB){

        url = URL.createObjectURL(AudioBLOB);

        console.log("blob URL",url);
        convertToBase64(AudioBLOB);

        var li = document.createElement('li');
        var au = document.createElement('audio');

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
            execute();
        },);

    }, _AudioFormat);
    console.log("after 1 sec");
}


function stopRecording(callback, AudioFormat) {
    recorder && recorder.stop();
    console.log('Stopped recording.');

    audio_stream.getAudioTracks()[0].stop();

    document.getElementById("recordButton").disabled = false;
    document.getElementById("stopButton").disabled = true;

    if(typeof(callback) == "function"){

        recorder && recorder.exportWAV(function (blob) {
            callback(blob);

            recorder.clear();
        }, (AudioFormat || "audio/wav"));
    }
}


window.onload = function(){
    Initialize();

    document.getElementById("recordButton").addEventListener("click", function(){
        startRecording();
    }, false);

    document.getElementById("stopButton").addEventListener("click", function(){
        var _AudioFormat = "audio/wav";
    }, false);
};


function convertToBase64(blob){
    var reader = new FileReader();
    reader.readAsDataURL(blob);
    reader.onloadend = function() {
        base64data = reader.result.split(',')[1];
        console.log(base64data);
        base64AudioFormat=base64data;
        console.log("base 64 data",base64AudioFormat);
    }
}


function loadClient() {
    console.log("loaded google client");
    gapi.client.setApiKey('AIzaSyBkoelEAXC1mv_Q2e_F32mnrk8am3IUzN0');
    return gapi.client.load("https://content.googleapis.com/discovery/v1/apis/speech/v1/rest")
        .then(function() { console.log("GAPI client loaded for API"); },
              function(err) { console.error("Error loading GAPI client for API", err); });
}

function execute() {
    var slectedLan = document.getElementById("language-selection");
    language = slectedLan.value;
    console.log("selected_language:",url);

    console.log("audio_url:",url);
    return gapi.client.speech.speech.recognize({
        "resource": {
            "audio": {
                "content": base64AudioFormat
            },
            "config": {
                "encoding": "LINEAR16",
                "languageCode": language,
                "sampleRateHertz": 44100
            }
        }
    })
        .then(function(response) {
                console.log("Response", response);
                document.getElementById("note_area").innerHTML=response.result.results[0].alternatives[0].transcript + " "
              },
              function(err) { console.error("Execute error", err); });
}
gapi.load("client",loadClient);
/*
  gapi.client.init({
    'apiKey': 'AIzaSyBkoelEAXC1mv_Q2e_F32mnrk8am3IUzN0',

  }).then(function(){
    console.log("intialize the gapi with api key");

});
 */