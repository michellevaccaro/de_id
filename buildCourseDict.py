__author__ = 'waldo'

from de_id_functions import *
import sys

def buildCDict(ulist):
    """
    :param ulist: a list of all userId and the course ids, sorted by user id. If a user took
    multiple courses, there will be multiple entries for the user, one per course
    :return: a dictionary, keyed by the concatenation of all the courses taken by a single user,
    with a list of all the users that took that combination of courses. This will only be for
    combinations of more than one course that were taken by any particular user.
    """
    cdict = {}
    oldid = -1
    clist = ''
    unique = True
    ccount = dcount = itercount = 0
    for uid, cid in ulist:
        itercount += 1
        if (oldid == uid):
            dcount += 1
            clist += cid
            unique = False
        elif not unique:
            if clist in cdict:
                cdict[clist].append(oldid)
            else:
                cdict[clist] = [oldid]
                ccount += 1
            unique = True
            clist = cid
        oldid = uid
    print ccount, dcount, itercount
    print len(cdict.keys())
    return cdict



def parseCourseString(coursestring):
    """
    :param coursestring: A string that is the concatenation of names of courses, separated by
    the character '#'
    :return: A list of the course names, with the seperator character removed
    """
    parts = coursestring.partiion('#')
    retlist = [parts[0]]
    while parts[2] != '':
        parts = parts[2].partition('#')
        retlist.append(parts[0])
    return retlist


def dropClass(classlist, studentlist, classdict):
    pass

if __name__ == '__main__':
    dbName = sys.argv[1]
    c = dbOpen(dbName)
    c.execute('SELECT user_id, course_id FROM source ORDER BY user_id')
    ulist = c.fetchall()
    print len(ulist)
    cdict = buildCDict(ulist)

    count = 0
    for classlist in cdict:
        if len(cdict[classlist]) < 5:
            count += 1
            print classlist, len(cdict[classlist]), cdict[classlist]
            dropClass(classlist, cdict[classlist], cdict)
    print count