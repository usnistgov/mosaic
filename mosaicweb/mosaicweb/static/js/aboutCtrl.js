'use strict';

angular.module('mosaicApp')
	.factory('AboutFactory', function($http) {
			var factory = {};

			factory.about = {};

			factory.init = function() {				
				var results = $http({
					method  : 'POST',
					url     : '/about',
					data    : {},  
					headers : { 'Content-Type': 'application/json; charset=utf-8' }
				})
					.then(
						function (response, status) {		// success
							factory.about = response.data;
						}, function (error) {				// error
							console.log(error);
						}
					);
			};

			factory.developers = [
					{ 'name': 'Arvind Balijepalli', 'institution': 'NIST', 'email': '', 'face': '/static/img/face.gif' },
					{ 'name': 'Kyle Briggs', 'institution': 'Univeristy of Ottawa', 'email': '', 'face': '/static/img/face.gif' },
					{ 'name': 'Jacob Forstater', 'institution': '','email': '', 'face': '/static/img/face.gif' },
					{ 'name': 'Canute Vaz', 'institution': '', 'email': '', 'face': '/static/img/face.gif' }
				];

			factory.init();

			return factory;
		}
	)
	.controller('AboutCtrl', function($scope, $mdDialog, AboutFactory, mosaicConfigFactory, mosaicUtilsFactory) {
			$scope.aboutFactory = AboutFactory;

			$scope.mosaicConfigModel = mosaicConfigFactory;
			$scope.mosaicUtilsModel = mosaicUtilsFactory;

			$scope.showDevelopers = function(ev) {
				$mdDialog.show({
					controller: DevelopersDialogController,
					templateUrl: 'static/partials/developers.tmpl.html',
					parent: angular.element(document.body),
					targetEvent: ev,
					clickOutsideToClose:true,
					fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
				})
			};

			$scope.showTermsOfUse = function(ev) {
				$mdDialog.show({
					controller: TermsOfUseDialogController,
					templateUrl: 'static/partials/termsofuse.tmpl.html',
					parent: angular.element(document.body),
					targetEvent: ev,
					clickOutsideToClose:true,
					fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
				})
			};

			function DevelopersDialogController($scope, $mdDialog, AboutFactory) {
				$scope.developers = AboutFactory.developers;

				$scope.hide = function() {
					$mdDialog.hide();
				};
				$scope.cancel = function() {
					$mdDialog.cancel();
				};
				$scope.answer = function(answer) {
					$mdDialog.hide(answer);
				};
			}

			function TermsOfUseDialogController($scope, $mdDialog) {
				$scope.hide = function() {
					$mdDialog.hide();
				};
				$scope.cancel = function() {
					$mdDialog.cancel();
				};
				$scope.answer = function(answer) {
					$mdDialog.hide(answer);
				};
			}
	});
