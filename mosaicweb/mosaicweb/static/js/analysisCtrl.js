'use strict';

angular.module('mosaicApp')
	.factory('AnalysisFactory', function($http, $q,mosaicUtilsFactory, mosaicConfigFactory, analysisSetupFactory, AnalysisStatisticsFactory) {
			var factory = {};

			factory.bdQuery = "select BlockDepth from metadata where ProcessingStatus='normal' and ResTime > 0.02";
			factory.bdBins = 500;
			factory.histDensity = false;

			factory.showAnalysisControl=true;
			factory.analysisSettings = {};

			factory.eventNumber=1;
			factory.errorRateColor='#696969';

			factory.requireControlUpdate = false;
			factory.pageError = false;

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

			factory.updateAnalysisData = function(params) {
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

						// Update stats during data update
						AnalysisStatisticsFactory.updateErrorStats();

						deferred.resolve(response);
					}, function (error) {	// error
						deferred.reject(error);
					});

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
				$scope.model.updateAnalysisData({
					query: $scope.model.bdQuery,
					nBins: $scope.model.bdBins
				});
			}
		};
		$scope.init();

		// watch
		$scope.$watch('model.bdQuery', function() {
			if ($scope.model.bdQuery != '' && $scope.model.bdBins > 0) {
				$scope.model.updateAnalysisData({
						query: $scope.model.bdQuery,
						nBins: $scope.model.bdBins
					});
			};
		});
		$scope.$watch('model.bdBins', function() {
			if ($scope.model.bdQuery != '' && $scope.model.bdBins > 0) {
				$scope.model.updateAnalysisData({
						query: $scope.model.bdQuery,
						nBins: $scope.model.bdBins
					});
			};
		});
		$scope.$watch('mosaicConfigModel.newDataAvailable', function() {
			if ($scope.mosaicConfigModel.newDataAvailable) {
				if ($scope.model.bdQuery != '' && $scope.model.bdBins > 0) {
					$scope.model.updateAnalysisData({
							query: $scope.model.bdQuery,
							nBins: $scope.model.bdBins
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
