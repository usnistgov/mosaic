import sys
import os
import glob
import string

class NotFoundError(Exception):
	pass

def path_separator():
	"""
		Automatically detect the current OS and return the appropriate file separator
	"""
	return {'darwin' : '/', 'linux' : '/', 'win32' : '\\', 'win64' : '\\'}[sys.platform]

def resource_path(filename):
	"""
		Find the location of a file in the source tree and return its absolute path.
		If the code is runthe function is called from (e.g. from within pyinstaller)
	"""
	sep=path_separator()
	dirlist=string.split( os.path.dirname( os.path.abspath(__file__) ), sep )[:-1]

	if filename==".settings" or filename=="settings":
		if os.path.isfile ( str(sep.join( dirlist ))+sep+filename ):
			return str(sep.join( dirlist ))
		elif os.path.isfile ( str(sep.join( dirlist[:-1] ))+sep+filename ):
			return str(sep.join( dirlist[:-1] ))
		else:
			NotFoundError('.settings')
	else:
		# print os.environ.get("_MEIPASS2", os.path.abspath(".") )
		if os.path.isfile( format_path(str(sep.join( dirlist ))+'/qtgui/ui/'+filename) ):
			# print format_path(str(sep.join( dirlist ))+'/qtgui/ui/'+filename)
			return format_path(str(sep.join( dirlist ))+'/qtgui/ui/'+filename)
		elif os.path.isfile ( format_path(sep.join( dirlist )+'/ui/'+filename) ):
			# print format_path(str(sep.join( dirlist ))+'/ui/'+filename)
			return format_path(str(sep.join( dirlist ))+'/ui/'+filename)
		# elif hasattr(sys, "_MEIPASS"):


def last_file_in_directory(path, filefilter):
	"""
		Return the last file matching filefilter in path
	"""
	try:
		return glob.glob(path+path_separator()+filefilter)[-1]
	except IndexError:
		return None

def format_path(path):
	""" 
		Take a standard *nix or mixed path and convert it to a windows path if needed.
	"""
	sep=path_separator()
	return (path.replace('/', sep)).replace('\\', sep)


if __name__ == '__main__':
	print resource_path('.settings')
	print last_file_in_directory('C:\\temp\\', '*sqlite')
	print format_path('C:\\temp\\*sqlite')
	# return os.path.join(
	# 	os.environ.get(
	# 		"_MEIPASS2",
	# 		os.path.abspath(".")
	# 	),
	# 	filename
	# )
