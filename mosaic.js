angular
    .module('mosaicApp', ['ngMaterial', 'users'])
    .config(function($mdThemingProvider, $mdIconProvider){
            // $mdThemingProvider.theme('default')
            //     .primaryPalette('brown')
            //     .accentPalette('red');

    })
    .controller('AppCtrl', function ($scope, $timeout, $mdSidenav, $mdUtil, $log) {
      $scope.baseURL = "https://abalijepalli.github.io/mosaic"
      $scope.docURL = $scope.baseURL+"/html/"
      $scope.mailingListURL = $scope.baseURL+"/html/doc/mailingList.html"
      $scope.scriptURL = $scope.baseURL+"/html/doc/ScriptingandAdvancedFeatures.html"
      $scope.algoURL = $scope.baseURL+"/html/doc/Algorithms.html"
      $scope.extendURL = $scope.baseURL+"/html/doc/Extend.html"
      $scope.addonURL = $scope.baseURL+"/html/doc/Addons.html"
      $scope.guiURL = $scope.baseURL+"/html/doc/GraphicalInterface.html"
      
      $scope.toggleLeft = buildToggler('left');
      $scope.toggleRight = buildToggler('right');
      /**
       * Build handler to open/close a SideNav; when animation finishes
       * report completion in console
       */
      function buildToggler(navID) {
        var debounceFn =  $mdUtil.debounce(function(){
              $mdSidenav(navID)
                .toggle()
                .then(function () {
                  $log.debug("toggle " + navID + " is done");
                });
            },300);
        return debounceFn;
      }
    })
    .controller('LeftCtrl', function ($scope, $timeout, $mdSidenav, $log) {
      $scope.close = function () {
        $mdSidenav('left').close()
          .then(function () {
            $log.debug("close LEFT is done");
          });
      };
    });