#!/usr/bin/env python
"""
Takes a database output by buildDB.py and prints the distribution of levels of
education in that database.

The name of the file containing the database should be given as the first argument.
The level of education categories of not specified ('') and 'NA' are merged into a single
category. This could be done with the categories 'none' and 'other', but was not. This
could easily change in the future.

The output prints more meaningful names than the abbreviations used in the database.
"""
__author__ = 'waldo'
import sys
from de_id_functions import *


transdict = {
    'Doctorate': 'p',
    'Masters or Professional': 'm',
    'Bachelors': 'b',
    'Associates degree': 'a',
    'Secondary/High School': 'hs',
    'Junior Secondary/Junior High/middle school': 'jhs',
    'Elementary/Primary school': 'el',
    'None': 'none',
    'Other': 'other',
    'Not specified': 'NA',
    'Doctorate in Science/Engineering (deprecated)': 'p_se',
    'Doctorate in another field (deprecated)': 'p_oth'
}


def buildleveldict(studentlist):
    """
    Build a dictionary mapping level of education to the number of registrants at that level

    This is straightforward; the only (slight) trick is that the education levels 'NA' and ''
    (that is, left blank) are merged into a single category of 'not specified'.
    :param studentlist: a list of student_id, level of education
    :return: a dictionary keyed by level of education with content the number of participants who
    reported having that level
    """
    retdict = {}
    for student in studentlist:
        level = student[1]
        if level == '':
            level = 'NA'
        if level in retdict:
            retdict[level] += 1
        else:
            retdict[level] = 1
    return retdict


if __name__ == '__main__':
    dbname = sys.argv[1]
    c = dbOpen(dbname)
    c.execute('Select user_id, LoE from source')
    studentlist = c.fetchall()
    leveldict = buildleveldict(studentlist)
    for description, code in transdict.items():
        print description, str(leveldict[code])