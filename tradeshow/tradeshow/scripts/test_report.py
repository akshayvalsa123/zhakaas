import os
from subprocess import call


def main():
    """
    """
    phantomscript = "/opt/projects/lead_management/tradeshow/tradeshow/scripts/reports.js"
    reportUrl = "http://localhost:5601/goto/d15c9284d4f93803b39c6993dc45b91c"
    reportUrl = "http://localhost:5601/app/kibana#/visualize/edit/AV6I6g5nI4GA_GKdURfp?_g=(refreshInterval:(display:Off,pause:!f,value:0),time:(from:'Fri%20Sep%2001%202017%2010:00:00%20GMT%2B0530',mode:absolute,to:'Fri%20Sep%2001%202017%2017:00:00%20GMT%2B0530'))&_a=(filters:!(),linked:!f,query:(query_string:(analyze_wildcard:!t,query:'exhibitor:%22Times%20DLF%22')),uiState:(spy:(mode:(fill:!f,name:table))),vis:(aggs:!((enabled:!t,id:'1',params:(customLabel:'Interested%20Leads'),schema:metric,type:count),(enabled:!t,id:'2',params:(customLabel:'Property%20Location',field:property_location.keyword,order:desc,orderBy:'1',size:10),schema:segment,type:terms),(enabled:!t,id:'3',params:(customLabel:'Property%20Type',field:property_type.keyword,order:desc,orderBy:'1',size:5),schema:group,type:terms)),listeners:(),params:(addLegend:!t,addTimeMarker:!f,addTooltip:!t,categoryAxes:!((id:CategoryAxis-1,labels:(rotate:0,show:!t,truncate:100),position:bottom,scale:(type:linear),show:!t,style:(),title:(text:'Property%20Location'),type:category)),grid:(categoryLines:!f,style:(color:%23eee)),legendPosition:right,orderBucketsBySum:!f,seriesParams:!((data:(id:'1',label:'Interested%20Leads'),drawLinesBetweenPoints:!t,mode:stacked,show:true,showCircles:!t,type:histogram,valueAxis:ValueAxis-1)),times:!(),valueAxes:!((id:ValueAxis-1,labels:(filter:!f,rotate:0,show:!t,truncate:100),name:LeftAxis-1,position:left,scale:(mode:normal,type:linear),show:!t,style:(),title:(text:'Interested%20Leads'),type:value))),title:'Locality%20Property%20Preference',type:histogram))"
    width = "1440";
    height = "900";
    reportFile = "/opt/projects/lead_management/reports/test.png"
    call(['phantomjs', phantomscript, reportUrl, width, height, reportFile])

if __name__ == "__main__":    
    main()



