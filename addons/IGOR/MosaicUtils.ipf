#pragma rtGlobals=3		// Use modern global access method and strict wave access.
#include <SQLUtils>


//  Simple high level Querry.  Takes two strings in the funciton call
//  Example usage  QuerySQLData("Macintosh HD/Users/joeyr/Documents/Data/SMMS/eventMD-20141105-153606.sqlite", "select BlockDepth, ResTime from metadata where ProcessingStatus='normal' and ResTime > 0.1 and BlockDepth between 0.05 and .8 limit 100")
Function QuerySQLData(db, query)
	String db, query
	String connectionStr= "DRIVER={SQLite3 Driver};DATABASE="+db+";"
	
	SQLHighLevelOp/CSTR={connectionStr, SQL_Driver_COMPLETE}/O/E=1 query
	
	// Print output variables
	Printf "V_flag=%d, V_SQLResult=%d, V_numWaves=%d, S_waveNames=\"%s\"\r", V_flag, V_SQLResult, V_numWaves, S_waveNames
	if (strlen(S_Diagnostics) > 0)
		Printf "Diagnostics: %s\r", S_Diagnostics
	endif
End


Menu "Mosaic"
	"Fetch SQL data. . .", FetchData()
End

//  Grab data from database with an input statment string
Function FetchData()
	String query = QueryBuilder()
	String connectionStr = BuildConnectionString()
	print query
	print connectionStr

	SQLHighLevelOp/CSTR={connectionStr, SQL_Driver_COMPLETE}/O/E=1 query

	// Print output variables
	Printf "V_flag=%d, V_SQLResult=%d, V_numWaves=%d, S_waveNames=\"%s\"\r", V_flag, V_SQLResult, V_numWaves, S_waveNames
	if (strlen(S_Diagnostics) > 0)
		Printf "Diagnostics: %s\r", S_Diagnostics
	endif

End


Function/S QueryBuilder()
	
	string SQ = "select BlockDepth, ResTime from metadata where ProcessingStatus='normal'"
	prompt SQ, "Search Query"
	
	DoPrompt "Enter query action", SQ

	if (V_Flag)
		return "select BlockDepth, ResTime from metadata where ProcessingStatus='normal' and ResTime > 0.1 and BlockDepth between 0.05 and .8 limit 100"	// User Canceled
	endif
	
	Print "Query Statement  =  ",SQ
	
	return SQ
	
End
// Build Connection string from file dialoge  assumes SQLite3 driver
Function/S BuildConnectionString()
	String connectionString
	String DriverString = "DRIVER={SQLite3 Driver}"
	String DatabaseString = DoOpenFileDialog()
	
	connectionString = DriverString+";"+"DATABASE="+DatabaseString+";"
	print connectionString
	return connectionString

End

// open dialog file modified from igor manual  currently configured for mac
// WINDOWS functionality is under development
Function/S DoOpenFileDialog()

	Variable refNum
	String message = "Select a file"
	String outputPath
	String fileFilters = "Data Files (*.sqlite):.sqlite;"
	fileFilters += "All Files:.*;"
	Open /D /R /F=fileFilters /M=message refNum
	outputPath = S_fileName
	String platform = UpperStr(igorinfo(2))
	variable test = cmpstr (platform, "MACINTOSH")
	if (test== 0)
		outputPath = ReplaceString(":", outputPath,"/")
		outputPath = "/Volumes/"+outputPath
		//outputPath = ReplaceString("Macintosh HD", outputPath,"Macintosh HD")
	endif
	
	return outputPath // Will be empty if user canceled

End

function TestVer()

	String platform = UpperStr(igorinfo(2))
	Variable pos = strsearch(platform,"Macintosh OS X",0)
	Return pos >= 0

end