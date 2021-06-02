'use strict';

angular.module('mosaicApp')
	.factory('AdvancedSettingsFactory', function($http, $q) {
			var factory = {};

			factory.selectedFileType='';
			factory.originalSettings={};
			factory.analysisSettings={};
			factory.validatingSettings = false;

			factory.origProcAlgo='';
			factory.procAlgo='';

			factory.controlsUpdateFlag = false;
			factory.procAlgoLocalChanges = false;
			
			factory.errorString = "";

			factory.post = function() {
				var deferred = $q.defer();

				var results = $http({
					method  : 'POST',
					url     : '/validate-settings',
					data    : {analysisSettings: factory.analysisSettings}, 
					headers : { 'Content-Type': 'application/json; charset=utf-8' }
				})
				.then(function (response, status) {	// success
						factory.errorString="";

						deferred.resolve(response);
					}, function (error) {	// error
						factory.errorString = error.data.errSummary+": "+error.data.errText;

						deferred.reject(error);
					});
				return deferred.promise;
			};

			factory.setUpdateFlags = function() {
				var orig = factory.originalSettings;
				var sett = angular.fromJson(factory.analysisSettings);

				var origTrajIO=null;
				var trajIO=null;

				if (factory.selectedFileType=='QDF') {
					origTrajIO=orig.qdfTrajIO;
					trajIO=sett.qdfTrajIO;
				} else if (factory.selectedFileType=='ABF') {
					origTrajIO=orig.abfTrajIO;
					trajIO=sett.abfTrajIO;
				} else if (factory.selectedFileType=='BIN') {
					origTrajIO=orig.binTrajIO;
					trajIO=sett.binTrajIO;
				} else if (factory.selectedFileType=='CHI') {
					origTrajIO=orig.chimeraTrajIO;
					trajIO=sett.chimeraTrajIO;
				};

				if ( 	orig.eventSegment.blockSizeSec != sett.eventSegment.blockSizeSec 
					 || origTrajIO.start != trajIO.start
					) {
					factory.controlsUpdateFlag = true;
				} else {
					factory.controlsUpdateFlag = false;
				};

				factory.procAlgoLocalChanges = factory.procAlgoChanged(orig, sett);
			};

			factory.procAlgoChanged = function(orig, sett) {
				factory.origProcAlgo=factory.procAlgorithm(orig);
				factory.procAlgo=factory.procAlgorithm(sett);

				if ( factory.origProcAlgo != factory.procAlgo ) {
					return true;
				} else if (factory.originalSettings[factory.origProcAlgo] != factory.analysisSettings[factory.procAlgo]) {
					return true;
				} else {
					return false;	
				}
			};

			factory.procAlgorithm = function(settingsObject) {
				// console.log(settingsObject);
				for (var section in settingsObject) {
					if ((['adept', 'adept2State', 'cusumPlus'].indexOf(section) != -1)) {
						return section
					}
				}
				return null;
			};

			return factory;
		}
	)
	.controller('AdvancedSettingsCtrl', function($scope, $mdDialog, $q, AdvancedSettingsFactory, analysisSettings, selectedFileType) {
			$scope.model = AdvancedSettingsFactory;

			$scope.model.originalSettings=analysisSettings;
			$scope.model.selectedFileType=selectedFileType;
			$scope.model.analysisSettings=JSON.stringify(analysisSettings, null, "	");
			$scope.number = 5;

			$scope.getNumber = function(num) {
				return new Array(num);
			};

			$scope.submitSettings = function() {
				var post = $scope.model.post();

				post.then(
						function(response) {
							$scope.model.setUpdateFlags();

							$scope.hide();
						}, function(error) {
							console.log(error);
						}
					)
			};

			$scope.hide = function() {
				$mdDialog.hide({
								status: 'OK',
								analysisSettings: $scope.model.analysisSettings,
								controlsUpdateFlag: $scope.model.controlsUpdateFlag
							});
			};
			$scope.cancel = function() {
				$scope.model.errorString="";
				$mdDialog.cancel();
			};
	});
