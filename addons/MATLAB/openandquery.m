% Script to open, query, and close SQLite database.  And then convert
% queried structure into an array.
% 
% USAGE
% 1.  Replace the example database path in line 20 with the correct path to
%     your database
% 2.  Replace the example queries in line 24 as relevant to your
%     database/project
% 3.  Run the script
% 
% NOTE
% The file path below (in line 20) is typical for Linux.  If you are using
% Windows simply replace it with the correct file path (e.g.,
% C:\Data\nanoporedata.sqlite).  Then run the script.
% 
% Ken Vaz
% December 3, 2014
% NIST, Gaithersburg, MD 20899

dbname = 'C:\sqlite\eventMD-PEG29-Reference.sqlite';	% Enter the path, including the database name, within the quotes

mksqlite('open',dbname);                                % Open the database
fieldnames = mksqlite('PRAGMA table_info(metadata)');	  % Read in all fieldnames
querytemp = mksqlite('select AbsEventStart, BlockDepth from metadata'); % Querying the database
mksqlite('close');                                      % Close the database

data = (cell2mat(struct2cell(querytemp)))';             % Format the data read into array(s), from a structure
