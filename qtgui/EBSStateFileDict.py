import csv

class EBSStateFileDict(dict):
	def __init__(self, stateFileName):
		with open(stateFileName, 'rb') as csvfile:
			statereader = csv.reader(csvfile, delimiter='=', quotechar='|')
	
			[ self.update({ str(row[0]).rstrip() : (str(row[1]).rstrip()).lstrip() }) for row in statereader if len(row) > 1 ]

	def __getitem__(self, key):
		val = dict.__getitem__(self, key)

		if key == "FB Resistance":
			if val.endswith("GOhms"):
				return float(val.rstrip("GOhms"))*1E9
		elif key == "FB Capacitance":
			if val.endswith("pF"):
				return float(val.rstrip("pF"))*1E-12
		elif key == "Sample Rate":
			if val.endswith("KHz"):
				return float(val.rstrip("KHz"))*1E3

		return val

	def pop(self, key, default):
		try:
			return self[key]
		except KeyError:
			return default
			
if __name__ == "__main__":
	# s=EBSStateFileDict('/Users/arvind/Research/Experiments/PEG29EBSRefData/20120323/singleChan/SingleChan-0001_state.txt')
	s=EBSStateFileDict('C:\\temp\\SingleChan-0001_state.txt')

	print s

	print
	print

	print 'FB Resistance =', float(s['FB Resistance'])/1e9, "GOhm"
	print 'FB Capacitance =', float(s['FB Capacitance'])/1e-12, "pF"
	print 'Sample Rate (Hz) = ', int(s['Sample Rate (Hz)'])/1e6, "MHz"

	# s=EBSStateFileDict('/Users/arvind/Desktop/POM ph5.45 m60_6/POM ph5.45 m60_6-0001_State.txt')

	# print s

	# print
	# print

	# print 'FB Resistance =', float(s['FB Resistance'])/1e9, "GOhm"
	# print 'FB Capacitance =', float(s['FB Capacitance'])/1e-12, "pF"
	# print 'Sample Rate = ', int(s['Sample Rate'])/1e6, "MHz"