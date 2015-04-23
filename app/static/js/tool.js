$(document).foundation();

var color_index = 0;
var background_colors = ["{'background':'rgba(124, 181, 236,0.5)'}", "{'background':'rgba(144, 237, 125,0.5)'}", "{'background':'rgba(247, 163, 92,0.5)'}", "{'background':'rgba(128, 133, 233,0.5)'}", "{'background':'rgba(241, 92, 128,0.5)'}", "{'background':'rgba(228, 211, 84,0.5)'}", "{'background':'rgba(128, 133, 232,0.5)'}", "{'background':'rgba(141, 70, 83,0.5)'}", "{'background':'rgba(145, 232, 225,0.5)'}"];
// colors: ['#7cb5ec', '#434348', '#90ed7d', '#f7a35c', '#8085e9', '#f15c80', '#e4d354', '#8085e8', '#8d4653', '#91e8e1']

theChart = new Highcharts.Chart(options);

var toolApp = angular.module('toolApp', []);

toolApp.controller('ToolController', ['$scope', '$http', function ($scope,$http)
{
    
    $scope.chart = {};
    
	$scope.selected = [];
    
    $http.get('http://www.coolbest.net:5000/api/charts/' + $("#user").val() ).success(function(data){
        $scope.recent = data;
    });
        
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
    	
    	console.log(series);
    	
    	var url = 'http://www.coolbest.net:5000/api/subtopic/' + series.topic.toString();
		$.getJSON(url, function (retval) {
			
			console.log(url);
			console.log(retval);
			
			s = {
				name: series.name,
				data: retval
			}
			
			theChart.addSeries(s);
			theChart.options.series.push(s);
			
            var obj = {},
            exportUrl = 'http://104.237.136.8:8080/highcharts-export-web/';
            obj.options = JSON.stringify(theChart.options);
            obj.type = 'image/png';
            obj.async = true;
            
            // GET THUMBNAIL
            $.ajax({
                type: 'post',
                url: exportUrl,
                data: obj,
                success: function (data) {
                    
                    slug = data.substr(6,8) // slug is between 'files/' & '.png' in return value
                    $scope.slug = slug;
                    $("#slug").val(slug);
                    
                    // SAVE CHART
                    resp = $.ajax({
                        type: 'POST',
                        url: '/charts/save/' + $("#user").val() + '/' + slug ,
                        data: obj.options
                    });
                    
                    // ADD THUMBNAIL TO RECENT
                    $scope.recent.unshift({"url": exportUrl + data})
                    $scope.$apply()
                    
                }
            });
			
		});
		
		// ADD BAR TO BENEATH GRAPH
		$scope.selected.push({"name":series.name,"color":background_colors[color_index]});
		color_index++;
		if (color_index == background_colors.length) color_index = 0;
    	
    }
    
    $scope.removeFromChart = function(index) {
    	
    	//alert(index);
    	
    	$scope.selected.splice(index,1);
    	theChart.series[index].remove();
    	
    }
    
    $scope.thumbMenu = function(index) {
        
        url = $scope.recent[index].url;        
        window.location = 'http://www.coolbest.net:5000/tool/' + url.split('charts/')[1];
        
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
    	
    	var l = $scope.selected.length;
		for (var i = 0; i < l; i++) {
			if ($scope.selected[i].name == thisname) return true;
		}
    	return false;
    	
    }
    
}]).config(function($interpolateProvider){
$interpolateProvider.startSymbol('{@').endSymbol('@}');
});

