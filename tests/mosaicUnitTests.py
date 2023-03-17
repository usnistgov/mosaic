import mosaic.utilities.mosaicLogging as mlog 

def _mosaicUnitTests(base):
	class mosaicUnitTests(base):
		# log=mlog.mosaicLogging().getLogger(__name__)

		description = "MOSAIC unit test suite is now run using pytest."
		user_options = []

		def initialize_options(self):
			pass

		def finalize_options(self):
			pass

		def run(self):
			print("MOSAIC unit test support within setuptools is deprecated. Run 'pytest' for unit tests.")

	return mosaicUnitTests