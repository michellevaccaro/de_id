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
    ret_string = ''.join(key_list)
    return ret_string


def get_LOE(level):
    try:
        return loe_dict[level]
    except:
        print "LOE ", level, ' not in LOE_gentable'
        return ''


def get_YOB(for_year, yob_gentable):
    for_year = for_year[:-2]
    try:
        return yob_gentable[for_year][0]
    except:
        return for_year


def get_nforum(posts, post_table):
    k = posts[:-2]
    if k == '9999':
        return '0'
    try:
        return post_table[k][0]
    except:
        print 'Form posts number', posts, 'not in forum generalization table'
        return posts


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
    i = 0
    for ent in cr.execute('Select user_id, course_id, cc_by_ip, LoE, Yob, gender, nforum_posts from source'):
        course_user = ent[1] + ent[0]
        if course_user not in suppress_table:
            key_list = [ent[1], cgtable[ent[2]], get_LOE(ent[3]), get_YOB(ent[4], yob_gentable),
                        ent[5], get_nforum(ent[6], forum_gentable)]
            dict_key = ''.join(key_list)
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


def main(db_filename, cl_suppress, geo_suppress, suppress_out, k_val):
    cr = dbOpen(db_filename)
    yob_gentable = build_numeric_dict(cr, 'YoB_bins')
    forum_gentable = build_numeric_dict(cr, 'nforum_posts_bins')
    cgtable = get_pickled_table(geo_suppress)
    class_suppress = get_pickled_table(cl_suppress)
    prop_dict = make_list_dict(cr, yob_gentable, forum_gentable, cgtable, class_suppress)
    full_suppress_list = list(class_suppress)
    suppress_total = len(class_suppress)
    print 'Number of suppressed records due to class identification is', suppress_total
    for k, v in prop_dict.iteritems():
        if len(v) < k_val:
            full_suppress_list.extend(v)
    print 'Total number of records suppressed =', str(len(full_suppress_list))
    outf = open(suppress_out, 'w')
    full_suppress_set = set(full_suppress_list)
    pickle.dump(full_suppress_set, outf)
    outf.close()


if __name__ == '__main__':
    """
    Build a full suppression table for a particular level of k-anonymity

    This program will take a db file that has already had the numeric binning constructed (using numeric_generalizaiton.py)
    along with a class suppression file and a particular value of k, and will determine the records that need to be
    suppressed to reach that level of k with the generalization that has already occurred. The full suppression list,
    including the records that need to be suppressed because of combinations of classes (i.e., the class suppression list)
    will be pickled into a file supplied as one of the command line arguments.

    Note that this program assumes that the only quasi-identifiers in the set are the Year of Birth, number of forum posts,
    level of education, location, gender, and classes taken. For both the year1 and year2 sets, this is the case, but
    if other quasi-identifiers are added to the output set, this program will need to be modified to take into account
    those identifiers.
    """
    if len(sys.argv) < 5:
        print 'Useage: buildFullSuppressionSet.py databaseFile classSuppress geoSuppress NewSuppress k-anonValue'
        sys.quit(1)

    db_filename = sys.argv[1]
    cl_suppress = sys.argv[2]
    geo_suppress = sys.argv[3]
    suppress_out = sys.argv[4]
    k_val = int(sys.argv[5])

    main(db_filename, cl_suppress, geo_suppress, suppress_out, k_val)
