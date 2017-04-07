__author__ = 'vaccaro'

import csv
import sys

def load_csv(fname):
    with open(fname, "rb") as f:
        reader = csv.DictReader(f)

        # initialize dictionaries
        dict = {}

        # read in values from file
        for row in reader:
            zip = row["postalCode"]
            city = row["city"]
            region = row["region"]
            key = zip + "-" + city + "-" + region
            if (not zip == "") and (not city == "") and (not region == ""):
                if key not in dict:
                    dict[key] = set()

                dict[key].add(row["continent"])

        with open('postal+city+region_continent.csv', 'wb') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in dict.items():
                writer.writerow([key, value])

load_csv("full2017-02-08.csv")