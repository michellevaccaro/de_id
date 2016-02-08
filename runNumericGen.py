#!/usr/bin/env python
'''
This runs the program to build the numeric generalization for YoB and forum posts
'''

import numeric_generalization as ng
from de_id_functions import dbOpen

bin_size = [('05', 5000), ('10', 10000), ('15', 15000),
            ('20', 20000), ('25', 25000)]

yobfnamebase = 'yobbin'
postfnamebase = 'postbin'
cr = dbOpen('year.db')

for b in bin_size:
    yobfname = open(yobfnamebase + b[0]+'k', 'w')
    postfname = open(postfnamebase + b[0]+'k', 'w')
    ng.YoB_binsize = b[1]
    ng.nforum_post_binsize = [1]
    ng.main(cr, yobfname, postfname)
    yobfname.close()
    postfname.close()



