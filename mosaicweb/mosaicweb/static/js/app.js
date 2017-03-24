'use strict';

angular.module('mosaicApp', ['ngRoute', 'ngMaterial', 'ngMessages', 'ngAnimate', 'plotly'])
.config(
	function($mdThemingProvider) {
		var mosaicPrimary = {
			'50': '#6573d5',
			'100': '#5161d0',
			'200': '#3d4eca',
			'300': '#3343bb',
			'400': '#2d3ca7',
			'500': '#283593',
			'600': '#232e7f',
			'700': '#1d276b',
			'800': '#181f57',
			'900': '#121843',
			'A100': '#7985db',
			'A200': '#8d97e0',
			'A400': '#a1aae6',
			'A700': '#0d112f',
			'contrastDefaultColor': 'light',
			'contrastDarkColors': ['50', '100', '200', '300', 'A100', 'A400']
		};
		$mdThemingProvider
			.definePalette('mosaicPrimary', mosaicPrimary);

		var mosaicAccent = {
			'50': '#b3b3b3',
			'100': '#bfbfbf',
			'200': '#cccccc',
			'300': '#d9d9d9',
			'400': '#e6e6e6',
			'500': '#f2f2f2',
			'600': '#ffffff',
			'700': '#ffffff',
			'800': '#ffffff',
			'900': '#ffffff',
			'A100': '#ffffff',
			'A200': '#ffffff',
			'A400': '#f2f2f2',
			'A700': '#ffffff',
			'contrastDefaultColor': 'dark',
			'contrastDarkColors': ['50', '100', '200', '300', 'A100', 'A400']
		};
		$mdThemingProvider
			.definePalette('mosaicAccent', mosaicAccent);

	   $mdThemingProvider.theme('default')
		   .primaryPalette('mosaicPrimary')
		   .accentPalette('mosaicAccent')
	}
)
.config(
	function($routeProvider, $locationProvider) {
		$locationProvider.hashPrefix('');

		$routeProvider
			.when('/', {
				 templateUrl: '/static/partials/index.html'
			 })
			 .when('/about/', {
				 templateUrl: '/static/partials/about.html',
				 controller: 'AboutCtrl'
			 })
			 .when('/setup-analysis/', {
				 templateUrl: '/static/partials/setupAnalysis.html',
				 controller: 'analysisSetupCtrl'
			 })
			 .when('/analysis/', {
				 templateUrl: '/static/partials/analysis.html',
				 controller: 'AnalysisCtrl'
			 })
			 .when('/wait/', {
				 templateUrl: '/static/partials/wait.html'
			 })
			 .otherwise({
				 redirectTo: '/'
			 });
	}
)
.controller('AppCtrl', 
	function($scope, $mdDialog, $http, $location, $window, $timeout, $document, mosaicConfigFactory, mosaicUtilsFactory, analysisSetupFactory) {
		$scope.location = $location;

		$scope.customFullscreen = true;

		$scope.AnalysisLoading = false;

		$scope.mosaicConfigModel=mosaicConfigFactory;
		$scope.mosaicUtilsModel = mosaicUtilsFactory;

		// funcs
		$scope.setupNewAnalysis = function(ev) {
			$scope.newAnalysisFileListing(ev);
			$scope.AnalysisLoading = true;
		};

		$scope.newAnalysisFileListing = function(ev) {
			var dlg = $mdDialog.show({
				controller: 'fileListingCtrl',
				templateUrl: 'static/partials/filelisting.tmpl.html',
				parent: angular.element(document.body),
				targetEvent: ev,
				clickOutsideToClose:true,
				fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
			});

			dlg
			.then(function(response) {
				analysisSetupFactory.dataPath=response.filename.relpath;

				var setupInit = analysisSetupFactory.getSetupData("/new-analysis", {
									dataPath: analysisSetupFactory.dataPath
								});

				setupInit
					.then(function(response) {
						$scope.showNewAnalysisSettings();
					}, function(error) {
						$scope.AnalysisLoading = false;
					});
			}, function() {
				$scope.AnalysisLoading = false;
			});
		};

		$scope.showNewAnalysisSettings = function() {
			$scope.AnalysisLoading = false;	
			$location.path('/setup-analysis/');
		};
		
		$scope.startAnalysis = function(params) {
			$scope.analysisModel.updateAnalysisData(params)
				.then(function (response, status) {	// success
					$mdDialog.hide();

					$location.path('/analysis/');

					$scope.AnalysisLoading = false;

				}, function (error) {	// error
					console.log(error);
				});
			$scope.AnalysisLoading = true;
		};

		$scope.returnToAnalysis = function() {
			$location.path('/analysis/');
		};

		$scope.aboutMosaic = function() {
			$location.path('/about/');				
		};
		
		$scope.pageBack = function() {
			$window.history.back();
		};
	});
		
