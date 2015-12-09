//////////////////////////////////// CLASS-LIKE THANGS

function Series (dataset,topic,name,filters,sub,unit,aggregation_level,budget) {

    this.dataset = dataset;
    this.topic = topic;
    this.name = name;
    this.sub = sub;
    this.budget = budget;
    
    if (filters) {
        this.filters = [];
        for (index = 0; index < filters.length; ++index) {
             var filter = new Filter(filters[index]);
             this.filters.push(filter);
        }
    }
    
    
    this.type = "line";
    this.yaxis = 0;
    this.xaxis = 0;
    this.measure_on_multiple_axes = false;
    
    this.color = undefined;
    this.unit = unit;
    
    this.measures = [];
    
    if (budget) {
        
        this.measures.push('amount');
        this.measures.push('percent_total');
        this.measures.push('percent_change');
        this.measure = 'amount';
    
    } else if (aggregation_level == 2) {
        
        this.measures.push('percent_total');
        this.measure = 'percent_total';
        
    } else {
        
        this.measures.push('count');
        this.measures.push('percent_total');
        this.measures.push('percent_change');
        this.measure = 'count';
    
    } 
    
   
    //this.measure = "count";
    
    
    this.chartdata = [];
    
    this.alldata = [];
    this.alldata.years = [];
    
    
    for (var i = 0; i < this.measures.length; i++) {
        
        this.alldata[this.measures[i]] = [];
    
    }
    
    
    //this.alldata.count = [];
    //this.alldata.percent_total = [];
    //this.alldata.percent_change = []; 
    
}

function Filter (name) {

    this.name = name
    this.display = name.replace('filter_','').replace(/_/g,' ').replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase(); });
    this.include = false;
    this.exclude = false;
    
}

function Chart() {
    
    this.series = [];
    this.yearFrom = 0;
    this.yearTo = 0;
    this.timePeriodsAvailable = [];
    this.stacked = false;
    this.scatter = false;
    this.chartType = "line";
    this.exportOption = 0;
    this.yaxes = [];
    this.timeSeries = "years";
    
}

function Saved(slug, imgsrc, options) {
    
    this.slug = slug;
    this.imgsrc = imgsrc;
    this.options = options;
    
}


//////////////////////////////////////// ANGULAR APP

var toolApp = angular.module('toolApp', []);

toolApp.controller('ToolController', ['$scope', '$http', '$timeout', function ($scope,$http,$timeout)
{
    
    // INIT VARS
    
    /*
    $scope.measures = [
        {"measure":"count","display":"Count"},
        {"measure":"percent_total","display":"Percent Total"},
        {"measure":"percent_change","display":"Percent Change"},
    ];
    */
    
    $scope.chart_types = [
        {"type":"line","display":"Line"},
        {"type":"spline","display":"Smooth Line"},
        {"type":"column","display":"Column"},
        {"type":"area","display":"Area"},
        {"type":"areaspline","display":"Smooth Area"},
        {"type":"stacked_area_count","display":"Stacked Area Count"},
        {"type":"stacked_area_percent_total","display":"Stacked Area Percent Total"},
        {"type":"stacked_column_count","display":"Stacked Column Count"},
        {"type":"stacked_column_percent_total","display":"Stacked Column Percent Total"},
        {"type":"scatter_plot","display":"Scatter Plot"},
        {"type":"scatter_plot_regression","display":"Scatter Plot With Regression"},
        ];
    
    $scope.yaxischoices = [
        {"num":0,"display":"primary"},
        {"num":1,"display":"secondary"},
        {"num":2,"display":"tertiary"}
    ];
        
    $scope.export_options = [
        {"num":0,"display":""},
        {"num":1,"display":"Download PNG"},
        {"num":2,"display":"Download JPEG"},
        {"num":3,"display":"Download SVG"},
        {"num":4,"display":"Download PDF"},
        {"num":5,"display":"Copy Image URL"},
        {"num":6,"display":"Copy Tool URL"},
        {"num":7,"display":"Copy Embed Code"}
    ];
    
    
    $scope.instances = [];
    
    $scope.recent = [];
    
    $scope.preserve_date_range = false;
    
    /* 
    if (!$scope.chart.timeSeries) {
        $scope.chart.timeSeries = "years";
    }
    */

    // LOAD SAVED CHARTS FROM DB BY USER COOKIE VAL

    $http.get(baseUrl + '/api/charts/' + $("#user").val() ).success(function(data){
    
        saved = [];
        angular.forEach(data, function (chart, index) {
            item = new Saved(chart.slug, baseUrl + '/charts/' + chart.slug, JSON.parse(chart.options));
            saved.unshift(item);
        });
        $scope.saved = saved;
        
    }); 
    
    
    // OPEN THE SEARCH BOX I CLICKED, CLOSE OTHERS
    
    if( event.target.tagName === "LABEL" ) {
         alert('clicked');
    }
    
    
    $scope.budgetPickerLabel = function(e) {
              
       angular.element('div.picker:visible').slideToggle('fast','linear');        
       angular.element(e.target).next('div').slideToggle('fast','linear');
               
    };
    
    
    
    // POLICY FACETED SEARCH (left sidebar)
          
    $http.get(baseUrl + '/api/projects').success(function(data){
        
            $scope.countries = data;
                        
            $timeout(function() {
                project = getQueryVariable('project');
                if (project) {
                    checkbox = angular.element('#' + project);
                    if (checkbox) checkbox.trigger('click');
                }
            }, 500);
            
    });
    
    $http.get(baseUrl + '/api/categories').success(function(data){
        $scope.categories = data;
    });
    
    $http.get(baseUrl + '/api/topics').success(function(data){
        
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
    
    $http.get(baseUrl + '/api/datasets').success(function(data){
    
        $scope.datasets = data;
    
    });
              
    $scope.doFacets = function() { 
        
        
        //console.log($scope.datasets);
        
        $scope.results = [];
        
        var cats = [];
        angular.element('#categories input:checked').each(function () {
            var cat = $(this).attr('catid');
            cats.push(cat);
        });
        
        angular.forEach($scope.datasets, function (dataset, index) {
            if (cats.indexOf(dataset.category.toString()) > -1) {
                angular.element('#projects input:checked').each(function () {
                    var country = $(this).attr('country');

                    angular.element('.choose_topic:checked').each(function () {
                       
                       var $this = $(this);
                       if ($this.length) {
                        var selText = $this.next('span').text();
                        var parentText = $this.closest('ol').siblings('label').children('span').text();
                        if (parentText.length) {
                            selText = parentText + ': ' + selText;
                        }
                        
                        if ( $this.attr('topic') ) {
                            topic = $this.attr('topic');
                            sub = false;
                        } else if ( $this.attr('subtopic') ) {
                            topic = $this.attr('subtopic');
                            sub = true;
                        }
                        
                        
                        if (country == dataset.country) {
                            
                            console.log(dataset.aggregation_level);
                            
                            // ADD TO SEARCH RESULTS
                            dataset_name = dataset.country + ': ' + dataset.name + ' #' + selText;
                            var searchResult = new Series(dataset.id,topic,dataset_name,dataset.filters,sub,dataset.unit,dataset.aggregation_level,false);
                            $scope.results.push(searchResult);
                                           
                        }
                       }
                    });
                });
            }
        });
        
    }
    
    $scope.noResults = function() {
        
       // console.log($scope.results);
        
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
        
        return angular.element('#projects input[type="checkbox"]:checked').length;
        
    }
    
    $scope.categoryCount = function() {
        
        return angular.element('#categories input[type="checkbox"]:checked').length;
        
    }
    
    $scope.topicCount = function() {
        
        return angular.element('#topics input.choose_topic:checked').length;
        
    }
    
    
    
    // BUDGET FACETED SEARCH (left sidebar)
    
    
    $http.get(baseUrl + '/api/budgetprojects').success(function(data){
        
        console.log(data);
        
        for (i = 0; i < data.length; ++i) {
            for (j = 0; j < data[i].datasets.length; ++j) {
                if (data[i].datasets[j].topics) { 
                    data[i].datasets[j].topics = data[i].datasets[j].topics;
                }
            }
        }
        
        $scope.budgetProjects = data;
                        
    });
    
    
    $scope.budgetCategories = [
        {"category_id": 1, "id": 1, "name": "Appropriations"}, 
        {"category_id": 2, "id": 2, "name": "Expeditures"}, 
        {"category_id": 3, "id": 3, "name": "Miscellaneous"}, 
    ];
    
    /*
    $http.get(baseUrl + '/api/datasets/budget').success(function(data){
        
        retval = data;
        for (index = 0; index < data.length; ++index) {
            data[index];
            retval[index].topics = JSON.parse(data[index].topics);
        }
        
        $scope.budgetDatasets = retval;
        
       // console.log('hi');
       // console.log(retval);
        
    
    });
    */
    
    $scope.budgetProjectCount = function() {
        
        //return angular.element('#projects input[type="checkbox"]:checked').length;
        return 0;
        
    }
    
    $scope.budgetTopicCount = function() {
        
        //return angular.element('#topics input.choose_topic:checked').length;
        return 0;
    }

    $scope.budgetResults = [];

    $scope.doBudgetResults = function(dataset,topic,name,sub) { 
                  
        var found_it = false;
        /*
        var idx;
        for (idx = 0; idx < $scope.budgetResults.length; idx++) {
            if ($scope.budgetResults[idx].topic === topic.id && $scope.budgetResults[idx].dataset === dataset.id) {
                $scope.budgetResults.splice(idx, 1);
                found_it = true;
                break;
            }
        }
        */
        
        if ($scope.chart.series) {
            var idx;
            for (idx = 0; idx < $scope.chart.series.length; idx++) {
                if ($scope.chart.series[idx].topic === topic.id && $scope.chart.series[idx].dataset === dataset.id) {
                    $scope.removeFromChart(idx);
                    found_it = true;
                    break;
                }
            }
        }
        
        
        // is newly selected
        if (found_it==false) {            
          dataset_name = dataset.country + ': ' + dataset.name + ' #' + name;
          var obj = new Series(dataset.id,topic.id,dataset_name,dataset.filters,sub,dataset.unit,1,true);
          //obj.budget = true;
          $scope.addToChart(obj);
          //$scope.budgetResults.push(obj);
        }
        
        
    }
    
    
    $scope.clickBudgetProject = function(country, countryHasBudgetSeriesInChart) {
        
        if (countryHasBudgetSeriesInChart) {
            
            iterator = [];
            angular.copy($scope.chart.series,iterator);
            
            for (var i = 0, len = iterator.length; i < len; i++) {
                                
                if ( (iterator[i].name.split(':')[0] == country.name) &&  (iterator[i].budget==true) ) {
                
                    position = $scope.budgetTopicFoundInChart(iterator[i].dataset,iterator[i].topic);
                    $scope.removeFromChart(position);
                    
                    
                }
            }
            
        }
        
    }
    
    $scope.budgetProjectFoundInChart = function(country)
    {   
        for(var i = 0, len = $scope.chart.series.length; i < len; i++) {
            
            for(var j = 0, len2 = country.datasets.length; j < len2; j++) {
            
                if ($scope.chart.series[i].dataset == country.datasets[j].id) return true;
            
            }
            
        }
        return false;
    }
    
    $scope.budgetTopicFoundInChart = function(dataset, topic)
    {   
        for(var i = 0, len = $scope.chart.series.length; i < len; i++) {
            
            if ( ($scope.chart.series[i].dataset == dataset) &&  ($scope.chart.series[i].topic == topic) ) return i;
        }
        return -1;
    }
    
    
    $scope.lessThan = function( what ) {
        return function( item ) {
            return parseInt(item.value) < parseInt(what);
        };
    };
    
    $scope.greaterThan = function( what ) {
        return function( item ) {
            return parseInt(item.value) > parseInt(what);
        };
    };
    
    
    // ADD TO CHART
        
    $scope.addToChart = function(result) {
    	
    	if ($scope.chart.scatter) {
    	
    	    alert('Scatter plot chart type requires exactly two series.');
    	    
    	} else {
    	
            result.color = $scope.getRgbaColor();
        
            switch($scope.chart.chartType) {
    
                case "stacked_area_count":
                    result.type = "area";
                    result.measure = "count";
                    break;
                case "stacked_area_percent_total":
                    result.type = "area";
                    result.measure = "percent_total";
                    break;
                case "stacked_column_count":
                    result.type = "column";
                    result.measure = "count";
                    break;
                case "stacked_column_percent_total":
                    result.type = "column";
                    result.measure = "percent_total";
                    break;
                default:
                    result.type = $scope.chart.chartType;
            
            }
        
            $scope.chart.series.push(result);
            
            if (result.sub) {
                var url = baseUrl + '/api/measures/dataset/' + result.dataset + '/subtopic/' + result.topic;
            } else {
                var url = baseUrl + '/api/measures/dataset/' + result.dataset + '/topic/' + result.topic;
            }
            
            //console.log(url);
            
            $.getJSON(url, function (retval) {
            
                // async... find the right series and assign the data
                
                angular.forEach($scope.chart.series, function (series, index) { 
                    if (result.name == series.name) {
                        $scope.chart.series[index].alldata = retval;
                        //console.log($scope.chart.series[index].alldata);
                    }
                });
            
                // redraw the chart
                
                
            
                $scope.drawChart(); 
            
            });
		
		}
    	
    }
    
    // REMOVE FROM CHART
    
    $scope.removeFromChart = function(index) {
        
        if ($scope.chart.scatter) {
        
            alert('Scatter plot chart type requires exactly two series.');
        
        } else {
        
            // RESET TO DEFAULTS FOR NEXT ADD
            $scope.chart.series[index].measure = "count";
            $scope.chart.series[index].type = "line";
            $scope.chart.series[index].yaxis = 0;
            $scope.chart.series[index].measure_on_multiple_axes = false; 	
        
            // REMOVE FROM CHART
            $scope.chart.series.splice(index,1);
        
            // RESET CHART TYPE IF RESTRICTED
            if ( $scope.chart.stacked && $scope.chart.series.length == 1) {
                $scope.chart.stacked = false;
                $scope.chart.chartType = $scope.chart.series[0].type;   
            }
            if ($scope.chart.series.length == 0) {   
                $scope.chart.chartType = "line";
            }
        
            doSeriesRemain = $scope.chart.series.length > 0;            
            $scope.drawChart(doSeriesRemain); 
        
        } 
    	
    }
    
    // CHART TO OPTIONS
        
    $scope.chartToOptions = function() {
        
        if ($scope.chart.series.length > 0) {
            
            angular.element('#intro').hide();
            angular.element('#chart').show();
            
            // get years available for these series

            chartMax = 0;
            chartMin = 9999;
            
            angular.forEach($scope.chart.series, function (series, index) {            
                
                timePeriods = $scope.chart.timeSeries == "congresses" ? $scope.years_to_congresses(series.alldata.years) : series.alldata.years;
                
                thisMax = Math.max.apply(null, timePeriods);
                thisMin = Math.min.apply(null, timePeriods);

                chartMax = thisMax > chartMax ? thisMax : chartMax
                chartMin = thisMin < chartMin ? thisMin : chartMin

            });

            
            var timePeriodsAvailable = [];
            for (var i = chartMin; i <= chartMax; i++) {
                
                var obj = {};
                obj['value'] = i;
                if ($scope.chart.timeSeries == "congresses") {
                    var firstYear = ( i * 2 ) + 1787;
                    var secondYearAbbr = firstYear < 1999 ? firstYear - 1899 : firstYear - 1999;
                    if (secondYearAbbr < 10) secondYearAbbr = '0' + secondYearAbbr;
                    obj['display'] = firstYear + '-' + secondYearAbbr;     
                } else {
                    obj['display'] = i;
                }
            
                timePeriodsAvailable.push(obj);
            }
            
            //console.log(timePeriodsAvailable);
            
            $scope.chart.timePeriodsAvailable = timePeriodsAvailable;


            // set years selected to default if blank
            //if ($scope.chart.yearFrom == 0 || $scope.chart.yearFrom < chartMin ) $scope.chart.yearFrom = chartMin;
            //if ($scope.chart.yearTo == 0 || $scope.chart.yearTo > chartMax) $scope.chart.yearTo = chartMax;
            
            // set years selected if we haven't just changed year
            if (!$scope.preserve_date_range) {
                $scope.chart.yearFrom = chartMin;
                $scope.chart.yearTo = chartMax;
            }
            $scope.preserve_date_range = false;
            
            // get years selected
            yearsSelected = [];
            for (var yr = $scope.chart.yearFrom; yr <= $scope.chart.yearTo; yr++) {
                yearsSelected.push(yr);
            }
            $scope.chart.yearsSelected = yearsSelected;
            
            
            // CONSOLIDATE ON ONE AXIS IF STACKED
            
            /*
            if ($scope.chart.stacked) {
               
                angular.forEach($scope.chart.series, function (series, index) {
            
                    series.yaxis = 0;
            
                });
                
            }
            */
            
            
            if ($scope.chart.scatter) {
            
                options = angular.copy(scatterOptions);

                var tooples = [];
                for (var yr = $scope.chart.yearFrom; yr <= $scope.chart.yearTo; yr++) {
                    
                    idx1 = $scope.chart.series[0].alldata['years'].indexOf(yr);
                    idx2 = $scope.chart.series[1].alldata['years'].indexOf(yr);
                    
                    if ( (idx1 != -1) && (idx2 != -1) ) {
                    
                        var toople = {
                            name: yr,
                            x: $scope.chart.series[0].alldata['count'][idx1],
                            y: $scope.chart.series[1].alldata['count'][idx2]
                        }
                
                        tooples.push(toople);
                    
                    }
                
                }

                options.xAxis.title.text = $scope.chart.series[0].name;
                options.yAxis.title.text = $scope.chart.series[1].name;
                options.series[0].data = tooples;
            
                if ($scope.chart.chartType == 'scatter_plot_regression') {
                    options.series[0].regression = true;
                }
            
            } else {
        
                options = angular.copy(defaultOptions);                
             
                // GET Y AXES
        
                $scope.chart.yaxes = [];
        
                // if there is not a y-axis for this measure, add one!!
                
                angular.forEach($scope.chart.series, function (series, index) {

                    bExists = false;
                    angular.forEach($scope.chart.yaxes, function (ax, i) {
                        if (series.measure == ax.measure) {
                            bExists = true;
                        }
                    });
            
                    if (!bExists) {
                        $scope.chart.yaxes.push({"measure":series.measure});
                    }

                });
                
                
                //SERIES TO OPTIONS
        
                angular.forEach($scope.chart.series, function (series, index) {
                
                    // sort into yAxis by measure
                    for (var i = 0; i < $scope.chart.yaxes.length; i++) {
                       ax = $scope.chart.yaxes[i];
                       if (series.measure == ax.measure && series.measure_on_multiple_axes == false) {
                            series.yaxis = i;
                            break;
                        }
                    }
            
                    // in case series is manually assigned to additional axis with identical measure
                    if (!$scope.chart.yaxes[series.yaxis]) {
                        //$scope.chart.yaxes.push({"measure":series.measure,"label":series.unit});
                        $scope.chart.yaxes.push({"measure":series.measure});
                        series.yaxis = $scope.chart.yaxes.length - 1;
                    }
                    
                    
                    var chartdata = [];
                    var allTimePeriods = $scope.chart.timeSeries == "congresses" ? $scope.years_to_congresses(series.alldata['years']) : series.alldata['years'];
                    

                    if ($scope.chart.timeSeries == "congresses") {
                    
                        var dataThisMeasure = series.measure == "percent_change" ? $scope.percent_change_by_congress(series.alldata['count'],series.alldata['years'][0] % 2) : $scope.aggregate_by_congress(series.alldata[series.measure],series.alldata['years'][0] % 2);
                    
                    } else {
                        
                        var dataThisMeasure = series.alldata[series.measure];
                        
                    } 
                    
                    for (var yr = $scope.chart.yearFrom; yr <= $scope.chart.yearTo; yr++) {
                        
                        idx = allTimePeriods.indexOf(yr);
                           
                        if (idx == -1) {
                            chartdata.push(null);
                        } else {
                            chartdata.push(dataThisMeasure[idx]);
                        }
                        
                    }
                    
                    $scope.chart.series[index].chartdata = chartdata;
                    
                    var s = {
                        /*
                        trump: series.trump,
                        alldata: series.alldata,
                        measure: series.measure,
                        filters: series.filters
                        */
                        topic: series.topic,
                        dataset: series.dataset,
                        type: series.type,
                        name: series.name,
                        data: chartdata,
                        color: hex_colors[rgba_colors.indexOf(series.color)],
                        yAxis: series.yaxis,
                        unit: series.unit,
                        stickyTracking: false,
                        measure: series.measure
                    }

                    options.series.push(s);
        
                });        
                
                
                // CONSTRUCT X AXIS
        
                options.xAxis[0].categories = $scope.chart.yearsSelected;
                
                if ($scope.chart.timeSeries == "congresses") {
                     angular.forEach(options.xAxis[0].categories, function (session,idx) {
                        var firstYear = ( session * 2 ) + 1787;
                        var secondYearAbbr = firstYear < 1999 ? firstYear - 1899 : firstYear - 1999;
                        if (secondYearAbbr < 10) secondYearAbbr = '0' + secondYearAbbr;
                        options.xAxis[0].categories[idx] = firstYear + '-' + secondYearAbbr;
                     });
                     options.xAxis[0].labels.step = 1;
                }
     
                // CONSTRUCT Y AXES
    
                angular.forEach($scope.chart.yaxes, function (ax,index) {

                    axis = { 
                        title: {
                            text: $scope.getAxisTitle(index)
                        },
                        plotLines: [{
                            value: 0,
                            width: 1,
                            color: '#808080'
                        }]
                    };
                    if (index > 0) {
                        axis.opposite = true;
                    }
                    if (ax.measure != 'percent_change') {
                        axis.min = 0;
                    }
            
                    options.yAxis.push(axis);
            
                });   
        
                // HANDLE STACKING
        
                if ($scope.chart.stacked && $scope.chart.series[0].type == 'area') {
        
                    options.plotOptions.area["stacking"] = 'normal';
        
                } else if ($scope.chart.stacked && $scope.chart.series[0].type == 'column') {
                
                    options.plotOptions.column["stacking"] = 'normal';
            
                } else {
            
                    options.plotOptions.area["stacking"] = undefined;
                    options.plotOptions.column["stacking"] = undefined;

                }
            
        
            }

        } else {
        
            options = angular.copy(defaultOptions);
            angular.element('#intro').show();
            angular.element('#chart').hide();
            
        }
        
        options.CAP_chart = $scope.chart;
        
        return options;
        
    }
    
    // APPLY FILTERS
    
    $scope.applyFilters = function(series) {
        
		// have filters been checked?
		var params = [];
		angular.forEach(series.filters, function (filter, index) { 
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
		
				
        //var url = baseUrl + '/api/measures/dataset/' + series.dataset + '/topic/' + series.topic;
        
        if (series.sub) {
            var url = baseUrl + '/api/measures/dataset/' + series.dataset + '/subtopic/' + series.topic;
        } else {
            var url = baseUrl + '/api/measures/dataset/' + series.dataset + '/topic/' + series.topic;
        }
        
    
        if (params.length > 0) {
            url = url + "?" + params.join("&");
        }
    
        $.getJSON(url, function (retval) {                
            series.alldata = retval;
            $scope.closeSeriesModal(series);
            $scope.drawChart();
        });
        
    }
    
    
    $scope.changeYears = function() {
    
        $scope.preserve_date_range = true;
        $scope.drawChart();
        
    }
    
    
    // DRAW CHART
    
    $scope.drawChart = function(burnThumb) {
        
        // always burn a thumbnail unless we are told not to...
        burnThumb = typeof burnThumb !== 'undefined' ? burnThumb : true;
        
        options = $scope.chartToOptions();
        
        //console.log(options);
        
        theChart.destroy();
		theChart = new Highcharts.Chart(options);
		
		if (burnThumb) {
		
            var obj = {},
            exportUrl = 'http://104.237.136.8:8080/highcharts-export-web/';
            obj.options = JSON.stringify(options);
            obj.type = 'image/png';
            obj.async = true;
        
            // GET THUMBNAIL (& SLUG, from export server)
            $.ajax({
                type: 'post',
                url: exportUrl,
                data: obj,
                success: function (data) {
                
                    slug = data.substr(6,8) // slug is between 'files/' & '.png' in return value
                    $scope.chart.slug = slug;
                                
                    // ADD THUMBNAIL TO RECENT
                    item = new Saved(slug, exportUrl + data, obj.options);
                    $scope.recent.unshift(item);
                    $scope.$apply();
                
                }
            });
        
        }
        
	
    }      
    
    // CHART CONTROLS
    
    $scope.allSeriesSameType = function(oldType) {
        
        var theType;
        var theMeasure;
        var validation_err;
        
        $scope.preserve_date_range = true;
        
        switch($scope.chart.chartType) {
        
            case "stacked_area_count":

                if ($scope.chart.series.length < 2) {
                    validation_err = "This chart type requires at least two series!";
                } else {                
                    theType = "area";
                    theMeasure = "count";
                    $scope.chart.scatter = false;
                    $scope.chart.stacked = true;
                }
                
                break;
                
            case "stacked_area_percent_total":
                
                if ($scope.chart.series.length < 2) {
                    validation_err = "This chart type requires at least two series!";
                } else {   
                    theType = "area";
                    theMeasure = "percent_total";
                    $scope.chart.scatter = false;
                    $scope.chart.stacked = true;
                }
                
                break;
                
            case "stacked_column_count":
                
                if ($scope.chart.series.length < 2) {
                    validation_err = "This chart type requires at least two series!";
                } else {               
                    theType = "column";
                    theMeasure = "count";
                    $scope.chart.scatter = false;
                    $scope.chart.stacked = true;
                }
                
                break;
                
            case "stacked_column_percent_total":
                
                if ($scope.chart.series.length < 2) {
                    validation_err = "This chart type requires at least two series!";
                } else {   
                    theType = "column";
                    theMeasure = "percent_total";
                    $scope.chart.scatter = false;
                    $scope.chart.stacked = true;
                }
                
                break;
                
            case "scatter_plot":
                
                if ($scope.chart.series.length != 2) {
                    validation_err = "This chart type requires exactly two series!";
                } else {
                    $scope.chart.scatter = true;
                    $scope.chart.stacked = false;
                }
                
                break;
                
            case "scatter_plot_regression":
                
                if ($scope.chart.series.length != 2) {
                    validation_err = "This chart type requires exactly two series!";
                } else {   
                    $scope.chart.scatter = true;
                    $scope.chart.stacked = false;
                }
                
                break;
                
            
            default:
            
                theType = $scope.chart.chartType;
                $scope.chart.stacked = false;
                $scope.chart.scatter = false;
                
        }
        
        if (validation_err) {
            
            alert(validation_err);
            $scope.chart.chartType = oldType;
            
        } else {
        
            if (!$scope.chart.scatter) {
        
                angular.forEach($scope.chart.series, function (series, index) {
                   series.type = theType;  
                   if (theMeasure) series.measure = theMeasure;
                   if ($scope.chart.stacked) series.yaxis = 0;
                   
                });
        
            }
            
            $scope.drawChart(); 
        
        }
        
    }
    
    $scope.saveChart = function() {
        
        strOptions = JSON.stringify(options);
            
        // SAVE CHART
        resp = $.ajax({
            type: 'POST',
            url: '/charts/save/' + $("#user").val() + '/' + $scope.chart.slug,
            data: strOptions,
            success: function() {
                alert('Chart pinned!\n\nClick "Chart History" to reload.');
                item = new Saved( $scope.chart.slug, baseUrl + '/charts/' + $scope.chart.slug, strOptions );
                $scope.saved.unshift(item);
                $scope.$apply();
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) { 
                alert('Could not pin chart.  Already pinned?'); 
            }
             
        });
        
    }
    
    $scope.editSeries = function(series) {
        
        // APPLY FILTERS (back to the data well!! closes modal and draws chart on finish)
        $scope.preserve_date_range = true;
        $scope.applyFilters(series);
        
    };
    
    $scope.closeSeriesModal = function(series) {
        
        angular.element('#seriesoptions-'+ series.dataset + '-' + series.topic).foundation('reveal','close');
        
    };

    $scope.deletePinned = function(index) {
            
        if (confirm('Really unpin?')) {  
        
             // DELETE CHART
            resp = $.ajax({
                type: 'POST',
                url: '/charts/unpin/' +  $scope.saved[index].slug ,
                success: function() {
                    //alert('chart un-pinned!');
                    $scope.saved.splice(index,1);
                    $scope.$apply();
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) { 
                    alert('Could not unpin.'); 
                }
             
            });
        
        }
        
    }
    
    
    $scope.recallPinned = function(index) {
        
        $scope.chart.slug = $scope.saved[index].slug;
        $scope.chart = JSON.parse($scope.saved[index].options).CAP_chart;
        $scope.preserve_date_range = true;
        $scope.drawChart(false); 
    
    }
    
    
    $scope.recallRecent = function(index) {
        
        $scope.chart.slug = $scope.recent[index].slug;
        $scope.chart = JSON.parse($scope.recent[index].options).CAP_chart;
        $scope.preserve_date_range = true;
        $scope.drawChart(false);     
        
    }
    
    
    // Y-AXIS HELPERS
    
    $scope.choiceIsVisible = function(series) {
        
        return function( choice ) {  
        
            // DOES THIS CHOICE BELONG TO A DIFFERENT AXIS SCALED FOR A DIFFERENT MEASURE?
            
            var avail = true;
            
            angular.forEach($scope.chart.series, function (s, index) {
    
                if (s != series && s.yaxis == choice.num) {
 
                    if (s.measure != series.measure) {
                        
                        avail = false;
                
                    }
                }
                
            });
            
            var xtra = 0;
            
            // DO YOU NEED XTRA OPTION?? only if you are not the only series scaled to your measure
            //console.log('series with this measure:' + $scope.chart.series.filter(function (el) {return el.measure == series.measure;}).length)
            
            xtra = 1 ? $scope.chart.series.length != $scope.chart.yaxes.length : 0;
            
            return choice.num < $scope.chart.yaxes.length + xtra
            && avail;
            
        };
        
    }
    
    $scope.checkAxes = function(thisSeries) {
        
        angular.forEach($scope.chart.series, function (series, index) {
            
            if (series.measure == thisSeries.measure) {
                series.measure_on_multiple_axes = true;
            } 
            
            
            else {
                series.measure_on_multiple_axes = false;
            }
            
            
        });
        
         
    }
    
    $scope.getAxisTitle = function(axIndex) {
        
        var unitLabels = [];
        var measureLabel = false;
        
        angular.forEach($scope.chart.series, function (s,key) {
            if ( (s.yaxis == axIndex) && (unitLabels.indexOf(s.unit) == -1) ) {
                
                if (s.measure == 'count' || s.measure == 'amount') {
                    unitLabels.push(s.unit);
                } else {
                    measureLabel = s.measure.split('_').join(' ').capitalizeFirstLetter();
                }
  
            }
        });
        
        return measureLabel ? measureLabel : unitLabels.join(', ');
        
    }
    
    $scope.chartExport = function(option) {
        
        //var save = false;
    
        $scope.chart.exportOption = 0;
    
        switch(option) {

            case 1: //PNG
                theChart.exportChart(
                    {
                    type: 'image/png',
                    filename: $scope.chart.slug,
                    sourceWidth: 960,
                    },
                
                    {
                    /*legend:{
                        enabled: true,
                        align: 'left',
                        verticalAlign: 'top',
                        floating: true 
                    },*/
                    yAxis: [{
                    gridLineWidth: 0,
                    minorGridLineWidth: 0,
                    labels: {
                        enabled: false
                    },
                    title: {
                        text: $scope.chart.series[0].measure.split('_').join(' ').capitalizeFirstLetter()
                    }
                    }]
                    }
                );
                break;
            
            case 2: //JPEG
                theChart.exportChart(
                    {
                    type: 'image/jpeg',
                    filename: $scope.chart.slug,
                    sourceWidth: 960,
                    },
                
                    {
                    /*legend:{
                        enabled: true,
                        align: 'left',
                        verticalAlign: 'top',
                        floating: true 
                    },*/
                    yAxis: [{
                    gridLineWidth: 0,
                    minorGridLineWidth: 0,
                    labels: {
                        enabled: false
                    },
                    title: {
                        text: $scope.chart.series[0].measure.split('_').join(' ').capitalizeFirstLetter()
                    }
                    }]
                    }
                );
                break;
            
            case 3: //SVG
                theChart.exportChart(
                    {
                    type: 'image/svg+xml',
                    filename: $scope.chart.slug,
                    sourceWidth: 960,
                    },
                
                    {
                    /*legend:{
                        enabled: true,
                        align: 'left',
                        verticalAlign: 'top',
                        floating: true 
                    },*/
                    yAxis: [{
                    gridLineWidth: 0,
                    minorGridLineWidth: 0,
                    labels: {
                        enabled: false
                    },
                    title: {
                        text: $scope.chart.series[0].measure.split('_').join(' ').capitalizeFirstLetter()
                    }
                    }]
                    }
                );
                break;
            
            case 4: //PDF
                theChart.exportChart(
                    {
                    type: 'application/pdf',
                    filename: $scope.chart.slug,
                    sourceWidth: 960,
                    },
                
                    {
                    /*legend:{
                        enabled: true,
                        align: 'left',
                        verticalAlign: 'top',
                        floating: true 
                    },*/
                    yAxis: [{
                    gridLineWidth: 0,
                    minorGridLineWidth: 0,
                    labels: {
                        enabled: false
                    },
                    title: {
                        text: $scope.chart.series[0].measure.split('_').join(' ').capitalizeFirstLetter()
                    }
                    }]
                    }
                );
                break;
            
            case 5:
                window.prompt( "copy to clipboard: Ctrl+C, Enter", baseUrl + "/charts/" + $scope.chart.slug );
               // save = true;
                break;
            
            case 6:
                window.prompt( "copy to clipboard: Ctrl+C, Enter", baseUrl + "/tool/" + $scope.chart.slug );
               // save = true;
                break;
                
            case 7:
                $('#embed_code').foundation('reveal', 'open');
               // save = true;
                break;
                
            default:
    
        }
        
      //  if (save) {
        
            strOptions = JSON.stringify(options);
            
            // SAVE CHART, UNPINNED
            resp = $.ajax({
                type: 'POST',
                url: '/charts/saveunpinned/' + $("#user").val() + '/' + $scope.chart.slug ,
                data: strOptions,
                success: function() { },
                error: function(XMLHttpRequest, textStatus, errorThrown) { 
                    alert('Error saving chart.'); 
                }
             
            });
        
      //  }

        
    }
    
    
    // CLEAR CHART
        
    $scope.clearChart = function() {
        
        $scope.clearSearch();
        $scope.chart = new Chart();
        $scope.drawChart(false);
        
    }
    
    
    $scope.clearSearch = function() {
        
        
        $scope.results = [];
        
        angular.element('div.picker input:checkbox').each(function() {
            $(this).removeAttr('checked');
        });
        
        /*
        angular.element('#categories input:checked').each(function () {
            var cat = $(this).attr('catid');
            cats.push(cat);
        });
        */
        
    
    }
    
    // HELPERS
      
    $scope.clickInclude = function(filter) {
        
        if (filter.include == true) filter.exclude = false;
    
    }  
      
    $scope.clickExclude = function(filter) {
        
        if (filter.exclude == true) filter.include = false;
    
    }  
            
    $scope.isSelected = function (thisname) {
    	
    	var l = $scope.chart.series.length;
		for (var i = 0; i < l; i++) {
			if ($scope.chart.series[i].name == thisname) return true;
		}
    	return false;
    	
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
    
    $scope.openDrilldown = function(f,d,t,y) {
        
        drilldown(f,d,t,y);
        
    }
    
    
    // US CONGRESS HELPER METHODS
    
    $scope.years_to_congresses = function(data) {
        
        var new_data = [];
        for (var i = 0; i < data.length; i++) {
            
            var val = Math.round((data[i] - 1787) / 2);
            
            if ( (data[i] % 2 == 1) ) {
                
                if (typeof data[i + 1] === 'undefined') {
                
                } else {

                    new_data.push(val);
                
                }
            
            }
            
        }
        
        return new_data;
    
    }
    
    $scope.aggregate_by_congress = function(data,starts_odd) {
                    
        var new_data = [];
        
        for (var i = 0; i < data.length; i++) {
        
            if (i % 2 == starts_odd) {
                
                var idx = starts_odd == 1 ? i - 1 : i + 1;
                
                if (idx >= 0 && (data[idx+1] != null) ) {
                    var val = (data[idx] + data[idx+1]);
                    new_data.push(val);
                } else {
                    new_data.push(null);
                }

            }
        }
        
        return new_data;
    
    }
    
    $scope.percent_change_by_congress = function(preAggCount,starts_odd) {
        
        count = $scope.aggregate_by_congress(preAggCount,starts_odd);
        
        percent_change = [];
        
        for (var i = 0; i < count.length; i++) {
            pc = (count[i - 1] > 0) ? (count[i] - count[i - 1]) / count[i - 1] * 100 : null;
            if (pc != null) {
                percent_change.push(pc);
            } else {
                percent_change.push(null);
            }
        }
        
        return percent_change;
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
    // theScope.chart.chartFromOptions(options);
    if (typeof options.CAP_chart == 'undefined') {
        options.CAP_chart = new Chart();
    }
    
    theScope.chart = options.CAP_chart;
    
    //console.log(options.CAP_chart);
    
    // send options to highcharts
    theChart = new Highcharts.Chart(options);

    $('h5.picker-label').click(function(e) {
    
        e.preventDefault();
        $('div.picker:visible').slideToggle('fast','linear');
        $(this).next('div').slideToggle('fast','linear');
        
        
    });
    
    $('a.coming-soon').click(function(e) {
        e.preventDefault();
        alert('Feature coming soon!');
    });
    
               
});


//////////////////////////////////////////////////////////////////////// UTILS

var clickPoint = function(event) {
                    
    if ( $('a[href="#data-view"]').attr('aria-selected') == "true" ) { 
        
        drilldown(
        this.series.userOptions.filters,
        this.series.userOptions.dataset,
        this.series.userOptions.topic,
        this.category);

    } else {

        $('#seriesoptions-'+ this.series.userOptions.dataset + '-' + this.series.userOptions.topic).foundation('reveal', 'open');

    }
}


var tooltipFormatter = function() {

   // return '<center><b>' + this.x + '</b><br/>' + this.series.name.split(': ').join(':<br/>').split(' #').join('<br/>#') + '<br/><b>' + this.y + '</b></center>';
   // return '<center><b>' + this.x + '</b><br/>' + this.series.name.split(': ')[0] + ' #' + this.series.name.split('#')[1] + '<br/><b>' + this.y + ' ' + this.series.userOptions.unit + '</b></center>';
     
   //  console.log(this);
     
     if (this.series.userOptions.measure == 'count' || this.series.userOptions.measure == 'amount') {
        var label = this.series.userOptions.unit;
     } else {
        var label = '%';
     }
     
     
     return '<center><b>' + this.x + '</b><br>' + this.y + ' ' + label + '</center>';

}

var drilldown = function(filters,dataset,topic,year) {
    
    // have filters been checked?
    var params = [];
    angular.forEach(filters, function (filter, index) { 
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
    
    var url = baseUrl + "/api/instances/" + dataset + "/" + topic + "/" + year;
    
    if (params.length > 0) {
        url = url + "?" + params.join("&");
    }
    
    $.get(url, function( data ) {
        
        theScope.instances = JSON.parse(data);
        theScope.$apply();
        $('#datapoints').foundation('reveal', 'open');
        
    });

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

function getQueryVariable(variable)
{
       var query = window.location.search.substring(1);
       var vars = query.split("&");
       for (var i=0;i<vars.length;i++) {
               var pair = vars[i].split("=");
               if(pair[0] == variable){return pair[1];}
       }
       return(false);
}
