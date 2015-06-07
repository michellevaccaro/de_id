#!/usr/bin/env python
__author__ = 'waldo'

from de_id_functions import *
from buildDeIdentifiedCSV import build_numeric_dict, get_pickled_table, loe_dict
import sys, pickle

def make_key(key_list):
    """
    Build a key by concatenating the items in a list into a single string

    :param key_list: a list of items that will form the key
    :return: A single string that is the concatenation of the items in the list
    """
    ret_string = ''
    for ent in key_list:
        ret_string += ent
    return ret_string

def make_list_dict(cr, yob_gentable, forum_gentable, cgtable, suppress_table):
    """
    Build a dictionary keyed by a concatenation of generalized quasi-identiiers with value a list of the course_id,
    user_id pairs that are identified by that combination of quasi-identifiers.

    Using the db file, the numeric generalizations that are in the db, the class suppression table, the geographic
    generalization table, and the level of education generalization table (hard coded at the moment), build the
    dictionary.
    :param cr: cursor to the database
    :param yob_gentable: Year of birth generalization table
    :param forum_gentable: number of forum posts generalization table
    :param cgtable: geographic generalization table
    :param suppress_table: Table of items that need to be suppressed because they are uniquely identified by the
    combination of courses. These will not be added to the dictionary produced by this function
    :return: A dictionary keyed by concatenation of quasi-identifiers with value a list of course_id, user_id that
    have that combination of quasi-identifiers.
    """
    ret_dict = {}

    for ent in cr.execute('Select user_id, course_id, final_cc_cname, LoE, Yob, gender, nforum_posts from source'):
        course_user = ent[1] + ent [0]
        if course_user not in suppress_table:
            entl = list(ent[1:])
            entl[1] = cgtable[entl[1]]
            if entl[2] in loe_dict:
                entl[2] = loe_dict[entl[2]]
            if entl[3] in yob_gentable:
                entl[3] = yob_gentable[entl[3]]
            entl[5] = forum_gentable[entl[5]]
            dict_key = make_key(entl)
            if dict_key in ret_dict:
                ret_dict[dict_key].append(course_user)
            else:
                ret_dict[dict_key] = [course_user]
    return ret_dict

def make_count_dict(prop_dict):
    """
    Build a dictionary, indexed by count, of the number of entries with a set of quasi-identifiers

    Using a dictionary that is keyed by the concatenation (in canonical order) of quasi-identifiers with values the
    set of course_id,user_id that have those quasi-identifiers, build a dictionary keyed by the number of entries
    with that set of quasi-identifiers with value the concatenation of quasi-identifiers (i.e., the keys of the
    dictionary handed in)

    :param A dictionary indexed by a concatenation of quasi-identifiers with values a list of course_id+user_id with those
    quasi-identifiers:
    :return: A dictionary keyed by count with values a list of concatenated quasi-identifiers that have that number of
    entries
    """
    ret_dict = {}
    for k in prop_dict.iterkeys():
        id_list = prop_dict[k]
        l = len(id_list)
        if l not in ret_dict:
            ret_dict[l] = [k]
        else:
            ret_dict[l].append(k)
    return ret_dict

if __name__ == '__main__':
    """
    Build a full suppression table for a particular level of k-anonymity

    This program will take a db file that has already had the numeric binning constructed (using numeric_generalizaiton.py)
    along with a class suppression file and a particular value of k, and will determine the records that need to be
    suppressed to reach that level of k with the generalization that has already occurred. The full suppression list,
    including the records that need to be suppressed because of combinations of classes (i.e., the class suppression list)
    will be pickled into a file supplied as one of the command line arguments.
    """
    if len(sys.argv) < 5:
        print 'Useage: buildFullSuppressionSet.py databaseFile classSuppress geoSuppress NewSuppress k-anonValue'
        sys.quit(1)

    db_filename = sys.argv[1]
    cl_suppress = sys.argv[2]
    geo_suppress = sys.argv[3]
    suppress_out = sys.argv[4]
    k_val = int(sys.argv[5])

    cr = dbOpen(db_filename)
    yob_gentable = build_numeric_dict(cr, 'YoB_bins')
    forum_gentable = build_numeric_dict(cr, 'nforum_posts_bins')
    cgtable = get_pickled_table(geo_suppress)
    class_suppress = get_pickled_table(cl_suppress)

    prop_dict = make_list_dict(cr, yob_gentable, forum_gentable, cgtable, class_suppress)

    count_dict = make_count_dict(prop_dict)

    full_suppress_list = class_suppress
    suppress_total = len(class_suppress)
    print 'Number of suppressed records due to class identification is', suppress_total

    for i in range(1,k_val):
        count = 0
        if i not in count_dict:
            print 'No properties with only ', str(i), 'records'
            continue
        for id_pair in count_dict[i]:
            for e in prop_dict[id_pair]:
                full_suppress_list.add(e)
            count += len(prop_dict[id_pair])
            suppress_total += len(prop_dict[id_pair])
        print 'Suppress records for value ', str(i), 'is', str(count)

    print 'Total suppressed records is ', suppress_total

    outf = open(suppress_out, 'w')
    pickle.dump(full_suppress_list, outf)
    outf.close()







