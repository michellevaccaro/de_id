__author__ = 'waldo'


from de_id_functions import *
import sys

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: python buildDB csvFileName databaseName'
        sys.exit(1)

    fromFileName = sys.argv[1]
    dbFileName = sys.argv[2]
    c = dbOpen(dbFileName)
    sourceLoad(c, fromFileName, 'source')
    c.execute('CREATE TABLE original AS SELECT * from source')
