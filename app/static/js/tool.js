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


theChart = {}
var toolApp = angular.module('toolApp', []);

toolApp.controller('ToolController', ['$scope', '$http', function ($scope,$http)
{
    
    $scope.chart = {};
    
	$scope.selected = [];
    
    $scope.recent = [];
    
    $scope.filters=[
    "Referral Hearing",
    "Budget Appropriations"
    ];
    
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
                    var country = $(this).attr('country');
                    angular.element('.choose_topic:checked').each(function () {
                       var $this = $(this);
                       if ($this.length) {
                        var selText = $this.next('span').text();
                        var subtopic = $this.attr('subtopic');
                        if (country == dataset.country) {
                            dataset_name = dataset.country + ': ' + dataset.name + ' #' + selText;
                            $scope.results.push({"dataset":dataset.id,"topic":subtopic,"name":dataset_name});                      
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
            angular.forEach($scope.selected, function (selected, index2) { 
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
        
        return angular.element('#topics input[type="checkbox"]:checked').length;
        
    }
    
    
    $scope.addToChart = function(series) {
    	
    	//console.log(series);
    	
    	//var url = 'http://www.coolbest.net:5000/api/subtopic/' + series.topic.toString();
    	var url = 'http://www.coolbest.net:5000/api/datasets/' + series.dataset.toString() + '/topic/' + series.topic.toString() + '/count';
		$.getJSON(url, function (retval) {
			
			//console.log(url);
			//console.log(retval);
			
			s = {
			    topic: series.topic,
			    dataset: series.dataset,
				name: series.name,
				data: retval,
				color: $scope.getHexColor(),
				_symbolIndex: ($scope.selected.length - 1) % 5
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
                   /* resp = $.ajax({
                        type: 'POST',
                        url: '/charts/save/' + $("#user").val() + '/' + slug ,
                        data: obj.options
                    });
                    */
                    
                    
                    // ADD THUMBNAIL TO RECENT
                    $scope.recent.unshift({"url": exportUrl + data, "options": obj.options });
                    $scope.$apply();
                    
                }
            });
			
		});
		
		// ADD BAR TO BENEATH GRAPH
		$scope.selected.push({"name":series.name,"color":$scope.getRgbaColor()});
		//console.log($scope.selected);
    	
    }
    
    
    $scope.getHexColor = function() {
        
        //construct array of all colors in scope.selected
        //var colors = [];
        //for (var i = 0; i < $scope.selected.length; i++) {
            return hex_colors[rgba_colors.indexOf($scope.selected[$scope.selected.length-1].color)];
        //}
        
        
        
        //remove existing colors, reset queue to handle dupes
        //var hex_q = angular.copy(hex_colors);  
        //for (var i = 0; i < colors.length; i++) {
         //   hex_q.remove(colors[i]);
          //  if (hex_q.length == 0) {
           //     hex_q = angular.copy(rgba_colors);   
            //}
        //}
        
        //return next color in line
        //return hex_q[0];
                
    }
    
    $scope.getRgbaColor = function() {
        
        //construct array of all colors in scope.selected
        var colors = [];
        for (var i = 0; i < $scope.selected.length; i++) {
            colors.push($scope.selected[i].color);
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
    
    $scope.removeFromChart = function(index) {
    	
    	//alert(index);
    	
    	$scope.selected.splice(index,1);
    	theChart.series[index].remove();
    	
    }
    
    $scope.savedMenu = function(index) {
        
        //alert(index);
        
        reverse_index = $scope.saved.length - 1 - index; 
        
        //alert(reverse_index);
          
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
    	
    	var l = $scope.selected.length;
		for (var i = 0; i < l; i++) {
			if ($scope.selected[i].name == thisname) return true;
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