var url = 'http://52.44.4.222/app/kibana#/dashboard/90426290-99cb-11e7-906a-4b92fe723860?_g=(refreshInterval%3A(display%3AOff%2Cpause%3A!f%2Cvalue%3A0)%2Ctime%3A(from%3Anow-7d%2Cmode%3Aquick%2Cto%3Anow))';
//var url = 'http://52.44.4.222/app/kibana#/dashboard/90426290-99cb-11e7-906a-4b92fe723860?embed=true&_g=(refreshInterval%3A(display%3AOff%2Cpause%3A!f%2Cvalue%3A0)%2Ctime%3A(from%3Anow-7d%2Cmode%3Aquick%2Cto%3Anow))';
var page = require('webpage').create();
//wait to load kibana in ms
var waitTime = 30 * 1000;

//size of virtual browser window
page.viewportSize = { width: 1500, height: 1000 };

page.open(url, function (status) {
    if (status !== 'success') {
        console.log('Unable to load the address!');
        phantom.exit();
    } else {
        window.setTimeout(function () {
       		//page.zoomFactor = 2.0;
//save as image
            page.render('kibana.jpg');
            phantom.exit();
        }, waitTime);
    }
});

