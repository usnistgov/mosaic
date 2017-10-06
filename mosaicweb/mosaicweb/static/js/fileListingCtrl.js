'use strict';

angular.module('mosaicApp')
	.factory('FileListingFactory', function($http, $q, mosaicUtilsFactory) {
			var factory = {};

			factory.dialogMode="directory";

			factory.toolbarTitle = "Load Data";
			factory.subheading = "Data Root";
			factory.selectedIndex = null;

			factory.fileList = [];

			factory.getListing = function(params, url) {
				var deferred = $q.defer();

				var results = mosaicUtilsFactory.post(url, params)
				.then(function (response, status) {	// success

						var flist = response.data.fileData;
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

			factory.setDialogMode = function(mode) {
				factory.dialogMode=mode;
			};

			factory.init = function() {
				if (factory.dialogMode=="directory") {
					factory.getListing({
						level: factory.subheading
					}, '/list-data-folders');
				} else if (factory.dialogMode=="sqlite") {
					factory.getListing({
						level: factory.subheading
					}, '/list-database-files');
				} else {
					console.log("not implemented");
				};
			};

			factory.upOneLevel = function() {
				var path = factory.subheading.split('/');
				if (factory.dialogMode=="directory") {
					if (path.length == 2) {
						factory.getListing({
							level: 'Data Root'
						}, '/list-data-folders');
					} else {
						factory.getListing({
							level: path.slice(0, -2).join()
						}, '/list-data-folders');
					};
				} else if (factory.dialogMode=="sqlite") {
					if (path.length == 2) {
						factory.getListing({
							level: 'Data Root'
						}, '/list-database-files');
					} else {
						factory.getListing({
							level: path.slice(0, -2).join()
						}, '/list-database-files');
					};
				}
			};

			factory.init();

			return factory;
		}
	)
	.controller('fileListingCtrl', function($scope, $mdDialog, FileListingFactory) {
			$scope.model = FileListingFactory;

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

				if ($scope.model.dialogMode=="directory") {
					$scope.model.getListing({
						level: path
					},"/list-data-folders");
				} else if ($scope.model.dialogMode=="sqlite") {
					$scope.model.getListing({
						level: path
					},"/list-database-files");
				}
			};

			$scope.selectItem = function(index) {
				$scope.model.selectedIndex=index;
			};
	});
