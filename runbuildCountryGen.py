#!/usr/bin/env python
'''
Run buildcountrygeneralizer.py to generate a group of generalization files for countries.
The base name of the files that will be produced is countryGen, to which will be appended the string that is
the first member of the pairs in bin_info, and with bin sizes that are the second of the pair in the list of bin_info.
Current values are 0 (no binning), 5k, 10k, 15, 20k, and 25k. The script assumes that a pickled dictionary mapping
countries to larger regions exists two directories above the script and is named 'country_continent'
'''

import buildcountrygeneralizer as bcg
from de_id_functions import dbOpen

bin_info = [('01k', 1000),
            ('02k', 2000),
            ('03k', 3000),
            ('04k', 4000)
            ]

cr = dbOpen('year.db')
cr.execute('Select cc_by_ip from source')
cc_list = cr.fetchall()

for bi in bin_info:
    outfile = 'countryGen'+bi[0]
    cc_to_regFile = '../../country_continent'
    bin_size = bi[1]
    bcg.main(cc_list, outfile, cc_to_regFile, bin_size)
