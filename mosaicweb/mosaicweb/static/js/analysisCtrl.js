'use strict';

angular.module('mosaicApp')
	.factory('AnalysisFactory', function($http, $q,mosaicUtilsFactory, mosaicConfigFactory, analysisSetupFactory, AnalysisStatisticsFactory) {
			var factory = {};

			factory.bdQuery = "select BlockDepth from metadata where ProcessingStatus='normal' and ResTime > 0.02";
			factory.contourQuery = "select BlockDepth, StateResTime from metadata where ProcessingStatus='normal' and ResTime > 0.02";

			factory.bdBins = 500;
			factory.histDensity = false;

			factory.contourBins = 200;
			factory.showContours = true;

			factory.showAnalysisControl=true;
			factory.analysisSettings = {};

			factory.eventNumber=1;
			factory.errorRateColor='#696969';

			factory.requireControlUpdate = false;
			factory.pageError = false;

			factory.histLoading = false;
			factory.contourLoading = false;

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

				mosaicUtilsFactory.post('/analysis-results', params)
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

		$scope.init = function() {
			// Switch session ID when explicitly set in route.
			if ($routeParams.sid != mosaicConfigFactory.sessionID) {
				mosaicConfigFactory.sessionID=$routeParams.sid;

				// Update statistics
				$scope.model.updateAnalysisStats();

				// Update histogram
				$scope.model.updateAnalysisHistogram({
					query: $scope.model.bdQuery,
					nBins: $scope.model.bdBins,
					density: $scope.model.histDensity
				});

				// Update contour plot
				$scope.model.updateAnalysisContour({
					query: $scope.model.contourQuery,
					nBins: $scope.model.contourBins,
					showContours: $scope.model.showContours
				});
				
			} else {
				// Update statistics
				$scope.model.updateAnalysisStats();
			};
		};
		$scope.init();

		// watch
		$scope.$watch('model.bdQuery', function() {
			if ($scope.model.bdQuery != '' && $scope.model.bdBins > 0) {
				$scope.model.updateAnalysisHistogram({
						query: $scope.model.bdQuery,
						nBins: $scope.model.bdBins,
						density: $scope.model.histDensity
					});
			};
		});
		$scope.$watch('model.bdBins', function() {
			if ($scope.model.bdQuery != '' && $scope.model.bdBins > 0) {
				$scope.model.updateAnalysisHistogram({
						query: $scope.model.bdQuery,
						nBins: $scope.model.bdBins,
						density: $scope.model.histDensity
					});
			};
		});
		$scope.$watch('model.histDensity', function() {
			if ($scope.model.bdQuery != '' && $scope.model.bdBins > 0) {
				$scope.model.updateAnalysisHistogram({
						query: $scope.model.bdQuery,
						nBins: $scope.model.bdBins,
						density: $scope.model.histDensity
					});
			};
		});
		$scope.$watch('model.contourQuery', function() {
			if ($scope.model.contourQuery != '' && $scope.model.contourBins > 0) {
				$scope.model.updateAnalysisContour({
					query: $scope.model.contourQuery,
					nBins: $scope.model.contourBins,
					showContours: $scope.model.showContours
				});
			};
		});
		$scope.$watch('model.contourBins', function() {
			if ($scope.model.contourQuery != '' && $scope.model.contourBins > 0) {
				$scope.model.updateAnalysisContour({
					query: $scope.model.contourQuery,
					nBins: $scope.model.contourBins,
					showContours: $scope.model.showContours
				});
			};
		});
		$scope.$watch('model.showContours', function() {
			if ($scope.model.contourQuery != '' && $scope.model.contourBins > 0) {
				$scope.model.updateAnalysisContour({
					query: $scope.model.contourQuery,
					nBins: $scope.model.contourBins,
					showContours: $scope.model.showContours
				});
			};
		});
		$scope.$watch('mosaicConfigModel.newDataAvailable', function() {
			if ($scope.mosaicConfigModel.newDataAvailable) {
				// Update statistics
				$scope.model.updateAnalysisStats();

				// Update histogram
				if ($scope.model.bdQuery != '' && $scope.model.bdBins > 0) {
					$scope.model.updateAnalysisHistogram({
							query: $scope.model.bdQuery,
							nBins: $scope.model.bdBins,
							density: $scope.model.histDensity
						});
				};

				// Update contour plot
				if ($scope.model.contourQuery != '' && $scope.model.contourBins > 0) {
					$scope.model.updateAnalysisContour({
						query: $scope.model.contourQuery,
						nBins: $scope.model.contourBins,
						showContours: $scope.model.showContours
					});
				};
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
