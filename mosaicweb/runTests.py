from tests.mosaicUnitTests import _mosaicUnitTests

def runUnitTests():
	testClass=_mosaicUnitTests(object)
	testObject=testClass()

	testObject.initialize_options()
	testObject.verbose=0

	testObject.run()

if __name__ == '__main__':
	runUnitTests()