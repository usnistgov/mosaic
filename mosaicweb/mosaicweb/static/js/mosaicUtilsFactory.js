'use strict';

angular.module('mosaicApp')
	.factory('mosaicUtilsFactory', function($http, $q, $location, mosaicConfigFactory) {
			var factory = {};

			factory.post = function(url, params) {
				var deferred = $q.defer();

				var results = $http({
					method  : 'POST',
					url     : url,
					data    : params, //$.param($scope.startAnalysisFormData),  
					headers : { 'Content-Type': 'application/json; charset=utf-8' }
				})
				.then(function (response, status) {	// success
					deferred.resolve(response);
				}, function (error) {	// error
					deferred.reject(error);
				});

				return deferred.promise;
			};

			factory.returnToAnalysis = function() {
				$location.path('/analysis/').search({s: mosaicConfigFactory.sessionID});
			};
			
			return factory;
		}
	);
