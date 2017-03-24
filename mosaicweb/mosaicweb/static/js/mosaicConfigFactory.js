'use strict';

angular.module('mosaicApp')
	.factory('mosaicConfigFactory', function($http, $q) {
			var factory = {};

			factory.sessionID = '4d066f15e3f045bab9be45c767388049';
			factory.analysisrunning = false;
			
			return factory;
		}
	);
