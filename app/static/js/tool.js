//////////////////////////////////// CLASS-LIKE THANGS

function Series (dataset,topic,name,filters,sub,unit,aggregation_level,budget) {

    this.dataset = dataset;
    this.topic = topic;
    this.name = name;
    this.sub = sub;
    this.budget = budget;
    this.agg = aggregation_level;
    
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
    //this.alldata.years = [];
    
    
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
    this.periodsSelected = [];
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

function Recent(key) {
    
    this.key = key;
    this.options = undefined;
    this.slug = undefined;
    this.imgsrc = undefined;    
    
}

//////////////////////////////////////// VUE APP

var toolApp = new Vue({

el: '#toolcontroller',

data: {
    
    pending:false,
    
    chart_types : [
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
        ],
        
    series_types : [
        {"type":"line","display":"Line"},
        {"type":"spline","display":"Smooth Line"},
        {"type":"column","display":"Column"},
        {"type":"area","display":"Area"},
        {"type":"areaspline","display":"Smooth Area"},
        ],

    yaxischoices : [
        {"num":0,"display":"primary"},
        {"num":1,"display":"secondary"},
        {"num":2,"display":"tertiary"}
    ],
        
    export_options : [
        {"num":0,"display":""},
        {"num":1,"display":"Download PNG"},
        {"num":2,"display":"Download Clean PNG"},
        {"num":3,"display":"Download JPEG"},
        {"num":4,"display":"Download SVG"},
       /*{"num":5,"display":"Download PDF"},*/
        {"num":6,"display":"Copy Image URL"},
        {"num":7,"display":"Copy Tool URL"},
        {"num":8,"display":"Copy Embed URL"},
    ],
    
    instances : [{"source":'',"description":''}],
    
    recent : [],
    
    preserve_date_range : false,
    
    budgetCategories : [
        {"category_id": 1, "id": 1, "name": "Appropriations"}, 
        {"category_id": 2, "id": 2, "name": "Expeditures"}, 
        {"category_id": 3, "id": 3, "name": "Miscellaneous"}, 
    ],
    
    budgetResults : [],
    
    budgetProjects: [],
    
    results: [],
    
    saved: [],
    
    countries: [],
    
    categories: [],
    
    //categories_filtered: [],
    
    topics: [],
    
    datasets: [],
    
    chart: {},
    
    pending: false,
    
},

created() {
    
    // LOAD SAVED CHARTS FROM DB BY USER COOKIE VAL
    
    const self = this;
    
    axios.get(baseUrl + '/api/charts/' + $("#user").val() ).then(function(response){
      
      var data = response.data;
            
      saved = [];
      data.forEach(function (chart, index) {
          item = new Saved(chart.slug, baseUrl + '/charts/' + chart.slug, chart.options);
          saved.unshift(item);
      });
      self.saved = saved;
  
    });

    axios.get(baseUrl + '/api/projects').then(function(response){
          
          self.countries = response.data;          
               
          window.setTimeout(function() {
              project = getQueryVariable('project');
              if (project) {
                  checkbox = jQuery('#' + project);
                  if (checkbox) checkbox.trigger('click');
              }
          }, 500);
          
      
    });

    axios.get(baseUrl + '/api/categories').then(function(response){
      
      var data = response.data;
      
      // remove budget!!  because we have a tab for it!! it's kind of a category but kind of not!!
      var removeIndex = data.map(function(item) { return item.name; }).indexOf("Budget");
      removeIndex > -1 && data.splice(removeIndex, 1);
      self.categories = data;
  
    });

    axios.get(baseUrl + '/api/topics').then(function(response){
        
        var data = response.data;
        
        
        
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
            row.isOpen = false;
            retval.push(row);
        }
        
        self.topics = retval;
  
    });

    axios.get(baseUrl + '/api/datasets').then(function(response){

        self.datasets = response.data;
    
    });  
    
    axios.get(baseUrl + '/api/budgetprojects').then(function(response){
        
        var data = response.data;
        
        // add stub for UI open state
        
        for (i = 0; i < data.length; ++i) {
            for (j = 0; j < data[i].datasets.length; ++j) {
                if (data[i].datasets[j].topics) {
                    for (k = 0; k < data[i].datasets[j].topics.length; ++k) { 
                      data[i].datasets[j].topics[k].isOpen = false;
                    }
                }
            }
        }

        self.budgetProjects = data;
                        
    });  

},

methods: {
    
    drill() {
      
      return this.$refs.drilldown;
      
    },
    
    // POLICY FACETED SEARCH (left sidebar)
        
    doFacets() { 
                
        this.results = [];
        
        var cats = [];
        jQuery('#categories input:checked').each(function () {
            var cat = $(this).attr('catid');
            cats.push(cat);
        });
        
        const self = this;
        
        this.datasets.forEach(function (dataset, index) {
            if (cats.indexOf(dataset.category.toString()) > -1) {
                jQuery('#projects input:checked').each(function () {
                    var country = $(this).attr('country');

                    jQuery('.choose_topic:checked').each(function () {
                       
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
                            
                            if (!sub || dataset.subs_avail == true) {
                            
                                // ADD TO SEARCH RESULTS
                                dataset_name = dataset.country + ': ' + dataset.name + ' #' + selText;
                                var searchResult = new Series(dataset.id,topic,dataset_name,dataset.filters,sub,dataset.unit,dataset.aggregation_level,false);
                                self.results.push(searchResult);
                            
                            }
                                           
                        }
                       }
                    });
                });
            }
        });
        
        if (jQuery('#projects input:checked').length == 0) {
            jQuery('#categories input:checkbox').removeAttr('checked');
        }
        
    },
    
    // only see categories that are available for chosen projects
    categories_filtered() {
                
        retval = [];
        
        const self = this;
        
        this.categories.forEach(function (category) {
        
          jQuery('#projects input:checked').each(function () {
              var country = $(this).attr('country');
              self.datasets.forEach(function (dataset, index) {
                  if ( 
                  (category.category_id == dataset.category) &&
                  (dataset.country == country) &&
                  (retval.indexOf(category) === -1)
                  ) {
                      retval.push(category);
                  }
              });
          });

        });
        
        return retval;
    
    },
    
    
    // BUDGET FACETED SEARCH (left sidebar)
    
    doBudgetResults(dataset,topic,name,sub) { 
        
      //  if (this.pending == false) {
           
            var found_it = false;
            /*
            var idx;
            for (idx = 0; idx < this.budgetResults.length; idx++) {
                if (this.budgetResults[idx].topic === topic.id && this.budgetResults[idx].dataset === dataset.id) {
                    this.budgetResults.splice(idx, 1);
                    found_it = true;
                    break;
                }
            }
            */
        
            if (this.chart.series) {
                var idx;
                for (idx = 0; idx < this.chart.series.length; idx++) {
                    if (this.chart.series[idx].topic === topic.id && this.chart.series[idx].dataset === dataset.id) {
                        this.removeFromChart(idx);
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
              this.addToChart(obj);
              //this.budgetResults.push(obj);
            }
        
      //  }
        
        
    },
    
    clickBudgetProject(country, countryHasBudgetSeriesInChart) {
        
        if (countryHasBudgetSeriesInChart) {
            
            //iterator = [];
            //angular.copy(this.chart.series,iterator);
            
            iterator = JSON.parse(JSON.stringify(this.chart.series));
            
            for (var i = 0, len = iterator.length; i < len; i++) {
                                
                if ( (iterator[i].name.split(':')[0] == country.name) &&  (iterator[i].budget==true) ) {
                
                    position = this.budgetTopicFoundInChart(iterator[i].dataset,iterator[i].topic);
                    this.removeFromChart(position);
                    
                    
                }
            }
            
        }
        
    },
    
    budgetProjectFoundInChart(country) {   
        for(var i = 0, len = this.chart.series.length; i < len; i++) {
            
            for(var j = 0, len2 = country.datasets.length; j < len2; j++) {
            
                if (this.chart.series[i].dataset == country.datasets[j].id) return true;
            
            }
            
        }
        return false;
    },
    
    budgetTopicFoundInChart(dataset, topic) {   
        for(var i = 0, len = this.chart.series.length; i < len; i++) {
            
            if ( (this.chart.series[i].dataset == dataset) &&  (this.chart.series[i].topic == topic) ) return i;
        } 
        return -1;
    },
    
    budgetPickerLabel(e) {
              
       jQuery('div.picker:visible').slideToggle('fast','linear');        
       jQuery(e.target).next('div').slideToggle('fast','linear');
               
    },
        
    // ADD TO CHART
        
    addToChart(result) {
    	
      try {ga('send', 'event', 'Add Series to Chart', result.dataset, result.name);} catch (e) {console.log('No analytics.');}
    	
    	if (this.pending == false) {
    	    
    	    this.pending = true;
    	    
            // WHEN WE ADD *ANYTHING* TO A SCATTER, IT RUINS IT!!  GO BACK TO LINE
        
            if (this.chart.scatter) {
            
                this.chart.series.forEach(function (series, index) {
                        this.chart.series[index].type = "line";
                        this.chart.series[index].measure = result.agg == 2 ? "percent_total" : "count";
                });
            
               // alert('Scatter plot chart type requires exactly two series.');
               this.chart.scatter = false;
               this.chart.chartType = "line";
                
            }
        
            // WHEN WE ADD A DATASET WITH AGGREGATION LEVEL = "percent" ... to a stacked count ... change it to stacked percent
                
            if ( (this.chart.chartType== "stacked_area_count" || this.chart.chartType=="stacked_column_count") && (result.agg == 2 || result.budget == true)) {
            
                this.chart.series.forEach(function (series, index) {
                        this.chart.series[index].measure = "percent_total";
                });
            
                this.chart.chartType = this.chart.chartType=="stacked_area_count" ? "stacked_area_percent_total" : "stacked_column_percent_total";  
            }
        
        
            result.color = this.getRgbaColor();
    
            switch(this.chart.chartType) {

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
                    result.type = this.chart.chartType;
        
            }
    
            this.chart.series.push(result);
        
            if (result.sub) {
                var url = baseUrl + '/api/measures/dataset/' + result.dataset + '/subtopic/' + result.topic;
            } else {
                var url = baseUrl + '/api/measures/dataset/' + result.dataset + '/topic/' + result.topic;
            }
            
            const self = this;
            $.getJSON(url, function (retval) {
        
                // async... find the right series and assign the data
                
                self.chart.series.forEach(function (series, index) { 
                    if (result.name == series.name) {
                        self.chart.series[index].alldata = retval;
                    }
                });
        
                // redraw the chart
            
                self.drawChart(); 
                
                //this.pending = false;
        
            });
        
        }
    
    },
    
    // REMOVE FROM CHART
    
    removeFromChart(index) {
        
        if (this.pending == false) {
        
            this.pending = true;
        
            if (this.chart.scatter) {
            
                this.chart.scatter = false;
                this.chart.chartType = "line";
        
            }
        
            // RESET TO DEFAULTS FOR NEXT ADD
            this.chart.series[index].measure = this.chart.series[index].agg == 2 ? "percent_total" : "count";
            this.chart.series[index].type = "line";
            this.chart.series[index].yaxis = 0;
            this.chart.series[index].measure_on_multiple_axes = false; 	
            
            // UNCHECK FILTER CHECKBOXES
            this.chart.series[index].filters.forEach(function (filter, index) {
                filter.exclude = false;
                filter.include = false;
            });
          
            // REMOVE FROM CHART
            this.chart.series.splice(index,1);
    
            // RESET CHART TYPE IF RESTRICTED
            if ( this.chart.stacked && this.chart.series.length == 1) {
                this.chart.stacked = false;
                this.chart.chartType = this.chart.series[0].type;   
            }
            if (this.chart.series.length == 0) {   
                this.chart.chartType = "line";
            }
    
            doSeriesRemain = this.chart.series.length > 0;            
            this.drawChart(doSeriesRemain); 
        
        }
        
    },
    
    // CHART TO OPTIONS
        
    chartToOptions() {
        
        const self = this;
        
        if (self.chart.series.length > 0) {
            
            jQuery('#intro').hide();
            jQuery('#chart').show();
            
            // get years available for these series

            chartMax = 0;
            chartMin = 9999;
            
            self.chart.series.forEach(function (series, index) {            
                
                timePeriods = self.chart.timeSeries == "congresses" ? self.years_to_congresses(series.alldata.years) : series.alldata.years;
                
                selfMax = Math.max.apply(null, timePeriods);
                selfMin = Math.min.apply(null, timePeriods);

                chartMax = selfMax > chartMax ? selfMax : chartMax
                chartMin = selfMin < chartMin ? selfMin : chartMin

            });

            
            var timePeriodsAvailable = [];
            for (var i = chartMin; i <= chartMax; i++) {
                
                var obj = {};
                obj['value'] = i;
                if (self.chart.timeSeries == "congresses") {
                    var firstYear = ( i * 2 ) + 1787;
                    var secondYearAbbr = firstYear < 1999 ? firstYear - 1899 : firstYear - 1999;
                    if (secondYearAbbr < 10) secondYearAbbr = '0' + secondYearAbbr;
                    obj['display'] = firstYear + '-' + secondYearAbbr;     
                } else {
                    obj['display'] = i;
                }
            
                timePeriodsAvailable.push(obj);
            }
            
            self.chart.timePeriodsAvailable = timePeriodsAvailable;


            // set years selected to default if blank
            //if (self.chart.yearFrom == 0 || self.chart.yearFrom < chartMin ) self.chart.yearFrom = chartMin;
            //if (self.chart.yearTo == 0 || self.chart.yearTo > chartMax) self.chart.yearTo = chartMax;
            
            // set years selected if we haven't just changed year
            if (!self.preserve_date_range) {
                self.chart.yearFrom = chartMin;
                self.chart.yearTo = chartMax;
            }
            self.preserve_date_range = false;
            
            // get years selected
            yearsSelected = [];
            for (var yr = self.chart.yearFrom; yr <= self.chart.yearTo; yr++) {
                yearsSelected.push(yr);
            }
            self.chart.yearsSelected = yearsSelected;
            
                
            periodsSelected = [];
            timePeriodsAvailable.forEach(function (timePeriod, index) {
                if (timePeriod.value >= self.chart.yearFrom && timePeriod.value <= self.chart.yearTo) {
                    periodsSelected.push(timePeriod);
                }
            });
            self.chart.periodsSelected = periodsSelected;

            
            // CONSOLIDATE ON ONE AXIS IF STACKED
            
            /*
            if (self.chart.stacked) {
               
                self.chart.series.forEach(function (series, index) {
            
                    series.yaxis = 0;
            
                });
                
            }
            */
            
            
            if (self.chart.scatter) {
            
                //options = angular.copy(scatterOptions);
                options = JSON.parse(JSON.stringify(scatterOptions));
                
                var tooples = [];
                for (var yr = self.chart.yearFrom; yr <= self.chart.yearTo; yr++) {
                    
                    idx1 = self.chart.series[0].alldata['years'].indexOf(yr);
                    idx2 = self.chart.series[1].alldata['years'].indexOf(yr);
                    
                    if ( (idx1 != -1) && (idx2 != -1) ) {
                    
                        var toople = {
                            name: yr,
                            x: self.chart.series[0].alldata['count'][idx1],
                            y: self.chart.series[1].alldata['count'][idx2]
                        }
                
                        tooples.push(toople);
                    
                    }
                
                }

                options.xAxis.title.text = self.chart.series[0].name;
                options.yAxis.title.text = self.chart.series[1].name;
                options.series[0].data = tooples;
            
                if (self.chart.chartType == 'scatter_plot_regression') {
                    options.series[0].regression = true;
                }
            
            } else {
        
                //options = angular.copy(defaultOptions);                
                options = JSON.parse(JSON.stringify(defaultOptions));
                
                // GET Y AXES
        
                self.chart.yaxes = [];
        
                // if there is not a y-axis for self measure, add one!!
                
                self.chart.series.forEach(function (series, index) {

                    bExists = false;
                    self.chart.yaxes.forEach(function (ax, i) {
                        if (series.measure == ax.measure) {
                            bExists = true;
                        }
                    });
            
                    if (!bExists) {
                        self.chart.yaxes.push({"measure":series.measure});
                    }

                });
                
                
                //SERIES TO OPTIONS
        
                self.chart.series.forEach(function (series, index) {
                
                    // sort into yAxis by measure
                    for (var i = 0; i < self.chart.yaxes.length; i++) {
                       ax = self.chart.yaxes[i];
                       if (series.measure == ax.measure && series.measure_on_multiple_axes == false) {
                            series.yaxis = i;
                            break;
                        }
                    }
            
                    // in case series is manually assigned to additional axis with identical measure
                    if (!self.chart.yaxes[series.yaxis]) {
                        //self.chart.yaxes.push({"measure":series.measure,"label":series.unit});
                        self.chart.yaxes.push({"measure":series.measure});
                        series.yaxis = self.chart.yaxes.length - 1;
                    }
                    
                    
                    var chartdata = [];
                    var allTimePeriods = self.chart.timeSeries == "congresses" ? self.years_to_congresses(series.alldata['years']) : series.alldata['years'];
                    

                    if (self.chart.timeSeries == "congresses") {
                    
                        if (series.measure == "percent_change") {
                    
                            var dataselfMeasure = self.percent_change_by_congress(series.alldata['count'],series.alldata['years'][0] % 2) 
                        
                        } else if (series.measure == "percent_total") {
                            
                            var dataselfMeasure = self.percent_total_by_congress(series.alldata['percent_total'],series.alldata['years'][0] % 2);
                            
                        } else {
                        
                            var dataselfMeasure = self.aggregate_by_congress(series.alldata[series.measure],series.alldata['years'][0] % 2);
                        
                        }
                    
                    } else {
                        
                        var dataselfMeasure = series.alldata[series.measure];
                        
                    } 
                    
                    for (var yr = self.chart.yearFrom; yr <= self.chart.yearTo; yr++) {
                        
                        idx = allTimePeriods.indexOf(yr);
                           
                        if (idx == -1) {
                            chartdata.push(null);
                        } else {
                            chartdata.push(dataselfMeasure[idx]);
                        }
                        
                    }
                    
                    self.chart.series[index].chartdata = chartdata;
                    
                    var s = {
                        /*
                        trump: series.trump,
                        alldata: series.alldata,
                        measure: series.measure,
                        filters: series.filters
                        */
                        sub: series.sub,
                        agg: series.agg,
                        filters: series.filters,
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
        
                options.xAxis[0].categories = self.chart.yearsSelected;
                
                if (self.chart.timeSeries == "congresses") {
                     options.xAxis[0].categories.forEach(function (session,idx) {
                        var firstYear = ( session * 2 ) + 1787;
                        var secondYearAbbr = firstYear < 1999 ? firstYear - 1899 : firstYear - 1999;
                        if (secondYearAbbr < 10) secondYearAbbr = '0' + secondYearAbbr;
                        options.xAxis[0].categories[idx] = firstYear + '-' + secondYearAbbr;
                     });
                     options.xAxis[0].labels.step = 1;
                }
     
                // CONSTRUCT Y AXES
    
                self.chart.yaxes.forEach(function (ax,index) {

                    axis = { 
                        title: {
                            text: self.getAxisTitle(index)
                        },
                        plotLines: [{
                            value: 0,
                            width: 1,
                            color: '#808080'
                        }],
                        labels: {
                            formatter: function() {
                                return this.value;
                            }
                        }
                    };
                    if (index > 0) {
                        axis.opposite = true;
                    }
                    if (ax.measure != 'percent_change') {
                        axis.min = 0;
                        axis.minRange = 1;
                    }
            
                    options.yAxis.push(axis);
            
                });   
        
                // HANDLE STACKING
        
                if (self.chart.stacked && self.chart.series[0].type == 'area') {
        
                    options.plotOptions.area["stacking"] = 'normal';
        
                } else if (self.chart.stacked && self.chart.series[0].type == 'column') {
                
                    options.plotOptions.column["stacking"] = 'normal';
            
                } else {
            
                    options.plotOptions.area["stacking"] = undefined;
                    options.plotOptions.column["stacking"] = undefined;

                }
            
        
            }

        } else {
        
           // options = angular.copy(defaultOptions);
            options = JSON.parse(JSON.stringify(defaultOptions));
            
            jQuery('#intro').show();
            jQuery('#chart').hide();
            
        }
        
        options.CAP_chart = self.chart;
         
        if (options.plotOptions.series) options.plotOptions.series.point.events['click'] = clickPoint;
        options.tooltip.formatter = tooltipFormatter;
        
        return options;
        
    },
    
    // APPLY FILTERS
    
    applyFilters(series) {
        
      this.pending = true;
        
      // have filters been checked?
      var params = [];
      series.filters.forEach(function (filter, index) { 
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
      
      const self = this;
      $.getJSON(url, function (retval) {                
          series.alldata = retval;
          self.closeSeriesModal(series);
          self.drawChart();
      });
        
    },
    
    changeYears() {
        
        this.pending = true;
        this.preserve_date_range = true;
        this.drawChart();
        
    },
    
    // DRAW CHART
    
    drawChart(burnThumb) {

        const self = this;
        
        // always burn a thumbnail unless we are told not to...
        burnThumb = typeof burnThumb !== 'undefined' ? burnThumb : true;
        
        options = self.chartToOptions();
        
        theChart.destroy();
		    theChart = new Highcharts.Chart(options);
		
		    if (burnThumb) {
		        
            var obj = {};
            //exportUrl = 'http://104.237.136.8:8080/highcharts-export-web/';
            obj.options = JSON.stringify(options);
            obj.type = 'image/png';
            obj.async = true;
            
            // ADD THUMBNAIL TO RECENT
            var d = new Date();
            var stamp = d.getTime();
            item = new Recent(stamp);
            self.recent.unshift(item);
            
            // GET THUMBNAIL (& SLUG, from export server)
            $.ajax({
                type: 'post',
                url: exportUrl,
                data: obj,
                success: function (data) {
                
                    var slug = data.substr(6,8) // slug is between 'files/' & '.png' in return value
                    self.chart.slug = slug;
                    
                    // find correct thumbnail by key and assign
                    self.recent.forEach(function (item,index) {
                        if (item.key == stamp) {
                            self.recent[index].slug = slug;
                            self.recent[index].imgsrc = exportUrl + data;
                            self.recent[index].options = obj.options;
                        }
                    });
                    
                    self.pending = false;
                    //self.$apply();
                
                }
            });
        
        }
        else {
            self.pending = false;
        }
	
    },   
    
    // CHART CONTROLS
    
    allSeriesSameType() {
        
        var theType;
        var theMeasure;
        var validation_err;
        
        this.preserve_date_range = true;
        
        switch(this.chart.chartType) {
        
            case "stacked_area_count":
                          
                theType = "area";
                theMeasure = "count";
                this.chart.scatter = false;
                this.chart.stacked = true;
            
                break;
                
            case "stacked_area_percent_total":
                
                theType = "area";
                theMeasure = "percent_total";
                this.chart.scatter = false;
                this.chart.stacked = true;
                
                break;
                
            case "stacked_column_count":
                
                theType = "column";
                theMeasure = "count";
                this.chart.scatter = false;
                this.chart.stacked = true;
                
                break;
                
            case "stacked_column_percent_total":
                
                theType = "column";
                theMeasure = "percent_total";
                this.chart.scatter = false;
                this.chart.stacked = true;
                
                break;
                
            case "scatter_plot":
                
                theMeasure = "count";
                this.chart.scatter = true;
                this.chart.stacked = false;

                
                break;
                
            case "scatter_plot_regression":
                
                theMeasure = "count";
                this.chart.scatter = true;
                this.chart.stacked = false;
                
                break;
                
            
            default:
            
                theType = this.chart.chartType;
                this.chart.stacked = false;
                this.chart.scatter = false;
                
        }
        
        this.pending = true;
        
        if (!this.chart.scatter) {
    
            this.chart.series.forEach(function (series, index) {
               series.type = theType;  
               if (theMeasure) series.measure = theMeasure;
               if (this.chart.stacked) series.yaxis = 0;
               
            });
    
        }
        
        this.drawChart(); 
        
    },
    
    saveChart() {
                
        strOptions = JSON.stringify(options);
            
        // SAVE CHART
        const self = this;
        resp = $.ajax({
            type: 'POST',
            url: '/charts/save/' + $("#user").val() + '/' + self.chart.slug,
            data: strOptions,
            success: function() {
                my_alert('Chart pinned!\n\nClick "Chart History" to reload.');
                item = new Saved( self.chart.slug, baseUrl + '/charts/' + self.chart.slug, strOptions );
                self.saved.unshift(item);
                //self.$apply();
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) { 
                my_alert('Could not pin chart.  Already pinned?'); 
            }
             
        });
        
    },
    
    editSeries(series) {
        
        // APPLY FILTERS (back to the data well!! closes modal and draws chart on finish)
        this.preserve_date_range = true;
        this.applyFilters(series);
        
    },
    
    closeSeriesModal(series) {
        
        jQuery('#seriesoptions-'+ series.dataset + '-' + series.topic).foundation('reveal','close');
        
    },

    deletePinned(index) {
            
        if (confirm('Really unpin?')) {  
        
             // DELETE CHART
            const self = this;
            resp = $.ajax({
                type: 'POST',
                url: '/charts/unpin/' +  self.saved[index].slug ,
                success: function() {
                    //alert('chart un-pinned!');
                    self.saved.splice(index,1);
                   // self.$apply();
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) { 
                    my_alert('Could not unpin.'); 
                }
             
            });
        
        }
        
    },
    
    recallPinned(index) {
        
        this.chart.slug = this.saved[index].slug;
        this.chart = JSON.parse(this.saved[index].options).CAP_chart;
       // this.chart = this.saved[index].options.CAP_chart;
        this.preserve_date_range = true;
        this.drawChart(false); 
    
    },
    
    recallRecent(index) {
        
        //var reverse_index = this.recent.length - index - 1;
        this.chart.slug = this.recent[index].slug;
       // this.chart = JSON.parse(this.recent[reverse_index].options).CAP_chart;
       
        this.chart = JSON.parse(this.recent[index].options).CAP_chart;
        this.preserve_date_range = true;
        this.drawChart(false);     
        
    },
    
    // Y-AXIS HELPERS
    
    checkAxes(thisSeries) {
        
        this.chart.series.forEach(function (series, index) {
            
            if (series.measure == thisSeries.measure) {
                series.measure_on_multiple_axes = true;
            } 
            
            
            else {
                series.measure_on_multiple_axes = false;
            }
            
            
        });
        
         
    },
    
    getAxisTitle(axIndex) {
        
        var unitLabels = [];
        var measureLabel = false;
        
        this.chart.series.forEach(function (s,key) {
            if ( (s.yaxis == axIndex) && (unitLabels.indexOf(s.unit) == -1) ) {
                
                if (s.measure == 'count' || s.measure == 'amount') {
                    unitLabels.push(s.unit);
                } else {
                    measureLabel = s.measure.split('_').join(' ').capitalizeFirstLetter();
                }
  
            }
        });
        
        return measureLabel ? measureLabel : unitLabels.join(', ');
        
    },
    
    chartExport(option) {
        
        //var save = false;
    
        this.chart.exportOption = 0;
        
        if (typeof(this.chart.slug) != "undefined") {
        
            var optionOverride =
            {
                legend:{
                    enabled: true
                }
            };
        
            strOptions = JSON.stringify(options);

            // SAVE CHART, UNPINNED
            const self = this;
            resp = $.ajax({
                type: 'POST',
                url: '/charts/saveunpinned/' + $("#user").val() + '/' + self.chart.slug,
                data: strOptions,
                success: function() {
            
                    switch(option) {

                        case 1: //PNG
                            theChart.exportChart(
                                {
                                type: 'image/png',
                                filename: self.chart.slug,
                                sourceWidth: 960,
                                },
                                optionOverride
                            );
                            break;
            
                        case 2: //CLEAN PNG
                            
                            optionOverride.legend = $.extend(optionOverride.legend,{enabled: false});
                            optionOverride.yAxis = [{
                                gridLineWidth: 0,
                                minorGridLineWidth: 0,
                                gridLineColor: 'transparent',
                                labels: {
                                    enabled: false
                                },
                                title: {
                                    text: options.yAxis[0].title.text
                                },
                                floor: 0
                            }];
                            
                            theChart.exportChart(
                                {
                                type: 'image/png',
                                filename: self.chart.slug,
                                sourceWidth: 960,
                                },
                                optionOverride
                                
                            );
                            break;
                        
                        case 3: //JPEG
                            theChart.exportChart(
                                {
                                type: 'image/jpeg',
                                filename: self.chart.slug,
                                sourceWidth: 960,
                                },
                                optionOverride
                            );
                            break;
            
                        case 4: //SVG
                            theChart.exportChart(
                                {
                                type: 'image/svg+xml',
                                filename: self.chart.slug,
                                sourceWidth: 960,
                                },
                                optionOverride
                            );
                            break;
            
                        case 5: //PDF
                            theChart.exportChart(
                                {
                                type: 'application/pdf',
                                filename: self.chart.slug,
                                sourceWidth: 960,
                                },
                                optionOverride
                            );
                            break;
            
                        case 6:
                            window.prompt( "copy to clipboard: Ctrl+C, Enter", baseUrl + "/charts/" + self.chart.slug );
                            break;
            
                        case 7:
                            window.prompt( "copy to clipboard: Ctrl+C, Enter", baseUrl + "/tool/" + self.chart.slug );
                            break;
                
                        case 8:
                            window.prompt( "copy to clipboard: Ctrl+C, Enter", baseUrl + "/embed/" + self.chart.slug );
                            break;
                
                        default:
    
                    }
            
            
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) { 
                    my_alert('Error saving chart.'); 
                }
         
            });
        
        } else {
        
            my_alert('No chart to export!');
            
        }
        
        
        
    },
    
    
    // CLEAR CHART
        
    clearChart() {
        
        this.clearSearch();
        this.chart = new Chart();
        this.drawChart(false);
        
    },
    
    clearSearch() {
        
        
        this.results = [];
        
        jQuery('div.picker input:checkbox').each(function() {
            $(this).removeAttr('checked');
        });
        
        
        this.budgetProjects.forEach(function (project, index) { 
        
            project.checked = false;
                
        });
        
        
        /*
        jQuery('#categories input:checked').each(function () {
            var cat = $(this).attr('catid');
            cats.push(cat);
        });
        */
        
    
    },
    
    // HELPERS
      
    clickInclude(filter) {
        
        if (filter.include == true) filter.exclude = false;
    
    },
      
    clickExclude(filter) {
        
        if (filter.exclude == true) filter.include = false;
    
    },
            
    isSelected(thisname) {
    	
      var l = this.chart.series.length;
      
      for (var i = 0; i < l; i++) {
        if (this.chart.series[i].name == thisname) return true;
      }
      
    	return false;
    	
    },
          
    getRgbaColor() {
        
        //construct array of colors in use
        var colors = [];
        for (var i = 0; i < this.chart.series.length; i++) {
            colors.push(this.chart.series[i].color);
        }
        
        var rgba_queue = rgba_colors.filter(function(c) {
            return colors.indexOf(c) == -1
        });
        
        if (rgba_queue.length == 0) {
            rgba_queue = JSON.parse(JSON.stringify(rgba_colors));
        }
      
        //return next color in line
        return rgba_queue[0];
                
    },
    
    openDrilldown(s,y) {
        
        drilldown(s.filters,s.dataset,s.sub,s.topic,s.agg,y);
        
    },
    
    getInstancesUrl(f,d,s,t) {
        
        var uri = getInstancesUri(f,d,s,t,this.chart.yearFrom,this.chart.yearTo);
        var url = baseUrl + "/api/instances/" + uri;
        return url;
        
    },
    
    
    // US CONGRESS HELPER METHODS
    
    years_to_congresses(data) {
        
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
    
    },
    
    aggregate_by_congress(data,starts_odd) {
                    
        var new_data = [];
        
        for (var i = 0; i < data.length; i++) {
        
            if (i % 2 == starts_odd) {
                
                var idx = starts_odd == 1 ? i - 1 : i + 1;
                
                if (idx >= 0  ) {
                    var thisyear = data[idx] === null ? 0 : data[idx];
                    var nextyear = data[idx+1] === null ? 0 : data[idx+1];
                    var val = (thisyear + nextyear);
                    if (val != Math.round(val)) {
                        val = Number(parseFloat(Math.round(val*1000)/1000).toFixed(3));
                    }
                    new_data.push(val);
                } else {
                    new_data.push(null);
                }

            }
        }
        
        return new_data;
    
    },
        
    percent_total_by_congress(data,starts_odd) {
                    
        var percent_total = [];
        
        for (var i = 0; i < data.length; i++) {
        
            if (i % 2 == starts_odd) {
                
                var idx = starts_odd == 1 ? i - 1 : i + 1;
                
                if (idx >= 0 && (data[idx+1] != null) ) {
                    var val = (data[idx] + data[idx+1]) / 2;
                    if (val != Math.round(val)) {
                        val = Number(parseFloat(Math.round(val*1000)/1000).toFixed(3));
                    }
                    percent_total.push(val);
                } else {
                    percent_total.push(null);
                }

            }
        }
        
        return percent_total;
    
    },

    percent_change_by_congress(preAggCount,starts_odd) {
        
        count = this.aggregate_by_congress(preAggCount,starts_odd);
        
        percent_change = [];
        
        for (var i = 0; i < count.length; i++) {
            pc = (count[i - 1] > 0) ? (count[i] - count[i - 1]) / count[i - 1] * 100 : null;
            if (pc != null) {
                percent_change.push(Number(parseFloat(pc).toFixed(3)));
            } else {
                percent_change.push(null);
            }
        }
        
        return percent_change;
    },
    
    noResults() {
        
        const self = this;
        var unhidden_results = [];
        this.results.forEach(function (result, index) {
            var add = true;
            self.chart.series.forEach(function (selected, index2) { 
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
        this.countryCount() > 0 && 
        this.categoryCount() > 0 && 
        this.topicCount() > 0
        ) ? true : false;
        
    },
    
    countryCount() {
        
        return jQuery('#projects input[type="checkbox"]:checked').length;
        
    },
    
    categoryCount() {
        
        return jQuery('#categories input[type="checkbox"]:checked').length;
        
    },
    
    topicCount() {
        
        return jQuery('#topics input.choose_topic:checked').length;
        
    },
    
    budgetProjectCount() {
        
        //return jQuery('#projects input[type="checkbox"]:checked').length;
        return 0;
        
    },
    
    budgetTopicCount() {
        
        //return jQuery('#topics input.choose_topic:checked').length;
        return 0;
    },
    
    allSeriesHaveCount() {

      for (var i=0;i<this.chart.series.length;i++) { 
          if (this.chart.series[i].agg == 2 || this.chart.series[i].budget == true) {
              return false;
          }
      }

      return true;
      
    },
    
    // only see chart types that are available for your selected series    
    chart_types_filtered() {
      
      const self = this;
      
      return this.chart_types.filter(function(item) {
        
            if (self.chart && self.chart.series) {
                
                // SOME SERIES DON'T HAVE COUNT, SOME CHART TYPES RELY ON IT
                if (
                    (item.type == 'stacked_area_count' ||
                    item.type == 'stacked_column_count' ||
                    item.type == 'scatter_plot' ||
                    item.type == 'scatter_plot_regression')
                    &&
                    (self.allSeriesHaveCount() == false)
                ) { return false; }
                
                // NEED EXACTLY TWO SERIES FOR SCATTER CHART TYPE, ALSO DOESN'T WORK WITH CONGRESS OPTION
                if (
                    (item.type == 'scatter_plot' ||
                    item.type == 'scatter_plot_regression')
                    &&
                    ( (self.chart.series.length != 2) || (self.chart.timeSeries=="congresses") )
                ) { return false; }
                
                // NEED AT LEAST TWO SERIES FOR STACKED CHART TYPE
                if (
                    (item.type == 'stacked_area_count' ||
                    item.type == 'stacked_column_count' ||
                    item.type == 'stacked_area_percent_total' ||
                    item.type == 'stacked_column_percent_total')
                    &&
                    (self.chart.series.length < 2)
                ) { return false; }
            
            }
                        
            return true;
            
        });
  
    },
    
    years_from() {
      
      const self = this;
      
      if (self.chart.timePeriodsAvailable) {
      
        return self.chart.timePeriodsAvailable.filter(function(item) {
          
            if (item.value < self.chart.yearTo) {
              return true;
            }
            return false;
      
        });
      
      }

      return self.chart.timePeriodsAvailable;
      
    },
    
    years_to() {
      
      const self = this;
      
      if (self.chart.timePeriodsAvailable) {
        return self.chart.timePeriodsAvailable.filter(function(item) {
          
            if (item.value > self.chart.yearFrom) {
              return true;
            }
            return false;
      
        });
      }

      return self.chart.timePeriodsAvailable;
    
    },
    
    yaxischoices_filtered(series) {
      
      const self = this;
      
      return this.yaxischoices.filter(function(choice) {
          
          if (self.chart && self.chart.series) {
          
              // DOES self CHOICE BELONG TO A DIFFERENT AXIS SCALED FOR A DIFFERENT MEASURE?

              var avail = true;

              self.chart.series.forEach(function (s, index) {

                  if (s != series && s.yaxis == choice.num) {

                      if (s.measure != series.measure) {
          
                          avail = false;
  
                      }
                  }
  
              });

              var xtra = 0;

              // DO YOU NEED XTRA OPTION?? only if you are not the only series scaled to your measure
              //console.log('series with self measure:' + self.chart.series.filter(function (el) {return el.measure == series.measure;}).length)

              xtra = 1 ? self.chart.series.length != self.chart.yaxes.length : 0;

              return choice.num < self.chart.yaxes.length + xtra
              && avail;
          
          }
          
          return true;
       
      });
      
    },
    
    clickTopic(topic) {

      topic.isOpen = !topic.isOpen;
  
    },
    
    onClipboardSuccess(e) {
    
      console.info('Action:', e.action);
      console.info('Text:', e.text);
      console.info('Trigger:', e.trigger);
      alert('Copied to clipboard.');
    
      e.clearSelection();
    
    },
    
    onClipboardError(e) {
    
      console.error('Action:', e.action);
      console.error('Trigger:', e.trigger);
    
    },


},

filters: {
  
  truncate: function (text, stop) {
    return text.slice(0, stop) + (stop < text.length ? '...' : '')
  },

},

delimiters: ['{@', '@}'],


});


/////////////////////////////////////////////////////////////////////// DOCUMENT READY

$(document).ready(function() {
    
    $(document).foundation();
    
    // access angular scope from outside app
   // theScope = angular.element(document.getElementById('toolcontroller')).scope();
    
    // create angular model from highcharts options
    // theScope.chart.chartFromOptions(options);
    if (typeof options.CAP_chart == 'undefined') {
        options.CAP_chart = new Chart();
    }
    
    toolApp.chart = options.CAP_chart;
    
    // send options to highcharts
    theChart = new Highcharts.Chart(options);

    $('h5.picker-label').click(function(e) {
        
        e.preventDefault();
        
        if ( ( $(this).text() == 'Select dataset types0' ) &&  ( $('#projects input:checked').length == 0 ) ) {
            
            my_alert('Please select a project first!');
            
        } else {
        
            $('div.picker:visible').slideToggle('fast','linear');
            $(this).next('div').slideToggle('fast','linear');
        
        }
        
        
    });
    
    
    var copyLink = document.getElementById('copy-table');
    var clipboard = new Clipboard(copyLink);
    clipboard.on('success', function(e) {
        //console.info('Action:', e.action);
        //console.info('Text:', e.text);
        //console.info('Trigger:', e.trigger);
        alert('Copied to clipboard.');
    
        e.clearSelection();
    });

    clipboard.on('error', function(e) {
        //console.error('Action:', e.action);
        //console.error('Trigger:', e.trigger);
    });
    
    //$('a.coming-soon').click(function(e) {
    //    e.preventDefault();
    //    alert('Feature coming soon!');
    //});
               
});


