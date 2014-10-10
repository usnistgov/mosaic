.. _working-with-sqlite-sec:

Work with SQLite
---------------------------------------------

*<name>* stores the output of an analysis in a SQLite database as described in the :ref:`database-page` section. Interacting with the data through the `Structured Query Language (SQL) <http://en.wikipedia.org/wiki/SQL>`_ is a flexible approach to further analyze or plot the output. Here we provide a few detailed examples of the common ways in which the output of *<name>* can be queried for further processing.

SQL queries are run using the *select* command. In its simplest form, a query can return the entire contents of a table using the syntax below. The statement below selects all columns *(select \*)* from the table specified by *<tablename>*.

.. sourcecode:: sql
   
    select * from <tablename>

The power of SQL lies in its ability to restrict results to match specific criteria. This is accomplished with the *where* clause described next. SQL queries can be very fast event for large databases. 

It is often desirable to only include events that were successfully fit in a plot or other analysis. All :ref:`eventprocess-page` algorithms implemented in *<name>* store a *ProcessingStatus* column in the output database. This enables one to easily query events that were successfully processed. This is easily accomplished with the query below, which returns all columns for events that were successfully processed (*ProcessingStatus=normal*).

.. sourcecode:: sql
   
    select * from metadata where ProcessingStatus='normal'

It is not always necessary to retrieve every column for events that fit a certain criteria. For example, :ref:`gui-blockdepth-sec` in the GUI displays a histogram of the blockade depths that match a user specified criteria. This is accomplished within the GUI by a query similar to the one shown below. There are two important differences between the query below and previous examples: i) by replacing \* with *BlockDepth*, we only retrieve the *BlockDepth* column for events that meet the criteria specified after the *where* clause, and ii) selection criteria specified after where can be nested as seen further with the examples below.


.. sourcecode:: sql
   
    select BlockDepth from metadata where ProcessingStatus='normal' and ResTime > 0.2


.. sourcecode:: sql
   
    select BlockDepth from metadata where ProcessingStatus='normal' and ResTime > 0.2 
    and BlockDepth between 0.1 and 0.5


Multiple columns can be retrieved from a table by providing a comma separated list of column names after the *select* clause. As in previous cases, only events that meet a specified criteria are returned. The results can be ordered using *order*. In this example we sort the results in ascending order by the *AbsEventStart* column.

.. sourcecode:: sql
   
    select BlockDepth, ResTime, AbsEventStart from metadata where ProcessingStatus='normal' 
    order by AbsEventStart ASC

Finally, SQL allows the number of results returned to be limited using the *limit* clause. In this example, we limit the query results to the first 500 rows that meet our criteria.

.. sourcecode:: sql
   
    select AbsEventStart from metadata where ProcessingStatus='normal' 
    order by AbsEventStart ASC limit 500



