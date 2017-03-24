'use strict';

angular.module('mosaicApp')
	.factory('mosaicUtilsFactory', function($http, $q, $location, mosaicConfigFactory) {
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
