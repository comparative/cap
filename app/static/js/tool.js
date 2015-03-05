
$(document).foundation();

//var deferred = new $.Deferred();
var color_index = 0;
var background_colors = ["{'background':'rgba(124, 181, 236,0.5)'}", "{'background':'rgba(144, 237, 125,0.5)'}", "{'background':'rgba(247, 163, 92,0.5)'}", "{'background':'rgba(128, 133, 233,0.5)'}", "{'background':'rgba(241, 92, 128,0.5)'}", "{'background':'rgba(228, 211, 84,0.5)'}", "{'background':'rgba(128, 133, 232,0.5)'}", "{'background':'rgba(141, 70, 83,0.5)'}", "{'background':'rgba(145, 232, 225,0.5)'}"];

/*
var data1 = [];
var getData1 = 
$.getJSON('http://www.coolbest.net:5000/api/subtopic/105', function (retval1) {
    //return retval1;
    data1 = retval1;
});

var data2 = [];
var getData2 = 
$.getJSON('http://www.coolbest.net:5000/api/subtopic/107', function (retval2) {
	//return retval2;
	//console.log(retval2);
    data2 = retval2;
});
*/

var options = {
        
        chart: {
            renderTo: 'chart',
            ignoreHiddenSeries : false
        },
        
        title: {
            text: ''
        },
		
		tooltip: { enabled: false },
		credits: { enabled: false },
		
		xAxis: {
        	title : {
        		text: 'Year'
        	},
        	
            categories: ['2001', '2002', '2003', '2004', '2005', '2006',
                '2007', '2008', '2009', '2010',]
        },
             
        yAxis: {

            title: {
                text: 'Count'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        
        plotOptions:{
            line: {
                dataLabels: {
                    enabled: false 
                }
            },
            column:{
                borderWidth: 0.2
            },
            series:{
                point: {
                    events: {
                        'click': function(event){
                        
                            if ( $('a[href="#data-view"]').attr('aria-selected') == "true" ) { 
                                
                                $('#datapoints').foundation('reveal', 'open');
                                
                            } else {
                                
                                $('#lineoptions').foundation('reveal', 'open');
                                
                            }
                        }
                    }
               },
               
               states: {
                hover: {
                halo: false
                }
               },
               
               shadow: false,
               animation: false,
               cursor: 'pointer'
           }
        },
        
        legend:{
            enabled: false
        },
        
        /*exporting:{
            buttons:{
                printButton:{
                    enabled: false
                },
                exportButton:{
                    enabled: true
                }	 
            },
            url: 'http://www.policyagendas.org/papgraph/exporting',
            width: '960'
        },*/
        
        series: [],
    	
    
    	colors: ['#7cb5ec', '#90ed7d', '#f7a35c', '#8085e9', '#f15c80', '#e4d354', '#8085e8', '#8d4653', '#91e8e1']

    	
    };

theChart = new Highcharts.Chart(options);

/*
var drawChart = 
function (data1,data2) {
    
    
    var series1 = {
            name: 'US State of Pennsylvania: Parliamentary Activities: Hearings: Macroeconomics: Budget, Debt',
            data: data1[0]
        };
        
    var series2 = {
            name: 'US State of Pennsylvania: Parliamentary Activities: Macroeconomics: Tax Policy, Reform',
            data: data2[0]
        };
    
    options.series.push(series1);
    options.series.push(series2);
	
	theChart.destroy();
    theChart = new Highcharts.Chart(options);
    
    
};
*/


$(document).ready(function() {
    
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
    
    $('#pushme').click(function(e) {
    	
    	/*
		var turnOffGrid = { lineWidth: 0,
		gridLineWidth: 0,
		minorGridLineWidth: 0,
		lineColor: 'transparent',      
		labels: {
		   enabled: false
		},
		minorTickLength: 0,
		tickLength: 0 };
    	*/
    	
    	//var turnOffGrid = {
		//gridLineWidth: 0
		//};
    	
    	/*
    	var options = theChart.options;
    	options.yAxis.lineWidth = 0;
    	options.yAxis.gridLineWidth = 0;
    	options.yAxis.gridLineColor = 'transparent';
    	options.yAxis.labels = {
		   enabled: false
		}
		options.yAxis.minorTickLength = 0;
    	options.yAxis.tickLength = 0;
    	theChart = new Highcharts.Chart(options);

    	theChart.addSeries({
            name: 'US State of Shock',
            data: [1,2,3,4,5,6,7,8,9,0]
        });
    	*/
    	
    	//var theseOptions = theChart.options;
    	
    	//console.log(theseOptions);
    	
		//for (var attrname in turnOffGrid) { theseOptions.xAxis[attrname] = turnOffGrid[attrname]; }
		//for (var attrname in turnOffGrid) { theseOptions.yAxis[attrname] = turnOffGrid[attrname]; }
    	
    	
    	
    	//theChart.destroy();
    	//theChart = new Highcharts.Chart(theseOptions);
    	
    	
    	
    	/*
    	e.preventDefault();
    	theChart.addSeries({
            name: 'US State of Shock',
            data: [1,2,3,4,5,6,7,8,9,0]
        });
    	*/
    	
		//theChart.redraw();
		
		
		
		
    });
    
    /*
    $('#countryModal input').click(function() {     
        $('#denmark').show();
    });
    */
    
});
    
//$.when(getData1, getData2).done(drawChart);

var toolApp = angular.module('toolApp', []);

toolApp.controller('ToolController', ['$scope', '$http', function ($scope,$http)
{
	     
	$scope.selected = [];

    
    $http.get('http://www.coolbest.net:5000/api/countries').success(function(data){
        $scope.countries = data;
    });
    
    $http.get('http://www.coolbest.net:5000/api/categories').success(function(data){
        $scope.categories = data;
    });
    
    $http.get('http://www.coolbest.net:5000/api/topics').success(function(data){
        $scope.topics = data;
    });
    
    $http.get('http://www.coolbest.net:5000/api/datasets').success(function(data){
        $scope.datasets = data;
    });
    
    $scope.surprise = function() { 
        $scope.results = [];
        
        var cats = [];
        angular.element('#categories input:checked').each(function () {
            var cat = $(this).attr('catid');
            cats.push(cat);
        });
        
        angular.forEach($scope.datasets, function (dataset, index) {
            if (cats.indexOf(dataset.category.toString()) > -1) {
                angular.element('#countries input:checked').each(function () {
                    var country = $(this).next('label').text();
                    angular.element('#topics input:checked').each(function () {
                       var $this = $(this);
                       if ($this.length) {
                        var selText = $this.next('span').text();
                        var subtopic = $this.attr('subtopic');
                        $scope.results.push({"topic":subtopic,"name":country + ': ' + dataset.name + ' #' + selText});
                       }
                    });
                });
            }
        });
    }
    
    $scope.addToChart = function(series) {
    	
    	var url = 'http://www.coolbest.net:5000/api/subtopic/' + series.topic.toString();
		$.getJSON(url, function (retval) {
			
			console.log(url);
			console.log(retval);
			
			theChart.addSeries({
				name: series.name,
				data: retval
			});
			
		});
		
		$scope.selected.push({"name":series.name,"color":background_colors[color_index]});
		color_index++;
		if (color_index == background_colors.length) color_index = 0;
    	
    }
    
    $scope.removeFromChart = function(index) {
    	
    	//alert(index);
    	
    	$scope.selected.splice(index,1);
    	theChart.series[index].remove();
    	
    }
    
    $scope.isSelected = function (thisname) {
    	
    	var l = $scope.selected.length;
		for (var i = 0; i < l; i++) {
			if ($scope.selected[i].name == thisname) return true;
		}
    	return false;
    	
    }
    
}]).config(function($interpolateProvider){
$interpolateProvider.startSymbol('{@').endSymbol('@}');
});

// colors: ['#7cb5ec', '#434348', '#90ed7d', '#f7a35c', '#8085e9', '#f15c80', '#e4d354', '#8085e8', '#8d4653', '#91e8e1']



