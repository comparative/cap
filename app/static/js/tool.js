//////////////////////////////////// CLASS-LIKE THANGS

function Series (dataset,topic,name,filters) {

    this.dataset = dataset;
    this.topic = topic;
    this.name = name;
    
    if (filters) {
        this.filters = [];
        for (index = 0; index < filters.length; ++index) {
             var filter = new Filter(filters[index]);
             this.filters.push(filter);
        }
    }
    
    this.measure = "count";
    this.type = "line";
    
    this.color = undefined;
    this.data = [];
    
}

function Filter (name) {

    this.name = name
    this.display = name.replace('filter_','').replace(/_/g,' ').replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase(); });
    this.include = false;
    this.exclude = false;
    
}

function Chart() {
    
    this.series = [];
    this.yearFrom = year_list[0];
    this.yearTo = year_list[year_list.length - 1];
    
}

function Saved(slug, imgsrc, options) {
    
    this.slug = slug;
    this.imgsrc = imgsrc;
    this.options = options;
    
}


//////////////////////////////////////// ANGULAR APP

var toolApp = angular.module('toolApp', []);

toolApp.controller('ToolController', ['$scope', '$http', function ($scope,$http)
{
    
    $scope.years = year_list;
    
    $scope.measures = [
        {"measure":"count","display":"Count"},
        {"measure":"percent_total","display":"Percent Total"},
        {"measure":"percent_change","display":"Percent Change"},
    ];
    
    $scope.chart_types = [
        {"type":"line","display":"Line"},
        {"type":"spline","display":"Smooth Line"},
        {"type":"column","display":"Column"},
        {"type":"scatter","display":"Scatter"},
        {"type":"area","display":"Area"},
        {"type":"areaspline","display":"Smooth Area"}
    ];
    
    $scope.chart = new Chart();

    $http.get('http://www.coolbest.net:5000/api/charts/' + $("#user").val() ).success(function(data){
    
        saved = [];
        angular.forEach(data, function (chart, index) {
            item = new Saved(chart.slug, 'http://www.coolbest.net:5000/charts/' + chart.slug, chart.options);
            saved.unshift(item);
        });
        $scope.saved = saved;
        
    });
    
    $scope.recent = [];
    
    
    // FACETED SEARCH (right sidebar)
          
    $http.get('http://www.coolbest.net:5000/api/countries').success(function(data){
        $scope.countries = data;
    });
    
    $http.get('http://www.coolbest.net:5000/api/categories').success(function(data){
        $scope.categories = data;
    });
    
    $http.get('http://www.coolbest.net:5000/api/topics').success(function(data){
        
        var retval = [];
        for (var i = 0; i < data.length; i++) {
            var row = {};
            var parsed = data[i].topic.split('_');
            row.id = parsed[0];
            row.name = parsed[1];
            row.subtopics = [];
            for (var j = 0; j < data[i].subtopics.length; j++) {
                var subrow = {};
                var subparsed = data[i].subtopics[j].split('_');
                subrow.id = subparsed[0];
                subrow.name = subparsed[1];
                row.subtopics.push(subrow);
            }
            retval.push(row);
        }
        
        $scope.topics = retval;
        
    });
    
    $http.get('http://www.coolbest.net:5000/api/datasets').success(function(data){
    
        $scope.datasets = data;
    
    });
              
    $scope.doFacets = function() { 
        
        $scope.results = [];
        
        var cats = [];
        angular.element('#categories input:checked').each(function () {
            var cat = $(this).attr('catid');
            cats.push(cat);
        });
        
        angular.forEach($scope.datasets, function (dataset, index) {
            if (cats.indexOf(dataset.category.toString()) > -1) {
                angular.element('#countries input:checked').each(function () {
                    var country = $(this).attr('country');
                    angular.element('.choose_topic:checked').each(function () {
                       var $this = $(this);
                       if ($this.length) {
                        var selText = $this.next('span').text();
                        var subtopic = $this.attr('subtopic');
                        if (country == dataset.country) {
                        
                            // ADD TO SEARCH RESULTS
                            dataset_name = dataset.country + ': ' + dataset.name + ' #' + selText;
                            var searchResult = new Series(dataset.id,subtopic,dataset_name,JSON.parse(dataset.filters));
                            $scope.results.push(searchResult);
                                           
                        }
                       }
                    });
                });
            }
        });
        
    }
    
    $scope.noResults = function() {
    
        var unhidden_results = [];
        angular.forEach($scope.results, function (result, index) {
            var add = true;
            angular.forEach($scope.chart.series, function (selected, index2) { 
                if (result.name == selected.name) {
                    add = false;
                }
            });
            if (add) { 
                unhidden_results.push(result);
            }
        });
        
        return (
        unhidden_results.length == 0 && 
        $scope.countryCount() > 0 && 
        $scope.categoryCount() > 0 && 
        $scope.topicCount() > 0
        ) ? true : false;
        
    }
    
    $scope.countryCount = function() {
        
        return angular.element('#countries input[type="checkbox"]:checked').length;
        
    }
    
    $scope.categoryCount = function() {
        
        return angular.element('#categories input[type="checkbox"]:checked').length;
        
    }
    
    $scope.topicCount = function() {
        
        return angular.element('#topics input.choose_topic:checked').length;
        
    }
    
    $scope.chartToOptions = function() {
    
        
        options.series = [];
        
        angular.forEach($scope.chart.series, function (series, index) {
            
            dataslice = series.data.slice(year_list.indexOf($scope.chart.yearFrom),year_list.indexOf($scope.chart.yearTo) + 1);
            
            var s = {
                type: series.type,
			    topic: series.topic,
			    dataset: series.dataset,
				name: series.name,
				data: dataslice,
				color: hex_colors[rgba_colors.indexOf(series.color)]
			}
			
			options.series.push(s);
            
        });


        $scope.yearslice = year_list.slice(year_list.indexOf($scope.chart.yearFrom),year_list.indexOf($scope.chart.yearTo) + 1);
        options.xAxis.categories = $scope.yearslice;
            
        return options;
    
    }
    
    
    $scope.addToChart = function(result) {
    	
    	result.color = $scope.getRgbaColor();
    	$scope.chart.series.push(result);
    	
    	var url = 'http://www.coolbest.net:5000/api/datasets/' + result.dataset.toString() + '/topic/' + result.topic.toString() + '/count';
		
		$.getJSON(url, function (retval) {
			
			angular.forEach($scope.chart.series, function (selected, index) { 
                if (result.name == selected.name) {
                    $scope.chart.series[index].data = retval;
                }
            });
			
			$scope.drawChart(); 
            
		});
    	
    }
    
    $scope.removeFromChart = function(index) {
        
        $scope.chart.series.splice(index,1);
    	$scope.drawChart();    	
    	
    }
    
    $scope.allSeriesSameType = function() {
        
         angular.forEach($scope.chart.series, function (series, index) {
            series.type = $scope.chart.chartType;
         });
         
         $scope.drawChart();
        
    }
    
    $scope.drawChart = function() {
    
        theChart.destroy();
		theChart = new Highcharts.Chart($scope.chartToOptions());
		
        var obj = {},
        exportUrl = 'http://104.237.136.8:8080/highcharts-export-web/';
        obj.options = JSON.stringify(theChart.options);
        obj.type = 'image/png';
        obj.async = true;
        
        // GET THUMBNAIL (& SLUG, from export server)
        $.ajax({
            type: 'post',
            url: exportUrl,
            data: obj,
            success: function (data) {
                
                slug = data.substr(6,8) // slug is between 'files/' & '.png' in return value
                $scope.slug = slug;
                $("#slug").val(slug);
                                
                // ADD THUMBNAIL TO RECENT
                item = new Saved(slug, exportUrl + data, obj.options);
                $scope.recent.unshift(item);
                $scope.$apply();
                
            }
        });
	
    }
    
    $scope.getRgbaColor = function() {
        
        //construct array of all colors in scope.selected
        var colors = [];
        for (var i = 0; i < $scope.chart.series.length; i++) {
            colors.push($scope.chart.series[i].color);
        }
        
        //remove existing colors, reset queue to handle dupes
        var rgba_que = angular.copy(rgba_colors);  
        for (var i = 0; i < colors.length; i++) {
            rgba_que.remove(colors[i]);
            if (rgba_que.length == 0) {
                rgba_que = angular.copy(rgba_colors);   
            }
        }
        
        //return next color in line
        return rgba_que[0];
                
    }
    
    $scope.saveChart = function() {
        
        options = JSON.stringify(theChart.options);
            
        // SAVE CHART
        resp = $.ajax({
            type: 'POST',
            url: '/charts/save/' + $("#user").val() + '/' + $("#slug").val() ,
            data: options,
            success: function() {
                alert('chart pinned!');
                item = new Saved( $("#slug").val(), 'http://www.coolbest.net:5000/charts/' + $("#slug").val(), options );
                $scope.saved.unshift(item);
                $scope.$apply();
                console.log($scope.saved);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) { 
                alert('could not pin chart.  Already pinned?'); 
            }
             
        });
        
    }
    
    $scope.editSeries = function(series) {
        
        $scope.closeSeriesModal(series);
        $scope.drawChart();
        
    };
    
    $scope.closeSeriesModal = function(series) {
        
        angular.element('#seriesoptions-'+ series.dataset + '-' + series.topic).foundation('reveal','close');
        
    };

    
    $scope.savedMenu = function(index) {
        
        reverse_index = $scope.saved.length - 1 - index;           
        slug = $scope.saved[index].slug;        
        window.location = 'http://www.coolbest.net:5000/tool/' + slug;
        
    }
    
    $scope.thumbMenu = function(index) {
        
        /*reverse_index = $scope.saved.length - 1 - index;    
        url = $scope.saved[reverse_index].url;        
        window.location = 'http://www.coolbest.net:5000/tool/' + url.split('charts/')[1];*/
        
    }
    
    $scope.actions = function(index) {
        
        alert(index);
        
        /*
        if (action == 'download') {
            
            theChart.exportChart({
                type: 'img/png',
                filename: $scope.chart.slug + '.png'
            });
            
        }
        */
                 
    }
               
    $scope.isSelected = function (thisname) {
    	
    	var l = $scope.chart.series.length;
		for (var i = 0; i < l; i++) {
			if ($scope.chart.series[i].name == thisname) return true;
		}
    	return false;
    	
    }
       
    
}]).config(function($interpolateProvider){
$interpolateProvider.startSymbol('{@').endSymbol('@}');
});


/////////////////////////////////////////////////////////////////////// DOCUMENT READY

$(document).ready(function() {
    
    $(document).foundation();
    
    // access angular scope from outside app
    theScope = angular.element(document.getElementById('toolcontroller')).scope();
    
    // create angular model from highcharts options
    theScope.chart.chartFromOptions(options);
    
    // send options to highcharts
    theChart = new Highcharts.Chart(options);
    
    $('a.Source').click(function(e) {
        e.preventDefault();
        $('#datapoints').foundation('reveal', 'open');
    });

    $('img.thumb').click(function(e) {
        e.preventDefault();
        $('#thumbnailoptions').foundation('reveal', 'open');
    });

    $('h5.picker-label').click(function(e) {
        e.preventDefault();
        $('div.picker:visible').slideToggle('fast','linear');
        $(this).next('div').slideToggle('fast','linear');
    });

    $( "#chart_actions" ).change(function() {

        if ($(this).val() == "download") {
    
            theChart.exportChart({
                type: 'img/png',
                filename: $("#slug").val()
            });
    
        }
        
        if ($(this).val() == "copy") {
            
            window.prompt( "Copy to clipboard: Ctrl+C, Enter", "http://www.coolbest.net:5000/charts/" + $("#slug").val() );
    
        }
        
        if ($(this).val() == "embed") {
            
           $('#embed_code').foundation('reveal', 'open');
    
        }

    });
              
});


//////////////////////////////////////////////////////////////////////// UTILS

Chart.prototype.chartFromOptions = function(options) {

    var selected = [];
    for (var i = 0; i < options.series.length; i++) { 
        var series = options.series[i]; 
        selected.push({dataset: series.dataset, topic: series.topic, name: series.name, color: rgba_colors[hex_colors.indexOf(series.color)],data:series.data});
    }
    
    theScope.chart.series = selected;  

};


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
