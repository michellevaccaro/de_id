#!/usr/bin/env python
"""
Given some set of databases, count the number of distinct values in a particular field. Right now, it is
assumed that the table is named "source"
"""

from de_id_functions import dbOpen
import sys

def count_fields(c, fname, tbl_name):
    db_command = "Select " + fname + " from " + tbl_name " group by " + fname
    c.execute(db_command)
    return len(c.fetchall())

if __name__ == '__main__':
    for i in range(1, len(sys.argv)):
        print sys.argv[i]
        c = dbOpen(sys.argv[i])
        print 'Number of unique user ids = ', str(count_fields(c, 'user_id', 'source'))
        print 'Number of unique user, class combinations = ', str(count_fields(c, 'user_id, course_id', 'source'))
        print ''
