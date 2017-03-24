'use strict';

angular.module('mosaicApp')
	.factory('AnalysisStatisticsFactory', function($http, $q, mosaicUtilsFactory) {
			var factory = {};

			factory.analysisStats = {};
			factory.errorPercent = 0;
			factory.warnPercent = 0;

			factory.updateErrorStats = function() {
				mosaicUtilsFactory.post('/analysis-statistics', {})
					.then(function(response, status) {
						factory.analysisStats=response.data;

						factory.errorPercent=Math.round(factory.analysisStats.fractionError*10000)/100.;
						factory.warnPercent=Math.round(factory.analysisStats.fractionWarn*10000)/100.;				

						factory.errorStats.data[0].x=[response.data.fractionNormal*response.data.nTotal];
						factory.errorStats.data[1].x=[response.data.fractionWarn*response.data.nTotal];
						factory.errorStats.data[2].x=[response.data.fractionError*response.data.nTotal];
					}, function(error) {
						console.log(error);
					});
			};

			factory.errorStats = {
				data: [
					{
						name: 'normal',
						x: [200],
						y: [0],
						orientation: 'h',
						marker: {
							color: 'rgb(16, 108, 200)',
						},
						width: 0.5,
						type: 'bar'
					},
					{
						name: 'warn',
						x: [42],
						y: [0],
						orientation: 'h',
						type: 'bar',
						marker: {
							color: 'rgb(255,153,51)'
						},
						width: 0.5
					},
					{
						name: 'error',
						x: [14],
						y: [0],
						orientation: 'h',
						type: 'bar',
						marker: {
							color: 'rgb(255, 82, 82)'
						},
						width: 0.5
					}
				],
				layout: {
					xaxis: {
						autorange: true,
						showgrid: false,
						zeroline: false,
						showline: false,
						autotick: false,
						ticks: '',
						showticklabels: false
					},
					yaxis: {
						autorange: true,
						showgrid: false,
						zeroline: false,
						showline: false,
						autotick: false,
						ticks: '',
						showticklabels: false
					},
					barmode: 'stack',
					showlegend: true,
					legend: {
						x: 1,
						y: 0,
						traceorder: 'normal',
						font: {
							family: 'Roboto, Helvetica',
							size: 12,
							color: '#000'
						}
					},
					margin: {
						l: 10,
						r: 0,
						b: 0,
						t: 0,
						pad: 0
					},
					paper_bgcolor: 'rgba(0,0,0,0)',
					plot_bgcolor: 'rgba(0,0,0,0)',
					hovermode: 'x',
					height: 75
				},
				options: {}
			};

			factory.updateErrorStats();

			return factory;
		}
	)
	.controller('AnalysisStatisticsCtrl', function($scope, $mdDialog, $interval, AnalysisStatisticsFactory) {
		$scope.model = AnalysisStatisticsFactory;

		$scope.customFullscreen = true;

		// $scope.model.updateErrorStats();

		$scope.updateStats = function() {
			$interval(function() {
				$scope.model.updateErrorStats();
			}, 5000);
		};

		$scope.hide = function() {
			$mdDialog.hide();
		};
		$scope.cancel = function() {
			$mdDialog.cancel();
		};
		$scope.answer = function(answer) {
			$mdDialog.hide(answer);
		};

		$scope.updateStats();
	});
