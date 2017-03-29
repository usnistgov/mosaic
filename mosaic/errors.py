# -*- coding: utf-8 -*-
"""
	Return an error string for fitting errors.

	:Created:	3/12/2016
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		5/27/16 	AB 	Added support for warning codes.
		5/27/16 	AB 	Added support for ADEPT initial guess errors that end in '_init'
		3/12/16		AB	Initial version	
"""
__all__ = ["errors"]

class errors(dict):
	def __init__(self):
		self.update(errors.error_dict)

	def __getitem__(self, key):
		try:
			if key.endswith("_init"):
				val=dict.__getitem__(self, key.split("_")[0])
			else:
				val=dict.__getitem__(self, key)
			return val
		except KeyError:
			return "Unknown error"

	error_dict={
		"eInvalidEvent" 		: "A valid event was not found in the data.",
		"eInvalidStates" 		: "Fewer than two states were identified in the event.",
		"eNegativeEventDelay" 	: "The residence times of one or more states are negative.",
		"eInvalidResTime" 		: "The residence times of one or more states are negative.",
		"eInvalidStartTime" 	: "The start time estimate of the event is past the end of the event data.",
		"eMaxLength" 			: "The event length exceeds the 'MaxEventLength' setting.",
		"eFitUserStop" 			: "Analysis was stopped by the user.",
		"eFitFailure" 			: "The least squares fit of the event failed.",
		"eFitConvergence" 		: "The least squares fit of the event did not converge to the specified tolerance.",
		"eInvalidChiSq" 		: "The reduced chi squared estimate of the fit was not a number.",
		"eInvalidOpenChCurr" 	: "The open channel current estimate of the fit was not a number",
		"eInvalidBlockDepth"	: "The blockade depth is outside the valid range of 0 to 1.",
		"eInvalidRCConst" 		: "The RC constant estimate of the event transient is negative or not a number.",

		"wInvalidRedChiSq" 		: "The reduced chi squared estimate of the fit was not a number.",
		"wInitGuessUnchanged"	: "At least one optimized fit parameter is unchanged from the initial guess."
	}


if __name__ == '__main__':
	e=errors()

	print e["eInvalidEvent"]
	print e["eInvalidRCConst"]
	print e["eInvalidStates_init"]
	print e["wInvalidRedChiSq"]
