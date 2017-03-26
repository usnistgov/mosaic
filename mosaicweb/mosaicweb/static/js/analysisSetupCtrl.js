'use strict';

angular.module('mosaicApp')
	.factory('analysisSetupFactory', function($http, $mdDialog, $mdToast, $q, $document, mosaicUtilsFactory, mosaicConfigFactory) {
		var factory = {};

		factory.dataPath = '';

		factory.analysisSettings = {};
		factory.trajPlot = {};
		factory.trajPlotOriginalCurrent = [];

		factory.ftypes = ["BIN", "ABF", "QDF"];
		factory.selectedFileType = "BIN";

		factory.procAlgoTypes = [
			{
				name: "ADEPT",
				algorithm: "adept"
			}, 
			{
				name: "ADEPT 2-State",
				algorithm: "adept2State"
			}, 
			{
				name: "CUSUM+",
				algorithm: "cusumPlus"
			}
		];
		factory.selectedProcAlgoType = factory.procAlgoTypes[0];

		factory.partAlgoTypes = ["Current Threshold"];
		factory.selectedPartAlgoType = "Current Threshold";

		// factory.analysisSettings.blockSize = 0.25;
		// factory.analysisSettings.dcOffset = 0.0;
		// factory.analysisSettings.currThreshold = 100;
		// factory.analysisSettings.start = 0;
		// factory.analysisSettings.saveToDisk = true;
		// factory.analysisSettings.fitTolerance = 1e-7;
		// factory.analysisSettings.linkRCConstants = false;

		//local vars
		factory.currAuto = true;
		factory.currMeanAuto = 0;
		factory.currSigmaAuto = 0;
		factory.currMeanDisplay = 100;
		factory.currSigmaDisplay = 0;
		factory.currThresholdpA = 100;
		factory.currAuto = false;
		factory.dcOffset = 0;
		factory.start = 0;
		factory.end = '';
		factory.writeEventTS = false;
		factory.FsKHz = 0;

		factory.controlsUpdating = false;
		factory.controlEnabled = false;
		factory.modelInit = false;
		factory.serverError = false;
		factory.requireControlUpdate = false;

		factory.getSetupData = function(url, params) {
			var deferred = $q.defer();

			mosaicUtilsFactory.post(url, params)
				.then(function (response, status) {	// success
					// console.log(response.data);

					if (response.data.respondingURL=='new-analysis') {
						factory.trajPlot=response.data.trajPlot;
						factory.trajPlotOriginalCurrent = factory.trajPlot.data[0].y;

						factory.currMeanAuto=response.data.currMeanAuto;
						factory.currSigmaAuto=response.data.currSigmaAuto;
						factory.selectedFileType=response.data.fileType;

						factory.FsKHz=response.data.FsHz/1000.;

						factory.analysisSettings=angular.fromJson(response.data.settingsString);

						factory.procAlgorithmFromSettings()

						factory.updateLocals();

						if (response.data.warning != '') {
							mosaicUtilsFactory.showErrorToast("WARNING: "+response.data.warning);
						};
						// factory.settingsString=response.data.settingsString;
					} else if (response.data.respondingURL=='processing-algorithm') {
						var data = response.data;

						for (var section in factory.analysisSettings) {
							if ((['adept', 'adept2State', 'cusumPlus'].indexOf(section) != -1)) {
								delete factory.analysisSettings[section];
								factory.analysisSettings[data.procAlgorithmSectionName]=data.procAlgorithm;
							}
						}
					};

				factory.loadingToast = null;
				factory.controlsUpdating = false;
				factory.serverError = false;
				factory.modelInit = true;
				factory.requireControlUpdate=false;

				deferred.resolve(response);
			}, function (error) {	// error
				console.log(error);

				factory.errorString = error.data.errType+": "+error.data.errSummary;

				// if (error.data.errType=='EmptyDataPipeError') {
				// 	factory.showErrorToast("ERROR: Decrease the value of the Start field.");
				// } else if (error.data.errType=='FileNotFoundError') {
				// 	factory.showErrorToast("ERROR: No files found in '"+factory.dataPath+"'");
				// };
				
				factory.serverError=true;
				factory.controlsUpdating = false;
				// factory.loadingToast.hide();

				deferred.reject(error);
			});

			factory.controlsUpdating = true;
			// factory.loadingToast = factory.showLoadingToast();

			return deferred.promise;
		};

		// factory.init = function() {
		// 	factory.getSetupData("/new-analysis", {});
		// };

		factory.procAlgorithmFromSettings = function() {
			if (factory.analysisSettings.hasOwnProperty('adept')) {
				factory.selectedProcAlgoType=factory.procAlgoTypes[0]
			} else if (factory.analysisSettings.hasOwnProperty('adept2State')) {
				factory.selectedProcAlgoType=factory.procAlgoTypes[1]
			} else if (factory.analysisSettings.hasOwnProperty('cusumPlus')) {
				factory.selectedProcAlgoType=factory.procAlgoTypes[2]
			};
		};

		factory.arrayOffset = function(arr, offset) {
			var res = arr.map( function(value) { 
				return value - offset;
			});
			return res;
		};


		factory.showLoadingToast = function() {
			var toast = $mdToast.show({
				hideDelay   : 0,
				// position    : 'bottom right',
				controller  : 'LoadingToastCtrl',
				templateUrl : 'static/partials/loading-toast-template.tmpl.html'
			});
		};

		factory.toggleCurrAuto = function() {
			if( factory.currAuto ) {
				factory.currMeanDisplay = factory.currMeanAuto;
				factory.currSigmaDisplay = factory.currSigmaAuto;
			};
		}
		//Update funcs for local vars when advanced settings are changed
		factory.updateLocals = function() {
			factory.updateCurrAuto();
			factory.updateCurrThresholdpA();
			factory.updateTrajIO();
			factory.procAlgorithmFromSettings();

			factory.writeEventTS=factory.analysisSettings.eventSegment.writeEventTS ? true : false;
		};

		factory.updateCurrAuto = function() {
			if ( factory.analysisSettings.eventSegment.meanOpenCurr == -1 || factory.analysisSettings.eventSegment.sdOpenCurr == -1 ) {
				factory.currAuto = true;
				factory.currMeanDisplay = Math.round(factory.currMeanAuto*1000)/1000;
				factory.currSigmaDisplay = Math.round(factory.currSigmaAuto*1000)/1000;
			} else {
				factory.currAuto = false;
				factory.currMeanDisplay = Math.round(factory.analysisSettings.eventSegment.meanOpenCurr*1000)/1000;
				factory.currSigmaDisplay = Math.round(factory.analysisSettings.eventSegment.sdOpenCurr*1000)/1000;
			};
		};

		factory.updateCurrThresholdpA = function() {
			var thr=factory.analysisSettings.eventSegment.eventThreshold;

			factory.currThresholdpA = Math.round( (Math.abs(factory.currMeanDisplay)-thr*factory.currSigmaDisplay)*100)/100;
		};

		factory.updateTrajIO = function() {
			var settings = factory.analysisSettings;

			switch(factory.selectedFileType) {
				case 'QDF':
					factory.start=settings.qdfTrajIO.start;
					factory.end=settings.qdfTrajIO.end;
					factory.dcOffset=settings.qdfTrajIO.dcOffset;
					break;
				case 'ABF':
					factory.start=settings.abfTrajIO.start;
					factory.end=settings.abfTrajIO.end;
					factory.dcOffset=settings.abfTrajIO.dcOffset;
					break;
				case 'BIN':
					factory.start=settings.binTrajIO.start;
					factory.end=settings.binTrajIO.end;
					factory.dcOffset=settings.binTrajIO.dcOffset;
					break;
				default:
					factory.start=0.0;
					factory.end='';
					factory.dcOffset=0.0;
			};
		};

		// update analysisSettings with display values
		factory.reconcileSettings = function() {
			var settings = factory.analysisSettings;

			if (factory.currAuto) {
				settings.eventSegment.meanOpenCurr=-1;
				settings.eventSegment.sdOpenCurr=-1;
			} else {
				settings.eventSegment.meanOpenCurr=factory.currMeanDisplay;
				settings.eventSegment.sdOpenCurr=factory.currSigmaDisplay;
			};

			settings.eventSegment.eventThreshold=(factory.currMeanDisplay-factory.currThresholdpA)/factory.currSigmaDisplay;
			settings.eventSegment.writeEventTS=factory.writeEventTS ? 1 : 0;

			switch(factory.selectedFileType) {
				case 'QDF':
					settings.qdfTrajIO.start=factory.start;
					settings.qdfTrajIO.end=factory.end;
					settings.qdfTrajIO.dcOffset=factory.dcOffset;
					break;
				case 'ABF':
					settings.abfTrajIO.start=factory.start;
					settings.abfTrajIO.end=factory.end;
					settings.abfTrajIO.dcOffset;
					break;
				case 'BIN':
					settings.binTrajIO.start=factory.start;
					settings.binTrajIO.end=factory.end;
					settings.binTrajIO.dcOffset=factory.dcOffset;
					break;
				default:
					settings.abfTrajIO.start=0.0;
					settings.abfTrajIO.dcOffset=0.0
			};
			
		};

		// Init on start
		// factory.init();

		return factory;

	})
	.controller('LoadingToastCtrl', function($scope, $mdToast) {
		$scope.hide = function() {
			$mdToast.hide();
		};
	})
	.controller('analysisSetupCtrl', function($scope, $mdDialog, $q, $location, analysisSetupFactory, AdvancedSettingsFactory, mosaicConfigFactory) {
		$scope.model = analysisSetupFactory;
		$scope.advancedSettingsModel = AdvancedSettingsFactory;
		// $scope.analysisModel = AnalysisFactory;
		$scope.mosaicConfigModel = mosaicConfigFactory;

		// watch
		$scope.$watch('newAnalysisForm.blockSize.$pristine', function() {
			if ($scope.newAnalysisForm.blockSize.$valid && !$scope.model.controlsUpdating) {
				$scope.model.requireControlUpdate=true;
			};
		});
		$scope.$watch('newAnalysisForm.start.$pristine', function() {
			if ($scope.newAnalysisForm.blockSize.$valid && !$scope.model.controlsUpdating) {
				$scope.model.requireControlUpdate=true;
			};
		});
		$scope.$watch('newAnalysisForm.selectedProcAlgoType.$pristine', function() {
			if ($scope.advancedSettingsModel.procAlgoLocalChanges) {
				$scope.showConfirmDialog(
					'Discard Processing Algorithm Changes?',
					"Changes to '"+ $scope.advancedSettingsModel.procAlgo+ "' will be lost if you proceed.",
					'Proceed',
					'Cancel'
				).then(function(response) {
					// console.log(response);
					$scope.model.getSetupData('processing-algorithm',
							{
								procAlgorithm: $scope.model.selectedProcAlgoType.algorithm
							}
						);
						$scope.advancedSettingsModel.procAlgoLocalChanges=false;
						$scope.newAnalysisForm.$setPristine();
					}, function(error) {
						switch ($scope.advancedSettingsModel.procAlgo) {
							case 'adept':
								$scope.model.selectedProcAlgoType=$scope.model.procAlgoTypes[0];
								break;
							case 'adept2State':
								$scope.model.selectedProcAlgoType=$scope.model.procAlgoTypes[1];
								break;
							case 'cusumPlus':
								$scope.model.selectedProcAlgoType=$scope.model.procAlgoTypes[2];
								break;		
						};
						$scope.newAnalysisForm.$setPristine();
					}
				);
			} else {
				$scope.model.getSetupData('processing-algorithm',
					{
						procAlgorithm: $scope.model.selectedProcAlgoType.algorithm
					}
				);
				$scope.newAnalysisForm.$setPristine();
			};
		});		
		$scope.$watch('model.currThresholdpA', function() {
			if ($scope.newAnalysisForm.blockSize.$valid && !$scope.model.controlsUpdating) {
				$scope.model.trajPlot.data[2].y=[$scope.model.currThresholdpA, $scope.model.currThresholdpA];
				$scope.model.analysisSettings.eventSegment.eventThreshold=($scope.model.currMeanDisplay-$scope.model.currThresholdpA)/$scope.model.currSigmaDisplay;
			}
		});
		
		$scope.selectProcAlgo = function() {
			console.log($scope.model.selectedProcAlgoType);
		};

		$scope.showConfirmDialog = function(title, content, okText, cancelText ) {
			var deferred = $q.defer();

			var confirm = $mdDialog.confirm()
							.title(title)
							.textContent(content)
							.ariaLabel(title)
							.ok(okText)
							.cancel(cancelText);

			$mdDialog.show(confirm).then(function() {
				deferred.resolve('OKAY');
			}, function() {
				deferred.reject('CANCEL');
			});
			return deferred.promise;
		};

		//dialog functions
		$scope.cancel = function() {
			$mdDialog.cancel();
		};
		$scope.answer = function(answer) {
			var response={};

			response.answer=answer;
			response.analysisSettings=$scope.model.analysisSettings;

			$mdDialog.hide(response);
		};

		// local functions
		$scope.getFileType = function() {
			if ($scope.model.selectedFileType !== undefined) {
				return $scope.model.selectedFileType;
			} else {
				return "Select a file type";
			}
		};

		$scope.requireControlsUpdate = function() {
			$scope.model.requireControlUpdate=true;
		};

		$scope.getPartAlgoType = function() {
			if ($scope.model.selectedPartAlgoType !== undefined) {
				return $scope.model.selectedPartAlgoType;
			} else {
				return "Select a parition algorithm";
			}
		};

		$scope.getProcAlgoType = function() {
			if ($scope.model.selectedProcAlgoType !== undefined) {
				return $scope.model.selectedProcAlgoType.name;
			} else {
				return "Select a processing algorithm";
			}
		};

		$scope.formDisabled = function() {
			return (
					$scope.model.controlsUpdating 
					|| $scope.newAnalysisForm.start.$invalid
					|| $scope.newAnalysisForm.end.$invalid
					|| $scope.newAnalysisForm.blockSize.$invalid
					|| $scope.mosaicConfigModel.analysisRunning
				) ? true : false;
		};

		$scope.showAdvancedSettings = function() {
			$scope.model.reconcileSettings();

			$mdDialog.show({
				skipHide: true,
				locals: {analysisSettings: $scope.model.analysisSettings, selectedFileType: $scope.model.selectedFileType},
				controller: 'AdvancedSettingsCtrl',
				templateUrl: 'static/partials/advancedSettings.tmpl.html',
				parent: angular.element(document.body),
				clickOutsideToClose:false
			})
			.then(function(answer) {
				$scope.model.analysisSettings=angular.fromJson(answer.analysisSettings);
				$scope.model.updateLocals();

				$scope.model.requireControlUpdate=answer.controlsUpdateFlag;

			}, function() {
				$scope.status = 'You cancelled the dialog.';
			});
		};

		$scope.updateControls = function() {
			$scope.model.reconcileSettings();
			$scope.model.getSetupData("/new-analysis",
				{
					'settingsString': JSON.stringify($scope.model.analysisSettings),
					'dataPath': $scope.model.dataPath
					// 'sessionID': $scope.mosaicConfigModel.sessionID
				}
			).then(function(response) {
				$scope.newAnalysisForm.start.$setValidity("max", true);
			}, function(error) {
				if (error.data.errType = 'EmptyDataPipeError') {
					$scope.newAnalysisForm.start.$setValidity("max", false);
				};
			});
			$scope.model.requireControlUpdate=false;
			$scope.newAnalysisForm.$setPristine();
		};

		$scope.startAnalysis = function() {
			$location.path('/analysis/').search({sid:$scope.mosaicConfigModel.sessionID});
			$scope.model.controlsUpdating=false;
			// $scope.analysisModel.updateAnalysisData(
			// 	{
			// 		analysisSettings: $scope.model.analysisSettings
			// 	}
			// )
			// .then(function (response, status) {	// success
			// 	$scope.model.controlsUpdating=false;
			// 	// $location.path('/analysis/?s=adfjdskafa');
			// }, function (error) {	// error
			// 	console.log(error);
			// });
			// $scope.model.controlsUpdating=true;

		};
	});