'''
Created on Dec 28, 2014

@author: waldo

Creates a subset of the course/person dataset, replacing the student ID with a random
number between 1 and 10,000,000 but which is unique for each user and constant for the
same user, and replaces the name of the student with a randomly name chosen from a list
of the most common first and last names in the U.S. These names must be stored in
files named femaleNames.csv, maleNames.csv, and lastNames.csv in the directory in which
the program is run. The program takes the name of the file containing all of the 
course/person records and the name of the subset file to be generated as command
line arguments.
'''
import csv, random, sys

def pickThis():
    '''
    Randomly returns a value of True or False; used to pick which records will be in
    the subset generated. Changing the values of the maximum returned integer will decrease
    the number of records chosen. As it is now, it will give about one in six.
    '''
    if random.randint(1,6) == 2:
        return True
    else:
        return False
    
def buildNlist(fname):
    '''
    Build a list of names from the file with the supplied name. The file is assumed
    to be in CSV format, with one name per line. 
    '''
    inf = csv.reader(open(fname, 'rU'))
    flist = []
    for n in inf:
        flist.append(n[0])
    return flist, len(flist)

def processName(gender):
    '''
    Return a gender-appropriate name  to be used to mask the real user name. If the
    (self-reported) gender is missing, then randomly chooses a gender for the name.
    There is no guarantee that the returned name will be unique.
    '''
    retName = ''
    if gender == 'na':
        if random.randint(0,1) == 0:
            gender = 'm'
    if gender == 'm':
        retName = mnlist[random.randint(0, mncount - 1)]
    else:
        retName = fnlist[random.randint(0, fncount - 1)]
    retName = retName + ' ' + lnlist[random.randint(0, lncount - 1)]
    
    return retName

def maskId(edxId, gender):
    '''
    Returns a random name and user id given an edxId and a gender. The name and id
    will be the same for the same edx user ID. The generated id will be unique; there
    is no guarantee that the generated name will be unique.
    '''
    if edxId in idDict:
        return idDict[edxId][0], idDict[edxId][1]
    else:
        newName = processName(gender)
        i = random.randint(0, 10000000)
        while i in nidList:
            i = random.randint(0, 10000000)
        idDict[edxId] = [i, newName]
        nidList.append(i)
    return i, newName
        
    
    
if __name__ == '__main__':
    '''
    Checks the command line inputs, reads in the name files, and the goes through the
    large file, randomly picking some of the entries. Once an entry is picked, it
    has the id number changed and the name altered, and then gets written to the 
    output file. At the end, the total number of records read in the input file and
    the number written to the output file are displayed as a check.
    '''
    if len(sys.argv) != 3:
        print 'Usage: buildRandomSubset.py fullDataSet.csv newDataSet.csv'
    infName = sys.argv[1]
    inf = csv.reader(open(infName, 'rU'))
    outfName = sys.argv[2]
    outf = csv.writer(open(outfName, 'w'))
    
    idDict = {}
    nidList = []
    fnlist, fncount = buildNlist('femaleNames.csv')
    mnlist, mncount = buildNlist('maleNames.csv')
    lnlist, lncount = buildNlist('lastNames.csv')
    
    outf.writerow(inf.next())
    numlines = 0
    totLines = 0
    for l in inf:
        totLines += 1
        if pickThis():
            nid, nname = maskId(l[1], l[10])
            l[1] = nid
            l[2] = nname
            outf.writerow(l)
            numlines += 1
    print str(numlines) + " lines written out of " + str(totLines)
            
    