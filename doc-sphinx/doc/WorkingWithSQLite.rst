.. _working-with-sqlite-page:

Work with SQLite
=================================

*<name>* stores the output of an analysis in a SQLite database as described in the `Database Structure <link?>`_ section. Interacting with the data through the `Structured Query Language (SQL) <http://en.wikipedia.org/wiki/SQL>`_ is a flexible approach to further analyzing the output. Here we provide a few detailed examples of the common ways in which the output of *<name>* can be queried for further processing. The ex

.. sourcecode:: sql
   
    select * from metadata where ProcessingStatus='normal'

.. sourcecode:: sql
   
    select BlockDepth from metadata where ProcessingStatus='normal' and ResTime > 0.2


.. sourcecode:: sql
   
    select BlockDepth from metadata where ProcessingStatus='normal' and ResTime > 0.2 and BlockDepth between 0.1 and 0.5


.. sourcecode:: sql
   
    select BlockDepth, ResTime, AbsEventStart from metadata where ProcessingStatus='normal' order by AbsEventStart ASC


.. sourcecode:: sql
   
    select AbsEventStart from metadata where ProcessingStatus='normal' order by AbsEventStart ASC limit 500