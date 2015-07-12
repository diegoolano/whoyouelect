function LoadImages(currID) {
    setTimeout(function() { 
		postMessage(currID); 
    }, 100);  
}

self.onmessage = function(event) {
	var currID = event.data;
	LoadImages(currID); 
};
