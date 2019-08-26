//////////////////////////////////////////////////////////////////////// UTILS

var clickPoint = function(event) {
                  
    if ( $('a[href="#data-view"]').attr('aria-selected') == "true" ) { 

        var cat = this.category;
        var result = toolApp.chart.periodsSelected.filter(function( obj ) {
            return obj.display == cat;
        });
        
        drilldown(
        this.series.userOptions.filters,
        this.series.userOptions.dataset,
        this.series.userOptions.sub,
        this.series.userOptions.topic,
        this.series.userOptions.agg,
        result[0].value);

    } else {

        $('#seriesoptions-'+ this.series.userOptions.dataset + '-' + this.series.userOptions.topic).foundation('reveal', 'open');

    }
}

var tooltipFormatter = function() {

   // return '<center><b>' + this.x + '</b><br/>' + this.series.name.split(': ').join(':<br/>').split(' #').join('<br/>#') + '<br/><b>' + this.y + '</b></center>';
   // return '<center><b>' + this.x + '</b><br/>' + this.series.name.split(': ')[0] + ' #' + this.series.name.split('#')[1] + '<br/><b>' + this.y + ' ' + this.series.userOptions.unit + '</b></center>';
     
     if (this.series.userOptions.measure == 'count' || this.series.userOptions.measure == 'amount') {
        var label = this.series.userOptions.unit;
     } else {
        var label = '%';
     }
     
     
     return '<center><b>' + this.x + '</b><br>' + this.y + ' ' + label + '</center>';

}

var drilldown = function(filters,dataset,flag,topic,agg,year) {
        
    if (topic==0) {
    
        my_alert('All topics series!! No drilldown available.');
    
    } else if (agg==0) {
    
        var uri = getInstancesUri(filters,dataset,flag,topic,year);
        var url = baseUrl + "/api/drilldown/" + uri;
    
        $.get(url, function( data ) {
      
            var instances = JSON.parse(data);      
            
            if (instances.length) {
            
                toolApp.instances = instances;
                //theScope.$apply();
                $('#datapoints').foundation('reveal', 'open');
                
            } else {
            
                my_alert('Source/description unavailable for this dataset.');
            
            }
        
        });
    
    } else {
        
        my_alert('Pre-aggregated dataset!! No drilldown available.');
        
    }

}

Array.prototype.remove = function() {

    var what, a = arguments, L = a.length, ax;
    while (L && this.length) {
        what = a[--L];
        while ((ax = this.indexOf(what)) !== -1) {
            this.splice(ax, 1);
        }
    }
    
    return this;
    
};

String.prototype.capitalizeFirstLetter = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}

function getQueryVariable(variable) {
       var query = window.location.search.substring(1);
       var vars = query.split("&");
       for (var i=0;i<vars.length;i++) {
               var pair = vars[i].split("=");
               if(pair[0] == variable){return pair[1];}
       }
       return(false);
}

function getInstancesUri(filters,dataset,flag,topic,frm,to) {
    
    // have filters been checked?
    var params = [];
    filters.forEach(function (filter, index) { 
        var param = undefined;
        if (filter.include) {
            param = filter.name + "=1";
        }
        if (filter.exclude) {
            param = filter.name + "=0";
        }
        if (param) {
            params.push(param);
        }   
    });
    
    var uri = dataset + "/";
    uri = uri + (flag ? "subtopic" : "topic");    
    uri = uri + "/" + topic
    if (typeof to === 'undefined') {
        uri = uri + "/" + frm;
    } else {
        uri = uri + "/" + frm + "/" + to;
    }
    
    if (params.length > 0) {
        uri = uri + "?" + params.join("&");
    }
    
    return uri;
    
}

function my_alert(text) {
    
    $('#my_alert').find('#message').text(text);
    $('#my_alert').foundation('reveal', 'open');
    
}