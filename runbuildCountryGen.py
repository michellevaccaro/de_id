#!/usr/bin/env python

import buildcountrygeneralizer as bcg
from de_id_functions import dbOpen

bin_info = [('05k', 5000), ('10k', 10000), ('15k', 15000), ('20k', 20000), ('25k', 25000)]

cr = dbOpen('year.db')
cr.execute('Select cc_by_ip from source')
cc_list = cr.fetchall()

for bi in bin_info:
    outfile = 'countryGen'+bi[0]
    cc_to_regFile = '../../country_continent'
    bin_size = bi[1]
    bcg.main(cc_list, outfile, cc_to_regFile, bin_size)
