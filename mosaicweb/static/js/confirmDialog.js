'use strict';

angular.module('mosaicApp')
	.controller('ConfirmDialogCtrl', function($scope, $mdDialog) {
		$scope.showConfirmDialog = function(title, content, okText, cancelText ) {
			var confirm = $mdDialog.confirm()
						.title(title)
						.textContent(content)
						.ariaLabel(title)
						.ok(okText)
						.cancel(cancelText);

			$mdDialog.show(confirm).then(function() {
				$scope.status = "OKAY";
			}, function() {
				$scope.status = "CANCEL";
			});
		};
	})