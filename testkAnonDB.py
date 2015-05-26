#!/usr/bin/env python
__author__ = 'waldo'

from de_id_functions import *
from buildDeIdentifiedCSV import build_numeric_dict, get_pickled_table, loe_dict
import sys, pickle

def make_key(key_list):
    ret_string = ''
    for ent in key_list:
        ret_string += ent
    return ret_string

def make_list_dict(cr, yob_gentable, forum_gentable, cgtable, suppress_table):
    #cr.execute('Select user_id, course_id, final_cc_cname, LoE, Yob, gender, nforum_posts from source')
    ret_dict = {}

    for ent in cr.execute('Select user_id, course_id, final_cc_cname, LoE, Yob, gender, nforum_posts from source'):
        course_user = ent[1] + ent [0]
        if course_user in suppress_table:
            continue

        ent_key = ent[1]
        if ent[2] in cgtable:
            ent_key += cgtable[ent[2]]
        else:
            ent_key += ent[2]
        if ent[3] in loe_dict:
            ent_key += loe_dict[ent[3]]
        else:
            ent_key += ent[3]
        if ent[4] in yob_gentable:
            ent_key += yob_gentable[ent[4]]
        else:
            ent_key += str(ent[4])
        ent_key += ent[5]
        ent_key += str(forum_gentable[ent[6]])

        if ent_key in ret_dict:
            ret_dict[ent_key].append(course_user)
        else:
            ret_dict[ent_key] = [course_user]
    return ret_dict

def make_count_dict(prop_dict):
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
    if len(sys.argv) < 5:
        print 'Useage: testkAnonDB.py databaseFile NewSuppress classSuppress geoSuppress k-anonValue'
        sys.quit(1)

    db_filename = sys.argv[1]
    suppress_out = sys.argv[2]
    cl_suppress = sys.argv[3]
    geo_suppress = sys.argv[4]
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
            full_suppress_list += prop_dict[id_pair]
            count += len(prop_dict[id_pair])
            suppress_total += len(prop_dict[id_pair])
        print 'Suppress records for value ', str(i), 'is', str(count)

    print 'Total suppressed records is ', suppress_total

    outf = open(suppress_out, 'w')
    pickle.dump(full_suppress_list, outf)
    outf.close()







