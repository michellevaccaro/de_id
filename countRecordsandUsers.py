#!/usr/bin/env python

from de_id_functions import dbOpen
import sys

if __name__ == '__main__':
    dbname = sys.argv[1]
    c = dbOpen(dbname)
    c.execute('Select course_id, user_id from source')
    all_rec = c.fetchall()
    users = set()
    for l in all_rec:
        users.add(l[1])

    print 'Total number of records = ', len(all_rec)
    print 'Total number of users = ', len(users)