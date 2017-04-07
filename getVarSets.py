#!/usr/bin/env python

'''
Given some csv, for each variable returns a set of the values the variable can assume.

'''
__author__ = 'vaccaro'

import csv
import sys

quasi_identifiers = ["ip", "cc_by_ip", "countryLabel", "continent", "city", "region", "subdivision", "postalCode",
                     "un_major_region", "latitude", "longitude", "LoE", "YoB", "gender", "nforum_posts",
                     "nforum_votes", "nforum_endorsed", "nforum_threads", "nforum_comments", "nforum_pinned",
                     "nforum_events", "profile_country", "email_domain"]

def load_csv(fname):
    with open(fname, "rb") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        # keys are the quasi identifiers
        keys = []
        for h in headers:
            if(h in quasi_identifiers):
                keys.append(h)

        # make dictionary of all unique values of quasi identifiers
        hDict = {}
        for k in keys:
            hDict[k] = set()

        # read in values from file
        for row in reader:
            for key in hDict:
                hDict[key].add(row[key])

        # write sets to csv
        for key in hDict:
            fname = key + ".csv"
            with open(fname, 'wb') as f:
                w = csv.writer(f)
                w.writerow([key])
                for x in hDict[key]:
                    w.writerow([x])

        # print hDict
        for key in hDict:
            print(key + str(hDict[key]))

load_csv("full2017-02-08.csv")