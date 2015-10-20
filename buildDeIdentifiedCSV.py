#!/usr/bin/env python

__author__ = 'waldo'

import pickle, sys, csv
from de_id_functions import *

"""
The set of fields that will be written to the output file. These need to be the names as
they appear in the database, and will also be the names used for the header of the csv
file. While I generally deplore the use of globals, in this case it makes sense.
"""

header_pr = ['Course ID',
             'User ID',
             'Explored',
             'Certified',
             'Location',
             'Level of Education',
             'Year of Birth',
             'Mean YoB',
             'Gender',
             'Grade',
             'Start time',
             'Last Interaction',
             'Number of Events',
             'Number of Forum Posts',
             'Mean Number of Forum Posts',
             'Total Time Spent',
             'Ever Taught',
             'Ever Taught This Course',
             'Reason for Taking Course'
             ]

loe_dict = { 'nan' : 'ug',
             'NA': 'ug',
             'm': 'pg',
             'p': 'pg',
             'b': 'pg',
             'a': 'ug',
             'hs': 'ug',
             'jhs': 'ug',
             'el': 'ug',
             'none':'ug',
             'other':'ug',
             '': 'ug',
             'p_se':'pg',
             'p_oth': 'pg'
             }

wfields = ['course_id',
           'user_id',
           'explored',
           'certified',
           'cc_by_ip',
           'LoE',
           'YoB',
           'gender',
           'grade',
           'start_time',
           'last_event',
           'nevents',
           'nforum_posts',
           'sum_dt',
           'prs_teach',
           'prs_teach_crs',
           'prs_reason_lc'
           ]

def build_select_string(tablename):
    """
    Build a string to be used in an SQL select statement

    Builds the select statement to be used in a cursor.execute() to get all of the fields
    that will be written (perhaps after generalization) for the de-identified file
    :param tablename: Name of the table from which the fields are to be taken
    :return: a string suitable for using in an execute() statement
    """
    fieldstr = ', '.join(wfields)
    retstr = "Select " + fieldstr + ' from ' + tablename
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
    Build a generalization dictionary from a table of keys, ranges, and means.

    This assumes the table has keys that are numeric values (in string form) and values that are ranges that the values
    map to for generalization, and the mean for that range.
    :param cr: A cursor for the database containing the table
    :param table_name: The name of the table to be used to build the dictionary
    :return: A dictionary with keys the numeric values, values numeric ranges  and means that generalize those values
    """
    ret_dict = {}
    sel_string = "Select * from " + table_name
    cr.execute(sel_string)
    for value, range, mean in cr.fetchall():
        ret_dict[value] = [range, mean]
    return ret_dict


def init_csv_file(fhandle):
    """
    Create a csv writer from an open file, and write the header from the global wfields
    :param fhandle: an file opened for writing
    :return: a csv.writer object
    """
    outf = csv.writer(fhandle)
    outf.writerow(header_pr)
    return outf


def main(db_file_name, outname, csuppress_file_name, cg_file_name):
    """
    The main routine that will create and write the final de-identified data set

    This method will open the database, the file containing the pickled version
    of the courses to suppress, and the country generalization file. It will then
    write a .csv file with the name supplied that contains all of the records
    that are not to be suppressed, with the generalized values that will give
    the de-identification.
    :param db_file_name: name of the file containing the database to be converted to csv
    :param outname:  name of the csv file to be produced
    :param csuppress_file_name: file containing a pickled version of the set of course/student
    records to be suppressed
    :param cg_file_name: file containing the pickled version of the dictionary mapping
    from country to region (if needed) for anonymization
    :return: None
    """
    c = dbOpen(db_file_name)
    outf = open(outname, 'w')
    csvout = init_csv_file(outf)
    csuppress = get_pickled_table(csuppress_file_name)
    cgtable = get_pickled_table(cg_file_name)
    yob_dict = build_numeric_dict(c, 'YoB_bins')
    forum_dict = build_numeric_dict(c, 'nforum_posts_bins')
    c.execute(build_select_string('source'))
    supressed_records = len(csuppress)
    encoding_errors = 0
    for rec in c.fetchall():
        if rec[0] + rec[1] not in csuppress:
            l = list(rec)
            l[4] = cgtable[l[4]]
            if l[5] in loe_dict:
                l[5] = loe_dict[l[5]]
            else:
                l[5] = 'ug'
            if (l[6] == '') or (l[6] == '9999.0'):
                l[6] = ''
                l.insert(7, '')
            else:
                year = l[6][:-2]
                yrange = yob_dict[year][0]
                ymean = yob_dict[year][1]
                l[6] = yrange
                try:
                    l.insert(7, str(round(float(ymean), 2)))
                except:
                    l.insert(7, 'NA')
            if (l[13] == '') or (l[13] == '9999.0'):
                l[13] = '0'
                l.insert(14,'0')
            else:
                nf = l[13][:-2]
                nf_range = forum_dict[nf][0]
                nf_mean = forum_dict[nf][1]
                l[13] = nf_range
                try:
                    l.insert(14, str(round(float(nf_mean), 2)))
                except:
                    l.insert(14, 'NA')
            try:
                csvout.writerow(l)
            except:
                encoding_errors += 1
                continue
    outf.close()
    print 'number of records suppressed for k-anonymity =', supressed_records
    print 'number of records supressed for encoding issues =', encoding_errors


if __name__ == '__main__':
    """
    The main routine, that will get the names of the files needed for the creation
    of the de-identified csv file, and pass those names on to the main() routine,
    which does all of the actual work.

    Usage: buildDeIdentifiedCSV databaseIn CSVfileOut recordSupressionFile countryGeneralizationFile
    """
    if len(sys.argv) < 5:
        print 'Usage: buildDeIdentifiedCSV databaseIn CSVfileOut recordSuppressFile countryGeneralizationFile'
        sys.exit(1)
    db_file_name = sys.argv[1]
    outname = sys.argv[2]
    csuppress_file_name = sys.argv[3]
    cg_file_name = sys.argv[4]

    main(db_file_name, outname, csuppress_file_name, cg_file_name)
