'use strict';

angular.module('mosaicApp')
	.factory('FileListingFactory', function($http, $q) {
			var factory = {};

			factory.toolbarTitle = "Load Data";
			factory.subheading = "Data Root";
			factory.selectedIndex = null;

			factory.fileList = [];

			factory.post = function(params) {
				var deferred = $q.defer();

				var results = $http({
					method  : 'POST',
					url     : '/list-data-folders',
					data    : params, 
					headers : { 'Content-Type': 'application/json; charset=utf-8' }
				})
				.then(function (response, status) {	// success
						var flist = response.data.dataFolders;
						if (Object.keys(flist).length > 0) {	
							factory.subheading=response.data.level;			
							factory.fileList=flist;

							factory.selectedIndex=null;
						};
						deferred.resolve(response);
					}, function (error) {	// error
						deferred.reject(error);
					});
				return deferred.promise;
			};

			factory.init = function() {
				factory.post({
					level: factory.subheading
				});
			};

			factory.upOneLevel = function() {
				var path = factory.subheading.split('/');
				if (path.length == 2) {
					factory.post({
						level: 'Data Root'
					});
				} else {
					factory.post({
						level: path.slice(0, -2).join()
					});
				};
			};

			factory.init();

			return factory;
		}
	)
	.controller('fileListingCtrl', function($scope, $mdDialog, FileListingFactory) {
			$scope.model = FileListingFactory;

			$scope.loadData = function() {
				var post = $scope.model.post();

				post.then(
						function(response) {		
							$scope.hide();
						}, function(error) {
							console.log(error);
						}
					)
			};

			$scope.hide = function() {
				$mdDialog.hide({
								status: 'OK'
							});
			};

			$scope.answer = function(answer) {
				$mdDialog.hide({
						status: answer,
						filename: $scope.model.fileList[$scope.model.selectedIndex]
					});
			};

			$scope.cancel = function() {
				$mdDialog.cancel();
			};

			$scope.folderDblClick = function(index) {
				var path = '';
				if ($scope.model.subheading == 'Data Root/') {
					path = $scope.model.fileList[index].name;
				} else {
					path = $scope.model.subheading+$scope.model.fileList[index].name
				}

				$scope.model.post({
					level: path
				});
			};

			$scope.selectItem = function(index) {
				$scope.model.selectedIndex=index;
			};
	});
