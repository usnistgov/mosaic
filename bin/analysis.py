import mosaic.apps.SingleChannelAnalysis

import mosaic.partition.eventSegment as es

import mosaic.process.adept2State as adept2State
import mosaic.process.adept as adept 
import mosaic.process.cusumPlus as cusumPlus

from mosaic.trajio.qdfTrajIO import *
from mosaic.trajio.abfTrajIO import *
from mosaic.trajio.tsvTrajIO import *
from mosaic.trajio.binTrajIO import *

from mosaic.filters.besselLowpassFilter import *
from mosaic.filters.waveletDenoiseFilter import *

# mosaic.apps.SingleChannelAnalysis.SingleChannelAnalysis(
# 			'data',
# 			qdfTrajIO, 
# 			None,
# 			es.eventSegment,
# 			adept.adept
# 		).Run()

mosaic.apps.SingleChannelAnalysis.SingleChannelAnalysis(
			'data',
			qdfTrajIO, 
			None,
			es.eventSegment,
			adept2State.adept2State
		).Run()

# mosaic.apps.SingleChannelAnalysis.SingleChannelAnalysis(
# 			'data',
# 			qdfTrajIO, 
# 			None,
# 			es.eventSegment,
# 			cusumPlus.cusumPlus
# 		).Run()
