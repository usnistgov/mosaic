'use strict';

angular.module('mosaicApp')
	.factory('AnalysisFactory', function($http, $q, $base64, $document, $mdToast, mosaicUtilsFactory, mosaicConfigFactory, analysisSetupFactory, AnalysisStatisticsFactory) {
			var factory = {};

			factory.histQuery = "select BlockDepth from metadata where ProcessingStatus='normal' and ResTime > 0.02";
			factory.contourQuery = "";

			factory.bdBins = 500;
			factory.histDensity = true;

			factory.contourBins = 200;
			factory.showContours = false;

			factory.showAnalysisControl=true;
			factory.analysisSettings = {};

			factory.eventNumber=1;
			factory.errorRateColor='#696969';

			factory.requireControlUpdate = false;
			factory.pageError = false;

			factory.histLoading = false;
			factory.contourLoading = false;

			factory.exportingCSV = false;

			factory.histogramAdvancedQuery=true;

			factory.selectedDBCols=null;
			factory.searchText=null;
			factory.searchConstraintText=null;
			factory.contourDBCols = [];
			factory.contourDBConstraintCols = [];
			factory.contourDBColsModel=[];
			factory.contourDBConstraintModel=[];
			factory.contourDBColsRemainingChoices=null;
			factory.contourDBConstraintColsRemainingChoices=null;
			factory.contourChipsReadonly=false;
			factory.contourDBColsRange={};
			factory.contourDBColMin=0;
			factory.contourDBColMax=1;
			factory.contourChipSelected=false;
			factory.contourSelectedChipName=null;
			factory.contourDBConstrain=false;

			factory.contourAdvancedQuery=false;

			factory.contourPlot={
				'contour': "<img width='90%' src='/static/img/contour.png' layout-padding>"
			};

			factory.analysisPlot={
				data:[
					{
						x:[1,1],
						y:[1,1],
						mode:'lines'
					},
				],
				layout:{
					xaxis: { 
						title: 'counts', 
						type: 'linear' 
					},
					yaxis: { 
						title: 'counts', 
						type: 'linear' 
					},
					paper_bgcolor:'rgba(0,0,0,0)', 
					plot_bgcolor:'rgba(0,0,0,0)'
				},
				options:{}
			}

			factory.analysisContour={
				data:[
					{
						x:[0,1],
						y:[0,1],
						z:[[10,10], [5,5]],
						type:'contour',
						// contour: {
						// 	'coloring': 'Viridis'
						// }
						colorscale: 'Viridis'
					},
				],
				layout:{
					xaxis: { 
						title: 'counts', 
						type: 'linear' 
					},
					yaxis: { 
						title: 'counts', 
						type: 'linear' 
					},
					zaxis: { 
						type: 'linear' 
					},
					paper_bgcolor:'rgba(0,0,0,0)', 
					plot_bgcolor:'rgba(0,0,0,0)'
				},
				options:{}
			}

			factory.querySearch = function(query) {
				if (factory.contourDBColsModel.length == 2) {
					return [];
				};

				factory.contourDBColsRemainingChoices=factory.contourDBCols.filter(function(n) {
					return factory.contourDBColsModel.indexOf(n) === -1;
				});

				var results = query ? factory.contourDBCols.filter(factory.createFilterFor(query)) : factory.contourDBColsRemainingChoices;
				return results;
			};

			factory.querySearchConstraints = function(query) {
				factory.contourDBConstraintColsRemainingChoices=factory.contourDBConstraintCols.filter(function(n) {
					return factory.contourDBConstraintModel.indexOf(n) === -1;
				});

				var results = query ? factory.contourDBConstraintCols.filter(factory.createFilterFor(query)) : factory.contourDBConstraintColsRemainingChoices;
				return results;
			};

			factory.createFilterFor = function(query) {
				var lowercaseQuery = angular.lowercase(query);

				return function filterFn(col) {
					return (col.toLowerCase().indexOf(lowercaseQuery) === 0);
				};
			};

			factory.addConstraintChip= function(chip_info) {
				factory.contourDBColsRange[chip_info]={
					min: 0,
					max: 1
				};
				factory.contourSelectedChipName=null;

				factory.contourDBColMin=factory.contourDBColsRange[chip_info].min;
				factory.contourDBColMax=factory.contourDBColsRange[chip_info].max;
			};

			factory.getConstraintChipInfo= function(chip_info) {
				if (chip_info) {
					factory.contourSelectedChipName=chip_info;

					var rng=factory.contourDBColsRange[chip_info];

					factory.contourDBColMin=rng.min;
					factory.contourDBColMax=rng.max;					

					factory.contourChipSelected=true;
				} else {
					factory.contourChipSelected=false;
				};

			};

			factory.buildContourQuery = function() {
				if (factory.contourDBColsModel.length==2) {
					var baseq = "select " + factory.contourDBColsModel.join(", ") + " from metadata where ProcessingStatus='normal'";
					var consarr=[];

					if (factory.contourDBConstrain && factory.contourDBConstraintModel.length > 0 ) {
						factory.contourDBConstraintModel.forEach(function(key,index) {
							if (key !== null || key !== undefined) {
								consarr.push(key+" between "+ factory.contourDBColsRange[key].min + " and " + factory.contourDBColsRange[key].max);								
							}
						});
						return String(baseq+" and "+consarr.join(" and "));
					} else {
						return String(baseq);
					};
				} else {
					return ""
				};
			};

			factory.updateContourQuery = function() {
				var qstr=factory.contourQuery;

				if (factory.contourAdvancedQuery) {
					qstr=factory.contourQuery;
				} else {
					qstr=factory.buildContourQuery();
				};

				if (factory.contourBins > 0) {
					factory.updateAnalysisContour({
						query: qstr,
						nBins: factory.contourBins,
						showContours: factory.showContours
					});
				};
			};

			factory.toggleAnalysisControlFlag = function() {
				factory.showAnalysisControl = !factory.showAnalysisControl;
			};

			factory.startAnalysis = function() {
				var deferred = $q.defer();


				mosaicUtilsFactory.post('/start-analysis', {
					'settingsString': analysisSetupFactory.getSettingsString()
				})
				.then(function(response, status) {
					deferred.resolve(response, status);
				}, function(error) {
					deferred.reject(error);
				});

				return deferred.promise;
			};

			factory.stopAnalysis = function() {
				mosaicUtilsFactory.post('/stop-analysis', {})
				.then(function(response, status) {
				}, function(error) {
					console.log(error);
				});
			};

			factory.updateAnalysisStats = function() {
				// Update stats during data update
				AnalysisStatisticsFactory.updateErrorStats();
			};

			factory.updateAnalysisHistogram = function(params) {
				var deferred = $q.defer();

				factory.analysisSettings = params;

				mosaicUtilsFactory.post('/analysis-histogram', params)
					.then(function (response, status) {	// success
						//save axes types
						var xaxistype=factory.analysisPlot.layout.xaxis.type;
						var yaxistype=factory.analysisPlot.layout.yaxis.type;

						factory.analysisPlot=response.data;

						factory.analysisPlot.layout.xaxis.type=xaxistype;
						factory.analysisPlot.layout.yaxis.type=yaxistype;

						factory.histLoading=false;

						deferred.resolve(response);
					}, function (error) {	// error
						deferred.reject(error);
					});

				factory.histLoading=true;
				return deferred.promise;
			};

			factory.updateAnalysisContour = function(params) {
				var deferred = $q.defer();

				factory.analysisSettings = params;

				mosaicUtilsFactory.post('/analysis-contour', params)
					.then(function (response, status) {	// success
						//save axes types
						var xaxistype=factory.analysisContour.layout.xaxis.type;
						var yaxistype=factory.analysisContour.layout.yaxis.type;

						factory.analysisContour=response.data;

						factory.contourQuery=$base64.decode(factory.analysisContour.queryString);

						factory.contourDBConstraintCols=factory.analysisContour.queryConstraintsCols;
						factory.contourDBCols=factory.analysisContour.queryCols;

						if (factory.contourDBColsModel.length === 0) {
							factory.contourDBColsModel=factory.analysisContour.selectedCols;
						}

						factory.analysisContour.layout.xaxis.type=xaxistype;
						factory.analysisContour.layout.yaxis.type=yaxistype;

						factory.contourLoading=false;

						deferred.resolve(response);
					}, function (error) {	// error
						deferred.reject(error);
					});

				factory.contourLoading=true;
				return deferred.promise;
			};

			factory.transpose = function(a) {
				return Object.keys(a[0]).map(function(c) {
					return a.map(function(r) { return r[c]; });
				});
			};

			factory.exportArrayAsCSV = function(data, filename) {
				var row = [];
				data.forEach(function (info, index) {
					var line = info.join(",");
					row.push(line);
				});
				var csvString = row.join("\n");

				factory.exportStringAsCSV(csvString, filename);
			};

			factory.exportStringAsCSV = function(csvString, filename) {
				var blob = new Blob([csvString], { type:"text/csv;charset=utf-8;" });			
				var downloadLink = angular.element('<a></a>');
							downloadLink.attr('href',window.URL.createObjectURL(blob));
							downloadLink.attr('download', filename);
				
				var body = $document.find('body').eq(0);
				body.append(downloadLink[0]);
				downloadLink[0].click();
			};

			factory.exportHistogramCSV = function() {
				var histData=factory.analysisPlot.data[0];				
				
				factory.exportArrayAsCSV(factory.transpose([histData.x, histData.y]), 'histogram.csv');
			};

			factory.exportAnalysisDatabaseCSV = function() {
				mosaicUtilsFactory.post('/analysis-database-csv', {queryString : "select * from metadata"})
					.then(function (response, status) {	// success
						factory.exportStringAsCSV($base64.decode(response.data.dbData), response.data.dbName+'.csv');
						factory.exportingCSV = false;
						$mdToast.hide(factory.exportToast);
					}, function (error) {	// error
						console.log(error);
						factory.exportingCSV = false;
					});
					factory.exportingCSV = true;
					factory.exportToast=factory.showInfoToast("Exporting database to CSV ...");

					$mdToast.show(factory.exportToast);
			};

			factory.showInfoToast = function(msg) {
				var toast = $mdToast.simple()
					.position('bottom left')
					.parent("#globalToastAnchor")
					.textContent(msg)
					.highlightClass('md-accent')
					.hideDelay(0);

				return toast;
			};

			return factory;
		}
	)
	.controller('AnalysisCtrl', function($scope, $mdDialog, $location,  $routeParams, AnalysisFactory, AnalysisStatisticsFactory, analysisSetupFactory, mosaicConfigFactory, mosaicUtilsFactory) {
		$scope.formContainer = {};

		$scope.model = AnalysisFactory;
		$scope.mosaicConfigModel = mosaicConfigFactory;

		$scope.setupModel = analysisSetupFactory;
		$scope.statsModel = AnalysisStatisticsFactory;

		$scope.customFullscreen = true;

		$scope.makeDBColsObject = function() {
				var dbcols=[
					{'name': 'BlockDepth'},
					{'name': 'StateResTime'}
				];

				return dbcols.map(function (col) {
					col._lowername = col.name.toLowerCase();
					return col;
				});
			};			

		$scope.init = function() {
			// Switch session ID when explicitly set in route.
			if ($routeParams.sid != mosaicConfigFactory.sessionID) {
				mosaicConfigFactory.sessionID=$routeParams.sid;
			};
			// Update statistics
			$scope.model.updateAnalysisStats();

			// Update histogram
			$scope.model.updateAnalysisHistogram({
				query: $scope.model.histQuery,
				nBins: $scope.model.bdBins,
				density: $scope.model.histDensity
			});

			// Update contour plot
			$scope.model.updateContourQuery()
		};
		$scope.init();

		// watch
		$scope.$watch('model.contourDBColMin', function() {
			if ($scope.model.contourSelectedChipName !== null){
				$scope.model.contourDBColsRange[$scope.model.contourSelectedChipName]={
					min : $scope.model.contourDBColMin,
					max : $scope.model.contourDBColMax
				};
			};

		});
		$scope.$watch('model.contourDBColMax', function() {
			if ($scope.model.contourSelectedChipName !== null){
				$scope.model.contourDBColsRange[$scope.model.contourSelectedChipName]={
					min : $scope.model.contourDBColMin,
					max : $scope.model.contourDBColMax
				};
			};
		});
		$scope.$watch('model.histQuery', function() {
			if ($scope.model.histQuery != '' && $scope.model.bdBins > 0) {
				$scope.model.updateAnalysisHistogram({
						query: $scope.model.histQuery,
						nBins: $scope.model.bdBins,
						density: $scope.model.histDensity
					});
			};
		});
		$scope.$watch('model.bdBins', function() {
			if ($scope.model.histQuery != '' && $scope.model.bdBins > 0) {
				$scope.model.updateAnalysisHistogram({
						query: $scope.model.histQuery,
						nBins: $scope.model.bdBins,
						density: $scope.model.histDensity
					});
			};
		});
		$scope.$watch('model.histDensity', function() {
			if ($scope.model.histQuery != '' && $scope.model.bdBins > 0) {
				$scope.model.updateAnalysisHistogram({
						query: $scope.model.histQuery,
						nBins: $scope.model.bdBins,
						density: $scope.model.histDensity
					});
			};
		});
		// $scope.$watch('model.contourQuery', function() {
		// 	$scope.model.updateContourQuery();
		// });
		$scope.$watch('model.contourBins', function() {
			$scope.model.updateContourQuery();
		});
		$scope.$watch('model.showContours', function() {
			$scope.model.updateContourQuery();
		});
		$scope.$watch('mosaicConfigModel.newDataAvailable', function() {
			if ($scope.mosaicConfigModel.newDataAvailable) {
				// Update statistics
				$scope.model.updateAnalysisStats();

				// Update histogram
				if ($scope.model.histQuery != '' && $scope.model.bdBins > 0) {
					$scope.model.updateAnalysisHistogram({
							query: $scope.model.histQuery,
							nBins: $scope.model.bdBins,
							density: $scope.model.histDensity
						});
				};

				// Update contour plot
				$scope.model.updateContourQuery();
			};
		});

		$scope.updateControls = function() {
			$scope.model.requireControlUpdate=false;
			$scope.formContainer.analysisHistogramForm.$setPristine();
		};

		$scope.showAnalysisLog = function(ev) {
			$mdDialog.show({
				controller: LogController,
				templateUrl: 'static/partials/analysislog.tmpl.html',
				parent: angular.element(document.body),
				targetEvent: ev,
				clickOutsideToClose:true,
				fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
			})
			.then(function(answer) {
				$scope.status = 'You said the information was "' + answer + '".';
			}, function() {
				$scope.status = 'You cancelled the dialog.';
			});
		};

		$scope.showAnalysisSettings = function() {
			$location.path('/setup-analysis/').search({sid: $scope.mosaicConfigModel.sessionID});
		};

		$scope.showAnalysisStatistics = function(ev) {
			$mdDialog.show({
				locals:{mosaicUtilsFactory: mosaicUtilsFactory},
				controller: 'AnalysisStatisticsCtrl',
				templateUrl: 'static/partials/analysisstats.tmpl.html',
				parent: angular.element(document.body),
				targetEvent: ev,
				clickOutsideToClose:true,
				fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
			})
			.then(function(answer) {
				$scope.status = 'You said the information was "' + answer + '".';
			}, function() {
				$scope.status = 'You cancelled the dialog.';
			});
		};

		$scope.showEventViewer = function(ev) {
			$mdDialog.show({
				controller: 'eventViewerCtrl',
				templateUrl: 'static/partials/eventviewer.tmpl.html',
				parent: angular.element(document.body),
				targetEvent: ev,
				clickOutsideToClose:true,
				fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
			})
		};

		function LogController($scope, $mdDialog) {
			$scope.utils=mosaicUtilsFactory;
			$scope.logText='';

			$scope.hide = function() {
				$mdDialog.hide();
			};
			
			$scope.cancel = function() {
				$mdDialog.cancel();
			};
			
			$scope.updateAnalysisLog = function() {
				$scope.utils.post('/analysis-log', {})
				.then(function(response, status) {
					$scope.logText=response.data.logText;
				}, function(error){
					console.log(error);
				});
			};

			$scope.updateAnalysisLog();
		}

	});
