/* var str2ab_blobreader = function(str, callback) {
    var blob;
    BlobBuilder = window.MozBlobBuilder || window.WebKitBlobBuilder || window.BlobBuilder;
    if (typeof(BlobBuilder) !== 'undefined') {
      var bb = new BlobBuilder();
      bb.append(str);
      blob = bb.getBlob();
    } else {
      blob = new Blob([str]);
    }
    var f = new FileReader();
    f.onload = function(e) {
        callback(e.target.result)
    }
    f.readAsArrayBuffer(blob);
}

function sendAsAB() {
 
    var ajaxRequest = new XMLHttpRequest();
    ajaxRequest.open('POST', 'https://api.github.com/markdown', true);
    ajaxRequest.setRequestHeader('Content-Type', 'application/json');
    
    ajaxRequest.onreadystatechange = function() {
        if (ajaxRequest.readyState == 4) {
            alert('Response: \n' + ajaxRequest.responseText);
        }
    };
        
   var buffer = str2ab_blobreader('{ "text": "test" }', function(buf) {
       ajaxRequest.send(buf);
    });

};
*/

//document.getElementById('blobButton').addEventListener('click', sendAsBlob);
//document.getElementById('arraybufferButton').addEventListener('click', sendAsAB);

//http://stackoverflow.com/questions/6965107/converting-between-strings-and-arraybuffers
function ab2str(buf) {
  return String.fromCharCode.apply(null, new Uint16Array(buf));
}

function str2ab(str) {
  var buf = new ArrayBuffer(str.length*2); // 2 bytes for each char
  var bufView = new Uint16Array(buf);
  for (var i=0, strLen=str.length; i<strLen; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
}


/*
//not working
self.addEventListener('message', function(e) {
  fetch(e.data, function(xhr) {	
		var result = xhr.responseText;
		setTimeout(function() { sendback(); }, 10);
		//pass JSON object back as an array buffer
		function sendback(){
			arrayBuffer = str2ab(result);
			self.postMessage(arrayBuffer,[arrayBuffer]);
		}
  });

}, false);
*/

//TRY 3rd approach her http://developerblog.redhat.com/2014/05/20/communicating-large-objects-with-web-workers-in-javascript/

self.addEventListener('message', function(e) {
  // http://techslides.com/demos/worker.js
  fetch(e.data, function(xhr) {	
		var result = xhr.responseText;
		//process the JSON
		var object = JSON.parse(result);
		//set a timeout just to add some latency
		setTimeout(function() { sendback(); }, 2000);
		//pass JSON object back as string
		function sendback(){
			self.postMessage(JSON.stringify(object));
		}
  });

}, false);



//simple XHR request in pure raw JavaScript
function fetch(url, callback) {
	var xhr;
	
	//console.log(url);

	if(typeof XMLHttpRequest !== 'undefined') xhr = new XMLHttpRequest();
	else {
		var versions = ["MSXML2.XmlHttp.5.0", 
						"MSXML2.XmlHttp.4.0",
					    "MSXML2.XmlHttp.3.0", 
					    "MSXML2.XmlHttp.2.0",
						"Microsoft.XmlHttp"]

		 for(var i = 0, len = versions.length; i < len; i++) {
			try {
				xhr = new ActiveXObject(versions[i]);
				break;
			}
			catch(e){}
		 } // end for
	}
	
	xhr.onreadystatechange = ensureReadiness;
	
	function ensureReadiness() {
		if(xhr.readyState < 4) {
			return;
		}
		
		if(xhr.status !== 200) {
			return;
		}

		// all is well	
		if(xhr.readyState === 4) {
			callback(xhr);
		}			
	}
	
	xhr.open('GET', url, true);
	xhr.send('');
}
