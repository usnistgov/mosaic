'use strict';

angular.module('mosaicApp')
	.factory('DataPathFactory', function($http, $q, mosaicUtilsFactory) {
			var factory = {};

			factory.dataPath="";
			factory.newDataPath="";
			factory.errorString = "";

			factory.setDataPath = function(params, url) {
				var deferred = $q.defer();

				var results = mosaicUtilsFactory.post(url, params)
				.then(function (response, status) {	// success
						deferred.resolve(response);
					}, function (error) {	// error
						factory.errorString = error.data.errText;
						deferred.reject(error);
					});
				return deferred.promise;
			};


			factory.init = function() {
				mosaicUtilsFactory.post('/get-data-path', {})
				.then(function(response) {
					factory.dataPath = response.data.dataPath;
					factory.newDataPath = factory.dataPath;
					factory.errorString = "";
				}, function(error) {
					console.log(error);
				});
			};

			factory.init();

			return factory;
		}
	)
	.controller('dataPathCtrl', function($scope, $mdDialog, $location, DataPathFactory) {
			$scope.model = DataPathFactory;

			$scope.hide = function() {
				$scope.model.newDataPath=$scope.model.dataPath;
				$mdDialog.hide();
			};

			$scope.changePath = function() {
				var post=$scope.model.setDataPath({dataPath: $scope.model.newDataPath}, "/set-data-path");

				post.then(
						function(response) {
							$scope.model.dataPath=$scope.model.newDataPath;
							$scope.model.errorString = "";
							location.reload(true);
							$scope.hide();
						}, function(error) {
							//$scope.model.newDataPath=$scope.model.dataPath;
							$scope.model.errorString = error.data.errText;
							console.log(error);
						}
					)

				// $mdDialog.hide();
			};

			$scope.cancel = function() {
				$scope.model.newDataPath=$scope.model.dataPath;
				$scope.model.errorString = "";
				$mdDialog.cancel();
			};

	})
	.directive('fileBrowser', function () {
		return {
			scope: true,        //create a new scope
			link: function (scope, el, attrs) {
				el.bind('change', function (event) {
					var files = event.target.files;
					console.log(files[0].webkitdirectory);                             
				});
			}
		};
	});
