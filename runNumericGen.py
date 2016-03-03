#!/usr/bin/env python
'''
Run buildcountrygeneralizer.py to generate a group of generalization files for Year of Birth and Number of Forum posts.
The base names of the files that will be produced are yobbin and postbin, to which will be appended the string that is
the first member of the pairs in bin_info, and with bin sizes that are the second of the pair in the list of bin_info.
Current values are 0 (no binning), 5k, 10k, 15, 20k, and 25k.
'''

import numeric_generalization as ng
from de_id_functions import dbOpen

bin_size = [('00k', 0),
            ('05k', 5000),
            ('10k', 10000),
            ('15k', 15000),
            ('20k', 20000),
            ('25k', 25000)
            ]

bin_size = [('00', 0)]
yobfnamebase = 'yobbin'
postfnamebase = 'postbin'
cr = dbOpen('year.db')

for b in bin_size:
    yobfname = open(yobfnamebase + b[0], 'w')
    postfname = open(postfnamebase + b[0], 'w')
    ng.YoB_binsize = b[1]
    ng.nforum_post_binsize = [1]
    ng.main(cr, yobfname, postfname)
    yobfname.close()
    postfname.close()



