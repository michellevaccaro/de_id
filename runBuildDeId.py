#!/usr/bin/env python
'''
Run the program to build the de-identified data set over a particular directory that contains yob and forum
bin files of the right sizes for the specified k-anonymity values.
'''
import buildDeIdentifiedCSV as csvBuilder
from de_id_functions import dbOpen

bin_size = ['05', '10', '15', '20', '25']
k_vals = [3,4,5,6]

cr = dbOpen('year.db')
cr.execute(csvBuilder.build_select_string('source'))
user_course_list = cr.fetchall()

country_base = 'countryGen'

for k in k_vals:
    for s in bin_size:
        class_supp = 'classSuppressSet' + str(k) + 'P'
        country_file = country_base + s + 'k'
        yob_fname = 'yobbin'+ s + 'k'
        fbin_fname = 'postbin' + s + 'k'
        full_suppress = 'fullSuppress' + s + s + str(k) + 'P'
        de_id_fname = 'deIdFile' + s + s + str(k) + 'P.csv'
        csvBuilder.main(user_course_list, de_id_fname, full_suppress,
                                          country_file, yob_fname, fbin_fname)
