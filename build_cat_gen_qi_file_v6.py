#! /usr/bin/env python

import cPickle, sys, csv


def get_gen_map(fname):
    fin = open(fname, 'rw')
    gen_map = cPickle.load(fin)
    fin.close()
    return gen_map


def get_gen_val(f_map, in_val):
    if(in_val in f_map):
        val = f_map[in_val][0]
        return val


def get_gen_loc(f_map, in_val):
    if (in_val in f_map):
        val = f_map[in_val]
        return val


def get_gen_course(f_map, in_val, bin_size):
    return f_map[in_val][2]


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: python build_cat_gen_qi_file.py qi_pickle_file_in qi_gen_file_out bin_size'
        sys.exit(1)

    fin_name = sys.argv[1]
    fin = open(fin_name, 'rU')
    qi_in_l = csv.reader(fin)

    fout_name = sys.argv[2]

    bin_size = int(sys.argv[3])

    loe_map = get_gen_map('LOE_map_generalization5.pkl')
    gender_map = get_gen_map('Gender_generalization_map.pkl')
    course_map = get_gen_map('course_id_categories.pkl')
    loc_map = get_gen_map('postal+city+region_subdivision.pkl')

    fout = open(fout_name, 'w')
    qi_gen_out = csv.writer(fout)

    header = qi_in_l.next()
    header[2] = 'Location'  # Rename region header
    del header[4]   # Delete city header
    del header[3]   # Delete region header
    qi_gen_out.writerow(header)

    for l in qi_in_l:
        loc_key = l[3] + "-" + l[4] + "-" + l[2]

        l[1] = get_gen_course(course_map, l[1], bin_size)     # Generalize course
        l[5] = get_gen_val(loe_map, l[5])    # Generalize education
        l[7] = get_gen_val(gender_map, l[7])       # Generalize gender
        l[2] = get_gen_loc(loc_map, loc_key)    # Generalize location

        del l[4]    # Delete city
        del l[3]    # Delete region

        qi_gen_out.writerow(l)

    fout.close()
    fin.close()