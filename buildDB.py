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

def splitDate(date):
    '''
    Remove the date from the time in the time signature while creating the main table. This replaces the call to
    splitDate(), which took a long time.
    '''
    if 'T' in date:
        point = date.index('T')
        date = date[:point]
    return date

def idGen2(varName, prefix, lDict):
    if varName in lDict:
        return(lDict[varName])
    nId = prefix + str(random.randint(0,10000000000))
    while nId in lDict:
        nId = prefix + str(random.randint(0,10000000000))
    lDict[varName] = nId
    lDict[nId] = varName
    return nId

def sourceLoad(cursor, fname, tableName):
    """
    cursor: sqlite3 cursor object
    fname: string, file name/path for loading, .csv format
    takes a .csv file and reads it into a sqlite database defined by the
    cursor object.
    CAUTION: will DELETE any existing table with same name
    """
    try:
        cursor.execute("DROP TABLE "+tableName)
    except:
        pass

    with open(fname, "rU") as inFile:
        csvIn = csv.reader(inFile)
        row = csvIn.next()
        headers = row
        tableCreate = "CREATE TABLE "+tableName+" ("
        tableInsert = "INSERT INTO "+tableName+" VALUES ("
        for col in headers[:-1]:
            if '.' in col:
                col = string.replace(col, '.', '_')
            tableCreate += col+" text, "
            tableInsert += "?,"
        tableCreate += headers[-1] + " text )"
        tableInsert += "?)"
        print len(headers)
        cursor.execute(tableCreate)

        idDict = {}
        for row in csvIn:
            if (row[29] == 'instructor') or (row[29] == 'staff' ):
                continue
            row[17] = splitDate(row[17])
            row[18] = splitDate(row[18])
            row[1] = idGen2(row[1], 'MHxPC14', idDict)
            if not (not (row[14] == 'NA') and not (row[14] < '1930') and not (row[14] > '2005')):
                row[14] = ''
            if row[15] == 'NA':
                row[15] = ''
            #row += ''
            trow = tuple(row)
            print trow, len(trow)
            #trow += (",")
            print tableInsert
            cursor.execute(tableInsert, trow)

    #cursor.execute("ALTER TABLE "+tableName+" ADD COLUMN Count integer")
    #cursor.execute("UPDATE "+tableName+" SET Count =1")

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
    countryNamer(c, 'source', 'final_cc')
    contImport(c, 'source', 'country_continent', 'final_cc_cname')

    if verbose:
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print (c.fetchall())
        c.execute("SELECT SUM(Count) FROM source")
        print (c.fetchall())