#!/usr/bin/env python

"""
Find the distribution of equivalence class sizes for a dataset with a particular set of quasi-identifiers

This program will take a set of fields in each line (hard coded, at the moment) and will build a dictionary
that has as key the concatenation of those fields, with values the count of the number of records that
are in the equivalence class defined by those fields.

The program then runs over this dictionary and creates another, keyed by the number of entries in an
equivalence class, with values the number of different equivalence classes that have this number of
entries. This dictionary will then be printed out, with the keys sorted from lowest to highest.

The first part of the code is taken from testKAnon.py, written for the HarvardX research group, that
builds the first of these dictionaries and then makes sure that there are no sets of quasi-identifiers
that have fewer than a user-supplied set of entries in them.

@author: waldo
"""
import operator
import csv
import utils
def buildKey(ids, dataLine):
    """
    Concatenate a set of fields together to build an overall key

    This is a simple approach to determining k-anonymity, in which all
    of the fields of interest are concatenated as a single key. The
    ids coming in should be a list of indexes into the fields in the dataLine.
    These will be concatenated in order to form a new key. Note that this
    currently assumes that all of the data fields are strings.

    """
    retKey = ''
    for i in ids:
        retKey += dataLine[i]

    return retKey

def makeDict(ids, infile):
    """
    Create and return a dictionary keyed by a concatenation of fields with value the number
    of entries containing all and only those fields.

    Taking a list of indexes into a line of a (csv) file and an open csv.reader(), build a
    dictionary that is keyed by the string concatenation of the fields in the index with
    value the number of times a line containing just those fields in those indexes occurs. Return
    the dictionary to the caller.

    """
    retDict = {}
    for line in infile:
        if line[12] == 'NA':
            line[12] = ''

        keyAnon = buildKey(ids, line)
        if keyAnon in retDict:
            retDict[keyAnon] += 1
        else:
            retDict[keyAnon] = 1

    return retDict

def makeEquivDict(qidict):
    retDict = {}
    for k, v in qidict.iteritems():
        if v in retDict:
            retDict[v] += 1
        else:
            retDict[v] = 1
    return retDict


if __name__ == '__main__':
    """
    When run stand-alone, this script will query for a filename and a level of anonymity
    to check for the externally-connected data fields in the .csv file. The user will also
    be prompted for either a summary of the anonymity level (in which case only the number
    of records that fail to be at least anonymous to the level indicated) will be printed, or
    a full report, in which case the concatenation of fields that allow identification finer
    than the level entered will be printed. Note that the indexes of the fields that can be
    linked to external properties is hard-coded at the moment; it would be good to have a more
    flexible mechanism for this but finding one that is not error prone is difficult.

    """
    idFields = [0, 10, 11, 12, 19]
    fname = utils.getFileName('data file to test')
    fin = open(fname, 'rU')
    fread = csv.reader(fin)

    l = fread.next()
    for i in idFields:
        print l[i]
    anonDict = makeDict(idFields, fread)
    qiequivDict = makeEquivDict(anonDict)

    sortedDict = sorted(qiequivDict.iterkeys())
    for k in sortedDict:
        print str(k), qiequivDict[k]


