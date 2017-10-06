'use strict';

angular.module('mosaicApp')
	.factory('EventViewerFactory', function($http, $q, $mdToast, $mdDialog, mosaicUtilsFactory, mosaicConfigFactory) {
			var factory = {};

			factory.eventNumber=1;
			factory.recordCount=10;
			factory.eventViewPlot='';
			factory.errorText='';
			factory.parameterTable={};
			// 'normal',
			factory.eventFilter=[];
			factory.displayNormal=true;
			factory.displayWarning=true;
			factory.displayError=true;

			factory.plotUpdating=false;

			factory.cellStyle="margin: 16px; padding: 16px; margin-top:0; margin-bottom:0; padding-top:0; padding-bottom:0;";

			factory.updateEvientView = function() {
				factory.eventFilter=[];
				if (factory.displayNormal) {
					factory.eventFilter.push('normal');
				};
				if (factory.displayWarning) {
					factory.eventFilter.push('warning');
				};
				if (factory.displayError) {
					factory.eventFilter.push('error');
				};

				mosaicUtilsFactory.post('/event-view', {
					'eventNumber': factory.eventNumber,
					'eventFilter': factory.eventFilter
				})
				.then(function(response, status) {
					factory.eventViewPlot=response.data.eventViewPlot;
					factory.eventNumber=response.data.eventNumber;
					factory.recordCount=response.data.recordCount;
					factory.errorText=response.data.errorText;
					factory.parameterTable=response.data.parameterTable;

					if (factory.errorText != '') {
						factory.showErrorToast();
						factory.parameterTable=[];
					} else {
						$mdToast.hide();
					};
					factory.plotUpdating=false;
				}, function(error) {
					console.log(error);
				});
				factory.plotUpdating=true;
			};

			factory.eventForward = function() {
				factory.eventNumber++;
				factory.eventNumber=Math.min(factory.eventNumber, factory.recordCount);
			};
			factory.eventBack = function() {
				factory.eventNumber--;
				factory.eventNumber=Math.max(1, factory.eventNumber);
			};

			factory.showErrorToast = function() {
				var toast = $mdToast.simple()
					.position('bottom center')
					.parent("#toastAnchor")
					.textContent(factory.errorText)
					.action('DISMISS')
					.highlightAction(true)
					.highlightClass('md-warn')
					.hideDelay(0);

					$mdToast.show(toast).then(function(response) {}, function() {
						console.log(factory.errorText);
					});
			};

			return factory;
		}
	)
	.controller('eventViewerCtrl', function($scope, $mdDialog, $mdPanel, $interval, EventViewerFactory) {
		$scope.model = EventViewerFactory;

		$scope.customFullscreen = true;

		$scope.model.updateEvientView();
		
		// watch
		$scope.$watch('model.eventNumber', function() {
			$scope.model.updateEvientView();
		});
		$scope.$watch('model.displayNormal', function() {
			$scope.model.eventNumber=1;
			$scope.model.updateEvientView();
		});
		$scope.$watch('model.displayWarning', function() {
			$scope.model.eventNumber=1;
			$scope.model.updateEvientView();
		});
		$scope.$watch('model.displayError', function() {
			$scope.model.eventNumber=1;
			$scope.model.updateEvientView();
		});

		$scope.key=function($event) {
			if ($event.keyCode == 39) 
				$scope.model.eventForward();
			else if ($event.keyCode == 37)
				$scope.model.eventBack();
		};

		$scope.cancel = function() {
			$mdDialog.cancel();
		};	
	});
