'use strict';

angular.module('mosaicApp', ['ngRoute', 'ngMaterial', 'ngMessages', 'ngAnimate', 'plotly', 'base64'])
.config(
	function($mdThemingProvider) {
		var mosaicPrimary = {
			'50': '#7683d6',
			'100': '#6371d0',
			'200': '#4f60cb',
			'300': '#3b4ec5',
			'400': '#3546b2',
			'500': '#2f3e9e',
			'600': '#29368a',
			'700': '#232f77',
			'800': '#1d2763',
			'900': '#181f4f',
			'A100': '#8a95dc',
			'A200': '#9da7e2',
			'A400': '#b1b9e8',
			'A700': '#12173c',
			'contrastDefaultColor': 'light',
			'contrastDarkColors': ['50', '100', '200', '300', 'A100', 'A400']
		};
		$mdThemingProvider
			.definePalette('mosaicPrimary', mosaicPrimary);

		var mosaicAccent = {
			'50': '#500a24',
			'100': '#670d2e',
			'200': '#7d1038',
			'300': '#941342',
			'400': '#ab154c',
			'500': '#c11856',
			'600': '#e4286d',
			'700': '#e73f7c',
			'800': '#ea568c',
			'900': '#ed6c9b',
			'A100': '#e4286d',
			'A200': '#d81b60',
			'A400': '#c11856',
			'A700': '#ef83ab',
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
				 templateUrl: '/static/partials/404.html'
			 });
	}
)
.controller('AppCtrl', 
	function($scope, $mdDialog, $mdMenu, $http, $location, $window, $timeout, $document, mosaicConfigFactory, mosaicUtilsFactory, analysisSetupFactory, AnalysisFactory, FileListingFactory) {
		$scope.location = $location;

		$scope.customFullscreen = true;

		$scope.AnalysisLoading = false;

		$scope.appAnalytics = true;
		$scope.showAnalyticsOptions = true;

		$scope.analysisModel=AnalysisFactory;
		$scope.mosaicConfigModel=mosaicConfigFactory;
		$scope.mosaicUtilsModel = mosaicUtilsFactory;

		// funcs
		$scope.setupNewAnalysis = function(ev) {
			FileListingFactory.setDialogMode("directory");
			$scope.fileListing(ev);
			$scope.AnalysisLoading = true;
		};

		$scope.loadPreviousAnalysis = function(ev) {
			FileListingFactory.setDialogMode("sqlite");
			$scope.fileListing(ev);
			$scope.AnalysisLoading = true;
		};

		$scope.analyticsUpdate = function (ev) {
			$scope.appAnalytics=!$scope.appAnalytics;

			$scope.analyticsPost({
				appAnalytics: $scope.appAnalytics
			})
		};

		$scope.analyticsPost = function(params) {
			mosaicUtilsFactory.post('/analytics', params)
			.then(function(response) {
				$scope.appAnalytics = response.data.appAnalytics;	
				$scope.showAnalyticsOptions = response.data.showAnalyticsOptions;
			}, function(error) {
				$scope.AnalysisLoading = false;	
				console.log(error);
			});
		};

		$scope.fileListing = function(ev) {
			$mdDialog.show({
				controller: 'fileListingCtrl',
				templateUrl: 'static/partials/filelisting.tmpl.html',
				parent: angular.element(document.body),
				targetEvent: ev,
				clickOutsideToClose:true,
				fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
			})
			.then(function(response) {
				if (FileListingFactory.dialogMode=="directory") {
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
				} else if(FileListingFactory.dialogMode=="sqlite") {
					mosaicUtilsFactory.post('/load-analysis', {
						databaseFile: response.filename.relpath
					})
					.then(function(response) {
						$scope.AnalysisLoading = false;	
						$location.path('/analysis/').search({sid: response.data.sessionID});
					}, function(error) {
						$scope.AnalysisLoading = false;	
						console.log(error);
					});
					
				};
			}, function() {
				$scope.AnalysisLoading = false;
			});
		};

		$scope.showNewAnalysisSettings = function() {
			$scope.AnalysisLoading = false;	
			$location.path('/setup-analysis/').search({sid: $scope.mosaicConfigModel.sessionID});
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

		// init
		$scope.analyticsPost({});
	});
		
