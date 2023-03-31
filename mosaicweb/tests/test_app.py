import pytest 
from mosaicweb.run import getAvailablePort

def test_availablePorts():
	assert getAvailablePort() > 1024