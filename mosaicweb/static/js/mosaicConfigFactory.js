'use strict';

angular.module('mosaicApp')
	.factory('mosaicConfigFactory', function($http, $q) {
			var factory = {};

			factory.sessionID = null;
			factory.analysisRunning = false;
			factory.newDataAvailable = false;
			
			return factory;
		}
	);
