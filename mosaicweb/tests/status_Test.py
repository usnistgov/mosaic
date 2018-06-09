import unittest
from mosaicweb.tests.mwebCommon import mwebCommonTest

class Status_TestSuite(mwebCommonTest):
	def test_init(self):
		result=self._post( '/initialization', dict() )

		d=self._get_data(result)

		self.assertBaseline("initialization", result)

	def test_about(self):
		result=self._post( '/about', dict() )

		d=self._get_data(result)

		self.assertBaseline("about", result)
		# self.assertGreaterEqual(int(d["ver"][0]), 2)

	def test_listActiveSessions(self):
		result=self._post( '/list-active-sessions', dict() )

		d=self._get_data(result)

		self.assertBaseline("list-active-sessions", result)
		self.assertGreaterEqual(len(d["sessions"]), 0)
