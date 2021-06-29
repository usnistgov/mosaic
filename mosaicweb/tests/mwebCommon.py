import unittest 
import json
import mosaic
from mosaicweb import app
from mosaic.utilities.util import eval_

class mwebSimpleCommonTest(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

class mwebCommonTest(unittest.TestCase):
	def setUp(self):
		self.app = app.test_client()
		self.app.testing = True 
		self._post( '/set-data-path', dict( dataPath=mosaic.__path__[0]+"/.." )) 

	def tearDown(self):
		pass

	def _post(self, url, data):
		return self.app.post(url, data=json.dumps(data), content_type='application/json', follow_redirects=True)
	
	def _get_data(self, result):
		return eval_(result.get_data())

	def assertBaseline(self, url, result):
		d=self._get_data(result)

		self.assertEqual(result.status_code, 200)
		self.assertEqual(d["respondingURL"], url)

	def assertBaselineError(self, url, result):
		d=self._get_data(result)

		self.assertEqual(result.status_code, 500)
		self.assertEqual(d["respondingURL"], url)