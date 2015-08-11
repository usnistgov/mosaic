"""
	Common exception types used across the system.
"""
class SettingsTypeError(Exception):
	def __init__(self, value):
		self.value="Setting {0} has an invalid type.".format(str(value).split()[-1])

	def __str__(self):
		return repr(self.value)