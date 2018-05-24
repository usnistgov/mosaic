import json
from mosaicweb import app
import mosaic
import unittest 

mosaic.WebServerDataLocation=mosaic.__path__[0]+"/.."

class mwebCommonTest(unittest.TestCase): 
	def setUp(self):
		self.app = app.test_client()
		self.app.testing = True 

	def tearDown(self):
		pass

	def _post(self, url, data):
		return self.app.post(url, data=json.dumps(data), content_type='application/json', follow_redirects=True)
	
	def _get_data(self, result):
		return eval(result.get_data())

	def assertBaseline(self, url, result):
		d=self._get_data(result)

		self.assertEqual(result.status_code, 200)
		self.assertEqual(d["respondingURL"], url)