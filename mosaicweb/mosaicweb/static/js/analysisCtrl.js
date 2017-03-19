'use strict';

angular.module('mosaicApp')
	.factory('AnalysisFactory', function($http, $q) {
			var factory = {};

			factory.AnalysisRunning = false;

			factory.bdQuery = "select BlockDepth from metadata where ProcessingStatus='normal' and ResTime > 0.02";
			factory.bdBins = 500;
			factory.histDensity = false;

			factory.showAnalysisControl=false;
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

			factory.stopAnalysis = function() {
				factory.AnalysisRunning = false;
			};

			factory.post = function(params) {
				var deferred = $q.defer();

				factory.analysisSettings = params;

				// console.log(factory.analysisSettings);

				var results = $http({
					method  : 'POST',
					url     : '/histogram',
					data    : params, //$.param($scope.startAnalysisFormData),  
					headers : { 'Content-Type': 'application/json; charset=utf-8' }
				})
				.then(function (response, status) {	// success
					// $scope.analysisPlot=response.data;
					factory.analysisPlot=response.data;
					factory.AnalysisRunning = true;

					deferred.resolve(response);
				}, function (error) {	// error
					deferred.reject(error);
				});

				return deferred.promise;
			};
			return factory;
		}
	)
	.controller('AnalysisCtrl', function($scope, $mdDialog, AnalysisFactory) {
		$scope.formContainer = {};

		$scope.model = AnalysisFactory;

		$scope.customFullscreen = true;

		// watch
		$scope.$watch('formContainer.analysisHistogramForm.bdQuery.$pristine', function() {
			$scope.model.requireControlUpdate=true;
		});
		$scope.$watch('formContainer.analysisHistogramForm.bdBins.$pristine', function() {
			$scope.model.requireControlUpdate=true;
		});

		$scope.updateControls = function() {
			$scope.model.requireControlUpdate=false;
			$scope.formContainer.analysisHistogramForm.$setPristine();
		};

		$scope.showAnalysisLog = function(ev) {
			$mdDialog.show({
				controller: DialogController,
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

		$scope.showEventViewer = function(ev) {
			$mdDialog.show({
				locals:{eventNumber: $scope.model.eventNumber},
				controller: EventViewController,
				templateUrl: 'static/partials/eventviewer.tmpl.html',
				parent: angular.element(document.body),
				targetEvent: ev,
				clickOutsideToClose:true,
				fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
			})
		};

		function DialogController($scope, $mdDialog) {
			$scope.hide = function() {
				$mdDialog.hide();
			};
			$scope.cancel = function() {
				$mdDialog.cancel();
			};
			$scope.answer = function(answer) {
				$mdDialog.hide(answer);
			};
		}

		function EventViewController($scope, $mdDialog, eventNumber) { 
			$scope.eventNumber = eventNumber;
			
			$scope.cancel = function() {
				$mdDialog.cancel();
			};

			$scope.eventForward = function() {
				$scope.eventNumber++;
			};
			$scope.eventBack = function() {
				$scope.eventNumber--;
				$scope.eventNumber=Math.max(0, $scope.eventNumber);
				
			};
		};
	});
