'use strict';

angular.module('mosaicApp')
	.factory('AnalysisStatisticsFactory', function($http, $q, mosaicUtilsFactory, mosaicConfigFactory) {
			var factory = {};

			factory.analysisStats = {};
			factory.errorPercent = 0;
			factory.warnPercent = 0;
			factory.normalPercent = 0;

			factory.analysisProgressMode='indeterminate';

			factory.updateErrorStats = function() {
				if (mosaicConfigFactory.sessionID != null) {
					mosaicUtilsFactory.post('/analysis-statistics', {})
					.then(function(response, status) {
						factory.analysisStats=response.data;

						factory.errorPercent=Math.round(factory.analysisStats.fractionError*10000)/100.;
						factory.warnPercent=Math.round(factory.analysisStats.fractionWarn*10000)/100.;	
						factory.normalPercent=Math.round(factory.analysisStats.fractionNormal*10000)/100.;				

						factory.errors=Math.round(response.data.fractionError*response.data.nTotal);
						factory.warnings=Math.round(response.data.fractionWarn*response.data.nTotal);
						factory.normal=Math.round(response.data.fractionNormal*response.data.nTotal);

						if (factory.analysisStats.analysisProgressPercent == 'n/a') {
							factory.analysisProgressMode='indeterminate';	
						} else {
							factory.analysisProgressMode='determinate';
						};
						
						factory.errorStats.data[0].x=[Math.round(response.data.fractionNormal*response.data.nTotal)];
						factory.errorStats.data[1].x=[Math.round(response.data.fractionWarn*response.data.nTotal)];
						factory.errorStats.data[2].x=[Math.round(response.data.fractionError*response.data.nTotal)];
					}, function(error) {
						console.log(error);
					});
				}
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
							// color: 'rgb(255, 82, 82)'
							color: 'rgb(255, 41, 41)'
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
						xanchor:"left",
						yanchor:"bottom",
						x:0,
						y:-0.6,
						orientation: "h",
						traceorder: 'normal',
						font: {
							family: 'Roboto, Helvetica',
							size: 14,
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
					hovermode: 'closest',
					hoverinfo: 'x+name',
					height: 125
				},
				options: {
					displayModeBar: false
				}
			};

			return factory;
		}
	)
	.controller('AnalysisStatisticsCtrl', function($scope, $mdDialog, $interval, AnalysisStatisticsFactory) {
		$scope.model = AnalysisStatisticsFactory;

		$scope.customFullscreen = true;

		$scope.infoStyle="color: #696969; padding:0; margin:0; padding-left: 16px; padding-bottom: 12px;";
		$scope.statsStyle="color: #696969; padding:0; margin:0; padding-left: 16px; padding-bottom: 12px;";

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

		$scope.model.updateErrorStats();
	});
