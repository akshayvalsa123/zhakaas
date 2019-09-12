var url = 'http://localhost:5601/goto/b35f2857af5e640b27ae20a12e26d244';
var page = require('webpage').create();
//wait to load kibana in ms
var waitTime = 15 * 1000;

var width = 1200;
var height = 1000;
//size of virtual browser window
page.viewportSize = { width: width, height: height };

page.open(url, function (status) {
    if (status !== 'success') {
        console.log('Unable to load the address!');
        phantom.exit();
    } else {

        window.setTimeout(function () {
       		//page.zoomFactor = 2.0;
//save as image
			//page.clipRect = {top: 100, left: 180, width: 1025, height: 900};
            page.render('kibana.jpg');
            phantom.exit();
        }, waitTime);
    }
});
