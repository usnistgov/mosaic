'use strict';

angular.module('mosaicApp')
	.factory('EventViewerFactory', function($http, $q, mosaicUtilsFactory, mosaicConfigFactory) {
			var factory = {};

			factory.eventNumber=1;
			factory.recordCount=10;
			factory.eventViewPlot='';

			factory.plotUpdating=false;

			factory.updateEvientView = function() {
				mosaicUtilsFactory.post('/event-view', {
					'eventNumber': factory.eventNumber
				})
				.then(function(response, status) {
					factory.eventViewPlot=response.data.eventViewPlot;
					factory.eventNumber=response.data.eventNumber;
					factory.recordCount=response.data.recordCount;
					
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

			return factory;
		}
	)
	.controller('eventViewerCtrl', function($scope, $mdDialog, $interval, EventViewerFactory) {
		$scope.model = EventViewerFactory;

		$scope.customFullscreen = true;

		$scope.model.updateEvientView();
		
		// watch
		$scope.$watch('model.eventNumber', function() {
			$scope.model.updateEvientView();
		});

		$scope.cancel = function() {
			$mdDialog.cancel();
		};	
	});
