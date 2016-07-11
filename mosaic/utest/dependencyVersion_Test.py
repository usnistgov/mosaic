class DependencyVersionTest(object):
	def runTestCase(self, dep, minver):
		module=__import__(dep)

		assert module.__version__ >= minver

class DepencencyVersion_TestSuite(DependencyVersionTest):
	def test_dependencyVersion(self):
		with open('../../requirements.txt', 'r') as req:
			modlist=req.read()

		for mod in modlist.split():
			m,v=mod.split('==')

			# This is a hack to handle non-essential deps
			if m not in ['pyinstaller', 'PyWavelets']:
				yield self.runTestCase, m, v

