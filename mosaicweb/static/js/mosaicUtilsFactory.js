'use strict';

angular.module('mosaicApp')
	.factory('mosaicUtilsFactory', function($http, $q, $location, $interval, $mdToast, mosaicConfigFactory) {
			var factory = {};

			factory.post = function(url, params) {
				var deferred = $q.defer();

				var p=params;
				if (mosaicConfigFactory.sessionID != null) {
					p.sessionID = mosaicConfigFactory.sessionID;
				};				
				var results = $http({
					method  : 'POST',
					url     : url,
					data    : p,
					headers : { 'Content-Type': 'application/json; charset=utf-8' }
				})
				.then(function (response, status) {	// success
					if ('sessionID' in response.data) {
						mosaicConfigFactory.sessionID=response.data.sessionID;
					};
					if ('analysisRunning' in response.data) {
						mosaicConfigFactory.analysisRunning=(response.data.analysisRunning === 'true');
					};
					if ('newDataAvailable' in response.data) {
						mosaicConfigFactory.newDataAvailable=response.data.newDataAvailable;
					};
					deferred.resolve(response);
				}, function (error) {	// error
					console.log(error);
					factory.showErrorToast(error.data.errSummary);
					deferred.reject(error);
				});

				return deferred.promise;
			};

			factory.returnToAnalysis = function() {
				$location.path('/analysis/').search({sid: mosaicConfigFactory.sessionID});
			};
			
			factory.showErrorToast = function(error) {
				var toast = $mdToast.simple()
					.position('bottom left')
					.parent("#globalToastAnchor")
					.textContent(error)
					.action('DISMISS')
					.highlightAction(true)
					.highlightClass('md-warn')
					.hideDelay(7000);

					$mdToast.show(toast).then(function(response) {
						if ( response == 'ok' ) {
								factory.serverError = false;
						}
					});
			};

			factory.pollAnalysisStatus = function() {
				$interval(function() {
					if (mosaicConfigFactory.analysisRunning) {
						factory.post('/poll-analysis-status', {});
					};
				}, 5000);
			};

			factory.pollAnalysisStatus();

			return factory;
		}
	);
