#!/usr/bin/env python

'''
Given some csv, for each variable returns a set of the values the variable can assume and the number of times this value
is assumed.

'''
__author__ = 'vaccaro'

import csv
import sys

#variables = ["countryLabel", "continent", "region", "subdivision", "un_major_region", "LoE",
#             "YoB", "gender", "nforum_posts", "nforum_votes", "nforum_endorsed", "nforum_threads", "nforum_comments",
#             "nforum_pinned", "nforum_events", "profile_country"]

variable = "cc_by_ip"

def load_csv(fname):
    with open(fname, "rb") as f:
        reader = csv.DictReader(f)

        # initialize dictionary
        dict = {}

        # read in values from file
        for row in reader:
            k = row[variable]
            if k not in dict:
                dict[k] = 1
            else:
                dict[k] += 1

        with open(variable + "_counts.csv", 'wb') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in dict.items():
                writer.writerow([key, value])

load_csv("full2017-02-08.csv")

