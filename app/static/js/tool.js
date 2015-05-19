$(document).foundation();

var rgba_colors = [
"{'background':'rgba(124, 181, 236, 0.5)'}", 
"{'background':'rgba(144, 237, 125, 0.5)'}", 
"{'background':'rgba(247, 163, 92, 0.5)'}", 
"{'background':'rgba(128, 133, 233, 0.5)'}", 
"{'background':'rgba(241, 92, 128, 0.5)'}", 
"{'background':'rgba(228, 211, 84, 0.5)'}", 
"{'background':'rgba(141, 70, 83, 0.5)'}",
"{'background':'rgba(145, 232, 225, 0.5)'}"
];

var hex_colors = ['#7cb5ec', '#90ed7d', '#f7a35c', '#8085e9', '#f15c80', '#e4d354', '#8d4653', '#91e8e1'];

var year_list = [];
for (i=1946; i < 2016; i++) {
    year_list.push(i.toString());            
}

theChart = {}
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
    
    
   /* $scope.chart = {
        series:[
    
            {data: [count:[],percent_total:[],percent_change[]],
            filters: [],
            topic: ,
            dataset: ,
            name: ,
            color: 
            },
        
            {data: [count:[],percent_total:[],percent_change[]],
            filters: [],
            topic: ,
            dataset: ,
            name: ,
            color: 
            },

        ],
    
        yearFrom: "1946",
    
        yearTo: "2015"    
    
    } */
    
    
    
    $scope.chart = {};
	$scope.chart.series = [];
    $scope.chart.yearFrom = $scope.years[0];
    $scope.chart.yearTo = $scope.years[$scope.years.length - 1];
    
    $scope.recent = [];
    

    
    $http.get('http://www.coolbest.net:5000/api/charts/' + $("#user").val() ).success(function(data){
        $scope.saved = data;
    });
        
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
        //console.log($scope.topics);
        
    });
    
    $http.get('http://www.coolbest.net:5000/api/datasets').success(function(data){
        
       // console.log(data);
        
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
                            dataset_name = dataset.country + ': ' + dataset.name + ' #' + selText;
                            $scope.results.push({"dataset":dataset.id,"topic":subtopic,"name":dataset_name,"filters":JSON.parse(dataset.filters)});                      
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
    
    
    $scope.addToChart = function(result) {
    	
    	//console.log(series.filters);
    	
    	filters = [];
    	angular.forEach(result.filters, function (f, index) {
    	    filter = {};
    	    filter.name = f
    	    filter.display = f.replace('filter_','').replace(/_/g,' ').replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase(); });
            filter.include = false;
            filter.exclude = false;
            filters.push(filter);
         });
    	
    	
    	$scope.chart.series.push(
    	{
    	"name":result.name,
    	"color":$scope.getRgbaColor(),
    	"dataset": result.dataset,
    	"topic": result.topic,
    	"filters": filters,
    	"measure": "count",
    	"type": "line"
    	});
    	
    	//console.log($scope.chart.series);
    	
    	
    	var url = 'http://www.coolbest.net:5000/api/datasets/' + result.dataset.toString() + '/topic/' + result.topic.toString() + '/count';
		$.getJSON(url, function (retval) {
			
			console.log(url);
			
			//console.log(retval);
			
			//$scope.chart.series[$scope.chart.series.length - 1].dataset = series.dataset;
			//$scope.chart.series[$scope.chart.series.length - 1].topic = series.topic;
			
			$scope.chart.series[$scope.chart.series.length - 1].data = retval; //DANGER! DANGER!
			$scope.redrawChart(); 
            
		});
    	
    }
    
    $scope.removeFromChart = function(index) {
        
        $scope.chart.series.splice(index,1);
    	$scope.redrawChart();    	
    	
    }
    
    
    $scope.allSeriesSameType = function() {
        
         angular.forEach($scope.chart.series, function (series, index) {
            series.type = $scope.chart.chartType;
         });
         
         $scope.redrawChart();
        
    }
    
    $scope.redrawChart = function() {
    
       // console.log($scope.chart);
    
        options.series = [];
        
        angular.forEach($scope.chart.series, function (series, index) {
            
            dataslice = series.data.slice(year_list.indexOf($scope.chart.yearFrom),year_list.indexOf($scope.chart.yearTo) + 1);
            
            //console.log($scope.chart.bs);
            
            var s = {
                type: series.type,
			    topic: series.topic,
			    dataset: series.dataset,
				name: series.name,
				data: dataslice,
				color: hex_colors[rgba_colors.indexOf(series.color)]
			}
			
			//console.log(s);
			
			options.series.push(s);
            
        });
        
        
        
        

        $scope.yearslice = year_list.slice(year_list.indexOf($scope.chart.yearFrom),year_list.indexOf($scope.chart.yearTo) + 1);
        options.xAxis.categories = $scope.yearslice;
        
        //options.chart.type = $scope.chart.chartType;
        
        theChart.destroy();
		theChart = new Highcharts.Chart(options);
		
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
                $scope.recent.unshift({"url": exportUrl + data, "options": obj.options });
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
            success: function(){  
                alert('chart pinned!');
                $scope.saved.unshift({"url": "http://www.coolbest.net:5000/charts/" + $("#slug").val(), "options": options});
                $scope.$apply(); 
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) { 
                alert('could not pin chart.  Already pinned?'); 
            }
             
        });
        
    }
    
    $scope.applySeriesOptions = function(series) {
        
        $scope.closeSeriesOptions(series);
        $scope.redrawChart();
        
    };
    
    $scope.closeSeriesOptions = function(series) {
        
        angular.element('#seriesoptions-'+ series.dataset + '-' + series.topic).foundation('reveal','close');
        
    };
    
    $scope.savedMenu = function(index) {
        
        reverse_index = $scope.saved.length - 1 - index;           
        url = $scope.saved[index].url;        
        window.location = 'http://www.coolbest.net:5000/tool/' + url.split('charts/')[1];
        
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