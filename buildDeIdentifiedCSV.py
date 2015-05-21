#!/usr/bin/env python

__author__ = 'waldo'

import pickle, sys, csv
from de_id_functions import *

"""
The set of fields that will be written to the output file. These need to be the names as
they appear in the database, and will also be the names used for the header of the csv
file. While I generally deplore the use of globals, in this case it makes sense.
"""
wfields = ['course_id',
           'user_id',
           'registered',
           'viewed',
           'explored',
           'certified',
           'final_cc_cname',
           'LoE',
           'YoB',
           'gender',
           'grade',
           'start_time',
           'last_event',
           'nevents',
           'ndays_act',
           'nplay_video',
           'nchapters',
           'nforum_posts',
           'roles'
           ]

def build_select_string(tablename):
    """
    Build a string to be used in an SQL select statement

    Builds the select statement to be used in a cursor.execute() to get all of the fields
    that will be written (perhaps after generalization) for the de-identified file
    :param tablename: Name of the table from which the fields are to be taken
    :return: a string suitable for using in an execute() statement
    """
    retstr = 'Select ' + wfields[0]
    for i in range(1,len(wfields) - 1):
        retstr = retstr + ', ' + wfields[i]
    retstr = retstr + ' from ' + tablename
    return retstr

def get_pickled_table(filename):
    """
    Reads in a dictionary that has been saved to the named file using pickle.dump()
    :param filename: The name of the file containing the pickled dictionary
    :return: The dictionary that was pickled in the file
    """
    with open(filename, 'rU') as pfile:
        supressdict = pickle.load(pfile)
        pfile.close()
        return supressdict

def build_numeric_dict(cr, table_name):
    """
    Build a generalization dictioclassSnary from a table.

    This assumes the table has keys that are numeric values and values that are ranges that the values
    map to for generalization.
    :param cr: A cursor for the database containing the table
    :param table_name: The name of the table to be used to build the dictionary
    :return: A dictionary with keys the numeric values and values numeric ranges that generalize those values
    """
    ret_dict = {}
    sel_string = "Select * from " + table_name
    cr.execute(sel_string)
    for pair in cr.fetchall():
        ret_dict[pair[0]] = pair[1]
    return ret_dict


def init_csv_file(fhandle):
    """
    Create a csv writer from an open file, and write the header from the global wfields
    :param fhandle: an file opened for writing
    :return: a csv.writer object
    """
    outf = csv.writer(fhandle)
    outf.writerow(wfields)
    return outf

if __name__ == '__main__':
    """
    The main routine, that will open the database, get the supression tables for classes,
    and the mapping dictionaries for the various generalizers, and then create a .csv
    file that is de-identified.

    Usage: buildDeIdentifiedCSV databaseIn CSVfileOut courseSupressionFile countryGeneralizationFile
    """

    if len(sys.argv) < 5:
        print 'Usage: buildDeIdentifiedCSV databaseIn CSVfileOut courseSupressionFile countryGeneralizationFile'
        sys.exit(1)

    c = dbOpen(sys.argv[1])
    outname = sys.argv[2]
    outf = open(outname, 'w')
    csvout = init_csv_file(outf)

    csuppress = get_pickled_table(sys.argv[3])
    cgtable = get_pickled_table(sys.argv[4])
    yob_dict = build_numeric_dict(c, 'YoB_bins')
    forum_dict = build_numeric_dict(c, 'nforum_posts_bins')

    c.execute(build_select_string('source'))
    rec_list = c.fetchall()
    supressed_records = 0
    encoding_errors = 0
    for rec in rec_list:
        if rec[0]+rec[1] in csuppress:
            supressed_records += 1
            continue
        l = list(rec)
        l[6] = cgtable[l[6]]
        if (l[8] != ''):
            l[8] = yob_dict[l[8]]
        if l[17] != '':
            l[17] = forum_dict[l[17]]
        try:
            csvout.writerow(l)
        except:
            encoding_errors += 1
            continue

    outf.close()


    print 'number of records suppressed for k-anonymity =', supressed_records
    print 'number of records supressed for encoding issues =', encoding_errors
