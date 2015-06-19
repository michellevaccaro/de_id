#!/usr/bin/env python
"""
Build a .csv file that tracks the percentage of students who only registered; viewed and registered; explored, viewed,
and registered; or were certified in a course, in the de-identified data set for the course, and in the records
suppressed to create the de-identified set.
"""
__author__ = 'waldo'

import pickle, sys, csv
from de_id_functions import *
from buildDeIdentifiedCSV import get_pickled_table


class Participation:
    """
    Record layout for the values of the dictionary that will be created for each class
    """
    registered = 0
    viewed = 0
    explored = 0
    certified = 0


def get_percent(i, k):
    """
    Given a number and a total, return the percentage of the total for the number
    :param i: the number to determine the percentage of total
    :param k: the total from which the number i is to be taken as a percentage
    :return: the percentage of k that is i
    """
    return (float(i) / k) * 100


def add_participation(c_dict, k, part_rec):
    """
    Add a participation record to the supplied dictionary

    Only the greatest value of the participation values will be recorded. If no record for the class is in the
    supplied dictionary, a record will be created. The value of the highest value of participation will be incremented;
    the ordering is that certified > explored > viewed > registered.
    :param c_dict: dictionary in which the record will or does appear
    :param k: the key to the dictionary; this will be the course id
    :param part_rec: the record for the participant of the course
    :return: None
    """
    if k not in c_dict:
        c_dict[k] = Participation()
    if part_rec[5] == '1':
        c_dict[k].certified += 1
    elif part_rec[4] == '1':
        c_dict[k].explored += 1
    elif part_rec[3] == '1':
        c_dict[k].viewed += 1
    else:
        c_dict[k].registered += 1


def write_dictionary(csvout, target_dict):
    """
    Write the entries in the target dictionary to a csv file

    The target dictionary will be written in the form key, percent registered, percent viewed, percent explored,
    percent certified. The parameter csvout must be a csv writer.
    :param csvout: A csv writer object
    :param target_dict: A dictionary keyed by course_id with values Participation objects
    :return: None
    """
    for k in target_dict.iterkeys():
        po = target_dict[k]
        total = po.registered + po.viewed + po.explored + po.certified
        if total != 0:
            rper = get_percent(po.registered, total)
            vper = get_percent(po.viewed, total)
            xper = get_percent(po.explored, total)
            cper = get_percent(po.certified, total)
            csvout.writerow([k, rper, vper, xper, cper])


def main(dbfname, suppress_fname, outfname):
    """
    Driver for the program; creates a triple of dictionaries for percentage participation by class and writes them
    to a single csv file

    The dictionaries created are for participation in the course in the full data set, in the de-identified data set,
    and in the records that are suppressed by the de-identification. These are written to the same csv file
    :param dbfname: The sqlite database containing the original data set
    :param suppress_fname: The file containing the set of suppressed records for de-identification
    :param outfname: The name of the file to create for the output. Note that if the file already exists, it will be
    overwritten
    :return: None
    """
    cr = dbOpen(dbfname)
    suppress_set = get_pickled_table(suppress_fname)

    select_str = 'Select course_id, user_id, registered, viewed, explored, certified from source'
    cr.execute(select_str)

    orig_dict = {}
    suppress_dict = {}
    anon_dict = {}
    for i in cr.fetchall():
        key = i[0] + i[1]
        ckey = i[0]
        add_participation(orig_dict, ckey, i)
        if key in suppress_set:
            add_participation(suppress_dict, ckey, i)
        else:
            add_participation(anon_dict, ckey, i)

    outf = open(outfname, 'w')
    csout = csv.writer(outf)
    csout.writerow(['Course ID', '% registered', '% viewed', '% explored', '% certified'])
    csout.writerow(['Suppressed records'])
    write_dictionary(csout, suppress_dict)
    csout.writerow(['Non-suppressed records'])
    write_dictionary(csout, anon_dict)
    csout.writerow(['Original records'])
    write_dictionary(csout, orig_dict)

    cr.close()
    outf.close()


if __name__ == '__main__':
    """
    Driver for the program when it is run stand-alone. Gets the arguments for main() from the command line and then
    calls main() with those arguments.
    """
    dbfname = sys.argv[1]
    suppress_fname = sys.argv[2]
    outf = sys.argv[3]

    main(dbfname, suppress_fname, outf)
