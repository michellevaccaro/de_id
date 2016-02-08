#!/usr/bin/env python
'''
Run the courseSetDeIdentify.py for a set of k-values and both participation and random suppression
mechanisms.
'''
import courseSetDeIdentify as csD
from de_id_functions import dbOpen, dbClose

k_values = [3, 4, 5, 6]
suppress_types = ['P', 'R']

c = dbOpen('year.db')
try:
    c.execute("Create Index user_id_idx on source ('user_id')")
except:
    pass

c.execute("Select user_id, course_id from source Order By user_id")
user_class_list = c.fetchall()
outbase = 'classSuppressSet'

for k_val in k_values:
    for s in suppress_types:
        outname = outbase + str(k_val) + s
        csD.main(user_class_list, c, k_val, s, outname)

dbClose(c)