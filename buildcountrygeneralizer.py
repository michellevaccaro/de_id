#!/usr/bin/env python
"""
Build a generalization table for country

Takes all of the countries listed in the database to be de-identified, and finds those that
do not have a minimum size. Using a mapping from country to region, builds a table keyed by
country that will have a region with at least the number of records needed to insure
k-anonymity (which is a hard-coded value at the moment, = 50).

Writes out a file with the name supplied as a command line parameter that is the pickle of
the generalization table.

Usage: buildcountrygeneralizer.py databaseFile generalizationFile {'p'}
where
    databaseFile : name of the file containing the database
    generalizationFile : name of the generalization table file to be written
    optional 'p' : useful to see what is happening; will print the generalization file,
    the mapping of countries to counts, and the mapping of regions to counts, on standard
    out.
"""

__author__ = 'waldo'

import sys, pickle, os
from de_id_functions import *
from edLevelDistribution import builddistdict
import utils


def readcountrycont(ccfile = ''):
    """
    Reads in the pickle file containing country->region tables, and returns the dictionary with
    that mapping.

    Reads in the file whose name is passed in; if no name is passed or if the file name passed
    in does not exist, this will interactively query the user for the file. This assumes that
    the file passed in is a pickled version of a dictionary from country to region, and simply
    reconstructs the dictionary and returns that dictionary.
    :param ccfile: the name of the file containing the pickle for the dictionary
    :return: a dictionary mapping from country names to more general regions
    """
    if (ccfile == '') or not(os.path.exists(ccfile)):
        ccfile = utils.getFileName('the country/continent file')
    pf = open(ccfile, 'rU')
    ccdict = pickle.load(pf)
    pf.close()
    return ccdict

def buildcont2country(ccdict):
    """
    Build a dictionary from regions to a list of countries in that region.

    This dictionary gets used if, after combining all of the countries that don't have
    a minimal number of records in that country, the region still does not have the minimal
    count. The rest of the countries are then used to increase the region count.

    :param ccdict: The dictionary from country to region
    :return: A dictionary from region to list of countries in that region
    """
    retdict = {}
    for country, cont in ccdict.items():
        if cont in retdict:
            if country not in retdict[cont]:
                retdict[cont].append(country)
        else:
            retdict[cont] = [country]
    return retdict

def addtogencount(gensize, cont, count):
    """
    Utility routine to insert or add a country's count of records to a region.

    Checks to see if the region is already in the region->size dictionary, and if not
    adds the region with an initial size. If the region is already in the dictionary,
    this will simply add the count to the region.
    :param gensize:  The dictionary from region to number of records in the region
    :param cont:  The region whose record is to be incremented
    :param count: The count to increment the record
    :return: None
    """
    if cont not in gensize:
        gensize[cont] = count
    else:
        gensize[cont] += count

def buildgentable(countrydist, country2cont, cont2country, minsize):
    """
    Build the dictionary that maps from countries to a geographic area with at least minsize records

    This routine builds a dictionary keyed by country, with value either the country (if there
    are sufficient records, determined by minsize) the country itself, or a region that will contain
    at least minsize records.

    :param countrydist: A dictionary keyed by country with value the number of records for that country
    :param country2cont: A dictionary keyed by country with value the region that country is in
    :param cont2country: A dictionary keyed by region with value a list of the countries in that region
    :param minsize: The minimal size needed for a country or region
    :return: a pair of dictionaries, one of which is keyed by country and has value the geographic area
    that has at least minsize entries, and a dictionary keyed by region with value the number of
    entries that will show that region as their geographic place.
    """
    retdict = {}
    gensize = {}
    for country, count in countrydist.iteritems():
        if count < minsize:
            retdict[country] = country2cont[country]
            addtogencount(gensize, country2cont[country], count)
        else:
            retdict[country] = country

    for region, size in gensize.iteritems():
        if size < minsize:
            mcountry = ''
            msize = 10000
            for country in cont2country[region]:
                if (country in retdict) \
                        and (retdict[country] == country) \
                        and countrydist[country] < msize:
                    mcountry = country
                    msize = countrydist[country]
            retdict[mcountry] = region
            gensize[region] += msize

    return retdict, gensize

def printtables(countrydist, gentable, gensizetable):
    """
    For debugging, print out the various country->continent tables and counts

    This should only be called when the user adds a third command line argument of 'p',
    for printing the tables.

    :param countrydist: dictionary of countryname -> number of records with that name
    :param gentable: dictionary of countryname -> generalized (if needed) name
    :param gensizetable:  dictionary of generalized name -> count for that name
    :return: None
    """
    for cont, count in gensizetable.iteritems():
        print cont, count

    for country, count in countrydist.iteritems():
        print country, count

    for country, value in gentable.iteritems():
        print country, value

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print 'Usage: buildcountrygeneralizer databaseFile outputFile country_to_continent_file {p}'
        exit(1)

    dbname = sys.argv[1]
    outname = sys.argv[2]
    ccfname = sys.argv[3]

    c = dbOpen(dbname)
    c.execute('Select final_cc_cname from source')
    countries = c.fetchall()

    countrydist = builddistdict(countries)
    country2cont = readcountrycont('../country_continent')
    cont2country = buildcont2country(country2cont)

    gentable, gensizetable = buildgentable(countrydist, country2cont, cont2country, geo_binsize)

    outf = open(outname, 'w')
    pickle.dump(gentable, outf)
    outf.close()

    if (len(sys.argv) > 4) and (sys.argv[4] == 'p'):
        printtables(countrydist, gentable, gensizetable)

