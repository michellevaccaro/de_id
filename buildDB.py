#!/usr/bin/env python

'''
Builds the basic database for de-identification. While building the database, this program
will replace the current student name and id with a randomly generated id (which is the same
for the student for all his or her records) and will also create the country/continent table.
The dates will also be altered to contain just the date (not the time), and a copy of the
table will be made as a separate table so that changes can be compared with the original.

The database will be saved, and can be copied and re-used for multiple runs of the rest of
the code.
'''
__author__ = 'waldo'

from de_id_functions import *
import sys

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: python buildDB csvFileName databaseName (verbose)'
        sys.exit(1)

    fromFileName = sys.argv[1]
    dbFileName = sys.argv[2]
    if len(sys.argv) > 3:
        verbose = True
    else:
        verbose = False

    c = dbOpen(dbFileName)
    sourceLoad(c, fromFileName, 'source')
    c.execute('CREATE TABLE original AS SELECT * from source')

    countryNamer(c, 'source', 'final_cc')
    contImport(c, 'source', 'country_continent', 'final_cc_cname')

    if verbose:
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print (c.fetchall())
        c.execute("SELECT SUM(Count) FROM source")
        print (c.fetchall())
