'use strict';

angular.module('mosaicApp')
	.factory('mosaicConfigFactory', function($http, $q) {
			var factory = {};

			factory.sessionID = null;
			factory.analysisrunning = false;
			
			return factory;
		}
	);
