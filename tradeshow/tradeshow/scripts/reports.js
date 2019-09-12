/*
A script using PhantomJS http://phantomjs.org to create Web page screenshot at
the given browser resolution and save it as a PNG file.
Written by Ramiro Gómez http://ramiro.org/
MIT licensed: http://rg.mit-license.org/
*/
var page = require('webpage').create(),
    args = require('system').args,
    re_trim = /^https?:\/\/|\/$/g,
    re_conv = /[^\w\.-]/g
var waitTime = 15 * 1000;
var url2filename = function(url, w, h) {
    return url
        .replace(re_trim, '')
        .replace(re_conv, '-')
        + '.' + w + 'x' + h + '.png'
}

var webshot = function(url, w, h, f) {
    page.viewportSize = { width: w, height: h }
    url = url.replace('\!', '!');
    page.open(url, function(status) {
        if (status !== 'success') {
            console.log('Unable to load url: ' + url)
            phantom.exit()
        } else {
            window.setTimeout(function() {
                page.clipRect = { top: 100, left: 180, width: w-180, height: h-200 }
                //f = url2filename(url, w, h)
                page.evaluate(function() {
                    if ('transparent' === document.defaultView.getComputedStyle(document.body).getPropertyValue('background-color')) {
                        document.body.style.backgroundColor = '#fff';
                    }
                    $('button.kuiCollapseButton.sidebar-collapser').click();
                });
                console.log('Creating file: ' + f)
                page.render(f)
                phantom.exit()
            }, waitTime)
        }
    })
}

//var url = "http://localhost:5601/app/kibana#/visualize/edit/AV6JAWiRI4GA_GKdURfw?_g=(refreshInterval:(display:Off,pause:!f,value:0),time:(from:'Fri%20Sep%2001%202017%2010:00:00%20GMT%2B0530',mode:absolute,to:'Fri%20Sep%2001%202017%2017:00:00%20GMT%2B0530'))&_a=(filters:!(),linked:!f,query:(match_all:()),uiState:(spy:(mode:(fill:!f,name:table))),vis:(aggs:!((enabled:!t,id:'1',params:(customLabel:Count),schema:metric,type:count),(enabled:!t,id:'2',params:(customLabel:'Lead%20Type',field:leadType.keyword,order:desc,orderBy:'1',size:5),schema:segment,type:terms),(enabled:!t,id:'3',params:(customLabel:'Finance%20Type',field:finance_finance.keyword,order:desc,orderBy:'1',size:5),schema:group,type:terms)),listeners:(),params:(addLegend:!t,addTimeMarker:!f,addTooltip:!t,categoryAxes:!((id:CategoryAxis-1,labels:(filter:!f,rotate:0,show:!t,truncate:200),position:left,scale:(type:linear),show:!t,style:(),title:(text:'Lead%20Type'),type:category)),grid:(categoryLines:!f,style:(color:%23eee),valueAxis:ValueAxis-1),legendPosition:top,orderBucketsBySum:!f,seriesParams:!((data:(id:'1',label:Count),drawLinesBetweenPoints:!t,mode:normal,show:!t,showCircles:!t,type:histogram,valueAxis:ValueAxis-1)),times:!(),valueAxes:!((id:ValueAxis-1,labels:(filter:!t,rotate:75,show:!t,truncate:100),name:LeftAxis-1,position:bottom,scale:(mode:normal,type:linear),show:!t,style:(),title:(text:Count),type:value))),title:'Lead%20Finance%20Stats',type:histogram))"

//var url = "http://localhost:5601/app/kibana#/visualize/edit/AV6JAWiRI4GA_GKdURfw?_g=(refreshInterval:(display:Off,pause:!f,value:0),time:(from:'Fri%20Sep%2001%202017%2010:00:00%20GMT%2B0530',mode:absolute,to:'Fri%20Sep%2001%202017%2017:00:00%20GMT%2B0530'))&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'exhibitor:%22Times%20Godrej%20Properties%22')),uiState:(spy:(mode:(fill:!f,name:table))),vis:(aggs:!((enabled:!t,id:'1',params:(customLabel:Count),schema:metric,type:count),(enabled:!t,id:'2',params:(customLabel:'Lead%20Type',field:leadType.keyword,order:desc,orderBy:'1',size:5),schema:segment,type:terms),(enabled:!t,id:'3',params:(customLabel:'Finance%20Type',field:finance_finance.keyword,order:desc,orderBy:'1',size:5),schema:group,type:terms)),listeners:(),params:(addLegend:!t,addTimeMarker:!f,addTooltip:!t,categoryAxes:!((id:CategoryAxis-1,labels:(filter:!f,rotate:0,show:!t,truncate:200),position:left,scale:(type:linear),show:!t,style:(),title:(text:'Lead%20Type'),type:category)),grid:(categoryLines:!f,style:(color:%23eee),valueAxis:ValueAxis-1),legendPosition:top,orderBucketsBySum:!f,seriesParams:!((data:(id:'1',label:Count),drawLinesBetweenPoints:!t,mode:normal,show:!t,showCircles:!t,type:histogram,valueAxis:ValueAxis-1)),times:!(),valueAxes:!((id:ValueAxis-1,labels:(filter:!t,rotate:75,show:!t,truncate:100),name:LeftAxis-1,position:bottom,scale:(mode:normal,type:linear),show:!t,style:(),title:(text:Count),type:value))),title:'Lead%20Finance%20Stats',type:histogram))"


//var w = 1440;
//var h = 900;
//var f = '/opt/projects/lead_management/reports/test.png';
//webshot(url, w, h, f);

webshot(args[1], args[2], args[3], args[4])
