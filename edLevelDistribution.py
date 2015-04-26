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

def filteredulevel(edlevel):
    if edlevel == '':
        return 'NA'
    else:
        return edlevel

def builddistdict(fromlist, withfilter = None):
    """
    Build a dictionary that maps from values to the number of entities in a list with those values.

    This function will take a list of tuples and, looking at the first value in the tuple, will
    build a dictionary keyed by the value with value the number of entries in the list with that value.
    If supplied, the withfilter function, which takes a single value, can be used to replace the
    key value with something else.

    :param fromlist: a list of tuples, the first of which will be used for the distribution
    :param withfilter: An optional filter that will take an instance of the value for distribution
    and return a value to be used
    :return: a dictionary, keyed by the values for the distribution, with values the number of
    occurrences of that value in the list
    """
    retdict = {}
    for entry in fromlist:
        level = entry[0]
        if withfilter is not None:
            level = withfilter(level)
        if level in retdict:
            retdict[level] += 1
        else:
            retdict[level] = 1
    return retdict


if __name__ == '__main__':
    dbname = sys.argv[1]
    c = dbOpen(dbname)
    c.execute('Select LoE from source')
    studentlist = c.fetchall()
    leveldict = builddistdict(studentlist, filteredulevel)
    for description, code in transdict.items():
        print description, str(leveldict[code])