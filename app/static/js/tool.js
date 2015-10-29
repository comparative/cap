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
    this.yaxis = 0;
    this.measure_on_multiple_axes = false;
    
    this.color = undefined;
    
    this.alldata = [];
    this.chartdata = [];
    this.alldata.years = [];
    this.alldata.count = [];
    this.alldata.percent_total = [];
    this.alldata.percent_change = [];
    
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
    this.yearsAvailable = [];
    this.stacked = false;
    this.scatter = false;
    this.chartType = "line";
    this.exportOption = 0;
    this.yaxes = [];
    
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
    
     $scope.budgetCountries = [
        {"id":"1","name":"US","topics":[{"id":"2","name":"Money","subtopics":[{"id":"23","name":"Tons of money"},{"id":"24","name":"Wads of money"}]},{"id":"3","name":"Pain"},{"id":"4","name":"Church"}]},
        {"id":"8","name":"Brasil","topics":[{"id":"5","name":"Money"},{"id":"6","name":"Pain","subtopics":[{"id":"63","name":"Emotional"},{"id":"64","name":"Referred"}]},{"id":"7","name":"Sleep"}]},
        {"id":"3","name":"Hungary","topics":[{"id":"8","name":"Sleep","subtopics":[{"id":"85","name":"Deep Sleep"},{"id":"86","name":"Naps"}]},{"id":"9","name":"Pain"},{"id":"10","name":"Church","subtopics":[{"id":"33","name":"Popes"},{"id":"34","name":"Steeples"}]}]},
    ];
    
    $scope.budgetCategories = [
        {"category_id": 1, "id": 1, "name": "Appropriations"}, 
        {"category_id": 2, "id": 2, "name": "Expeditures"}, 
        {"category_id": 3, "id": 3, "name": "Miscellaneous"}, 
    ];
    
    /*
    $scope.budgetDatasets = [
        {"category": 1, "country": "Denmark", "id": 37, "filters": "[\"filter_opening_debate_etc\", \"filter_eu\"]", "name": "Accounts"}, 
        {"category": 1, "country": "UK", "id": 46, "filters": "[]", "name": "Acts"}, 
        {"category": 1, "country": "Pennsylvania", "id": 22, "filters": "[\"filter_act\", \"filter_veto\", \"filter_lineitem\", \"filter_overridden\", \"filter_nosignature\", \"filter_signed\", \"filter_taxes\", \"filter_elderly\"]", "name": "Bills"},
        {"category": 1, "country": "Denmark", "id": 45, "filters": "[\"filter_eu\"]", "name": "Bills"}, 
        {"category": 1, "country": "belgium", "id": 18, "filters": "[]", "name": "Bills"}, 
        {"category": 3, "country": "belgium", "id": 86, "filters": "[]", "name": "Blah"}, 
        {"category": 1, "country": "US", "id": 24, "filters": "[]", "name": "CQ Almanac"}, 
        {"category": 3, "country": "belgium", "id": 76, "filters": "[]", "name": "DS"}, 
        {"category": 2, "country": "US", "id": 27, "filters": "[]", "name": "Exec Orders"}, 
        {"category": 1, "country": "Florida", "id": 65, "filters": "[]", "name": "Florida Bills 2011"}, 
        {"category": 2, "country": "belgium", "id": 19, "filters": "[]", "name": "Gov Agree"}, 
        {"category": 3, "country": "Brazil ", "id": 85, "filters": "[]", "name": "hear"}, 
        {"category": 1, "country": "Pennsylvania", "id": 73, "filters": "[\"filter_budget\", \"filter_harrisburg\"]", "name": "Hearings"}, 
        {"category": 1, "country": "US", "id": 20, "filters": "[\"filter_referral\", \"filter_approp\", \"filter_agency\", \"filter_program\", \"filter_admin\"]", "name": "Hearings"}, 
        {"category": 1, "country": "Denmark", "id": 42, "filters": "[\"filter_eu\", \"filter_concluding_debate_etc\", \"filter_debate_is_carried_through \"]", "name": "Interpellations"}, 
        {"category": 1, "country": "Hungary", "id": 67, "filters": "[]", "name": "Interpellations"}, 
        {"category": 1, "country": "Switzerland", "id": 32, "filters": "[\"filter_enacted_legislation\"]", "name": "Legislation"}, 
        {"category": 3, "country": "belgium", "id": 33, "filters": "[]", "name": "Manifestos"}, 
        {"category": 3, "country": "Denmark", "id": 40, "filters": "[\"filter_eu\"]", "name": "Manifestos"}, 
        {"category": 2, "country": "Switzerland", "id": 29, "filters": "[\"filter_swiss_news\", \"filter_swiss_subnational\"]", "name": "Media"}, 
        {"category": 1, "country": "Denmark", "id": 41, "filters": "[\"filter_eu\"]", "name": "Motions"}, 
        {"category": 3, "country": "Brazil ", "id": 84, "filters": "[]", "name": "ooo"}, 
        {"category": 2, "country": "Denmark", "id": 44, "filters": "[\"filter_eu\"]", "name": "PM Closing Speeches"}, 
        {"category": 2, "country": "Denmark", "id": 43, "filters": "[\"filter_eu\"]", "name": "PM Opening Speeches"}, 
        {"category": 1, "country": "US", "id": 25, "filters": "[\"filter_democrat\", \"filter_vetoed\", \"filter_commemorative\"]", "name": "Public Laws"}, 
        {"category": 1, "country": "belgium", "id": 74, "filters": "[]", "name": "Q & I"}, 
        {"category": 1, "country": "Denmark", "id": 39, "filters": "[\"filter_eu\"]", "name": "Questions Hour"}, 
        {"category": 1, "country": "Denmark", "id": 38, "filters": "[\"filter_eu\"]", "name": "Questions Wednesdays"}, 
        {"category": 1, "country": "Switzerland", "id": 31, "filters": "[]", "name": "Reports"}, 
        {"category": 1, "country": "US", "id": 26, "filters": "[]", "name": "Roll Call"}, 
        {"category": 2, "country": "US", "id": 21, "filters": "[]", "name": "SOTU"}, 
        {"category": 2, "country": "UK", "id": 35, "filters": "[\"filter_policy\", \"filter_executive_agenda\"]", "name": "Speeches"}, 
        {"category": 1, "country": "US", "id": 28, "filters": "[\"filter_vac\", \"filter_dis\", \"filter_gd\"]", "name": "Supreme Court"}, 
        {"category": 4, "country": "belgium", "id": 75, "filters": "[]", "name": "TV"}, 
        {"category": 5, "country": "Switzerland", "id": 30, "filters": "[\"filter_enacted_legislation\", \"filter_referendum_mandatory\", \"filter_referendum_optional\", \"filter_popular_initiative\", \"filter_counter_proposal\"]", "name": "Votes"}
    ];
    */
    
    
    $scope.measures = [
        {"measure":"count","display":"Count"},
        {"measure":"percent_total","display":"Percent Total"},
        {"measure":"percent_change","display":"Percent Change"},
    ];
    
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
        {"num":1,"display":"Download Image"},
        {"num":2,"display":"Copy Image URL"},
        {"num":3,"display":"Copy Tool URL"},
        {"num":4,"display":"Copy Embed Code"}
    ];
    
    
    $scope.instances = [];
    
    $scope.recent = [];
    
    $scope.preserve_date_range = false;

    // LOAD SAVED CHARTS FROM DB BY USER COOKIE VAL

    $http.get(baseUrl + '/api/charts/' + $("#user").val() ).success(function(data){
    
        saved = [];
        angular.forEach(data, function (chart, index) {
            item = new Saved(chart.slug, baseUrl + '/charts/' + chart.slug, JSON.parse(chart.options));
            saved.unshift(item);
        });
        $scope.saved = saved;
        
    });
    
    
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
        
        return angular.element('#projects input[type="checkbox"]:checked').length;
        
    }
    
    $scope.categoryCount = function() {
        
        return angular.element('#categories input[type="checkbox"]:checked').length;
        
    }
    
    $scope.topicCount = function() {
        
        return angular.element('#topics input.choose_topic:checked').length;
        
    }
    
    
    
    // BUDGET FACETED SEARCH (left sidebar)
    
    $http.get(baseUrl + '/api/datasets/budget').success(function(data){
    
        $scope.budgetDatasets = data;
    
    });
    
    $scope.budgetProjectCount = function() {
        
        //return angular.element('#projects input[type="checkbox"]:checked').length;
        return 0;
        
    }
    
    $scope.budgetTopicCount = function() {
        
        //return angular.element('#topics input.choose_topic:checked').length;
        return 0;
    }

    $scope.doBudge = function() { 
        
        $scope.budgetResults = [];
        
        var budgetCats = [];
        angular.element('#budget_categories input:checked').each(function () {
            var cat = $(this).attr('catid');
            budgetCats.push(cat);
        });
        
        angular.forEach($scope.budgetDatasets, function (dataset, index) {
        
            if (budgetCats.indexOf(dataset.category.toString()) > -1) {
        
                var country = $(this).attr('country');
                
               // var country = 'Country Music Hall of Fame';
                                
                angular.element('.choose_budget_topic:checked').each(function () {
                   var $this = $(this);
                   if ($this.length) {
                    var selText = $this.next('span').text();
                    var parentText = $this.closest('ol').siblings('label').children('span').text();
                    if (parentText.length) {
                        selText = parentText + ': ' + selText;
                    }
                    var subtopic = $this.attr('subtopic');
                    //if (country == dataset.country) {
                    
                        // ADD TO SEARCH RESULTS
                        dataset_name = dataset.country + ': ' + dataset.name + ' #' + selText;
                        var searchResult = new Series(dataset.id,subtopic,dataset_name,JSON.parse(dataset.filters));
                        $scope.budgetResults.push(searchResult);
                                       
                    //}
                   }
                });
                  
            }
            
        });
        
    }
    
    
    $scope.lessThan = function( what ) {
        return function( item ) {
            return parseInt(item) < parseInt(what);
        };
    };
    
    $scope.greaterThan = function( what ) {
        return function( item ) {
            return parseInt(item) > parseInt(what);
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
            
            var url = baseUrl + '/api/measures/dataset/' + result.dataset.toString() + '/topic/' + result.topic.toString();
        
            $.getJSON(url, function (retval) {
            
                // async... find the right series and assign the data
                
                angular.forEach($scope.chart.series, function (series, index) { 
                    if (result.name == series.name) {
                        $scope.chart.series[index].alldata = retval;
                        console.log($scope.chart.series[index].alldata);
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

                thisMax = Math.max.apply(null, series.alldata.years);
                thisMin = Math.min.apply(null, series.alldata.years);

                chartMax = thisMax > chartMax ? thisMax : chartMax
                chartMin = thisMin < chartMin ? thisMin : chartMin

            });

            
            var yearsAvailable = [];
            for (var i = chartMin; i <= chartMax; i++) {
                yearsAvailable.push(i);
            }
            $scope.chart.yearsAvailable = yearsAvailable;


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
                        //series.yaxis = index;
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
                        $scope.chart.yaxes.push({"measure":series.measure});
                        series.yaxis = $scope.chart.yaxes.length - 1;
                    }
                    
                    
                    var chartdata = [];
                    for (var yr = $scope.chart.yearFrom; yr <= $scope.chart.yearTo; yr++) {
                        
                        idx = series.alldata['years'].indexOf(yr);
                           
                        if (idx == -1) {
                            chartdata.push(null)
                        } else {
                            chartdata.push(series.alldata[series.measure][idx]);
                        }
                        
                    }
                    
                    console.log('fiddlywinkos');
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
                    }

                    options.series.push(s);
        
                });        
                
                
                // CONSTRUCT X AXIS
        
                options.xAxis[0].categories = $scope.chart.yearsSelected;
     
     
                // CONSTRUCT Y AXES
    
                angular.forEach($scope.chart.yaxes, function (ax,index) {

                    axis = { 
                        title: {
                            text: ax.measure.split('_').join(' ').capitalizeFirstLetter()
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
        
        console.log($scope.chart);
        
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
		
				
        var url = baseUrl + '/api/measures/dataset/' + series.dataset + '/topic/' + series.topic;
    
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
        //console.log(options);
            
        // SAVE CHART
        resp = $.ajax({
            type: 'POST',
            url: '/charts/save/' + $("#user").val() + '/' + $scope.chart.slug,
            data: strOptions,
            success: function() {
                alert('Chart pinned!\n\nClick "View History" to reload chart.');
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
    
    
    $scope.chartExport = function(option) {
        
        //var save = false;
    
        $scope.chart.exportOption = 0;
    
        switch(option) {

            case 1:
                theChart.exportChart(
                    {
                    type: 'img/png',
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
  
            case 2:
                window.prompt( "copy to clipboard: Ctrl+C, Enter", baseUrl + "/charts/" + $scope.chart.slug );
               // save = true;
                break;
            
            case 3:
                window.prompt( "copy to clipboard: Ctrl+C, Enter", baseUrl + "/tool/" + $scope.chart.slug );
               // save = true;
                break;
                
            case 4:
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
    
    console.log(options.CAP_chart);
    
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


var tooltipFormatter = function(event) {
    return '<center><b>' + this.x + '</b><br/>' + this.series.name.split(': ').join(':<br/>').split(' #').join('<br/>#') + '<br/><b>' + this.y + '</b></center>';
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
