#!/usr/bin/env python

__author__ = 'waldo'

from de_id_functions import *
import sys
import random

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
        if oldid == uid:
            dcount += 1
            clist += ('#' + cid)
            unique = False
        elif not unique:
            clist = ordercoursestring(clist)
            if clist in cdict:
                cdict[clist].append(oldid)
            else:
                cdict[clist] = [oldid]
                ccount += 1
                print clist
            unique = True
            clist = cid
        else :
            clist = cid
        oldid = uid
    print ccount, dcount, itercount
    print len(cdict.keys())
    return cdict

def ordercoursestring(coursestring):
    '''
    Take a string of terms separated by the character '#' and return a string of those terms in
    sorted order separated by '#'
    :param coursestring: a string of terms (course names) separated by '#'
    :return: a string of terms (course names) in order, separated by '#'
    '''
    clist = coursestringtolist(coursestring)
    clist.sort()
    return courselisttostring(clist)

def coursestringtolist(coursestring):
    """
    Create a list of courses from a string that contains the course names separated by the '#' character

    :param coursestring: A string that is the concatenation of names of courses, separated by
    the character '#'
    :return: A list of the course names, with the separator character removed
    """
    parts = coursestring.partition('#')
    retlist = [parts[0]]
    while parts[2] != '':
        parts = parts[2].partition('#')
        retlist.append(parts[0])
    return retlist

def courselisttostring(courseslist):
    '''
    Create a string of course names separated by the '#' character from a list of the course names
    :param courseslist:
    :return: a string of the course names in the list, separated by the character '#'
    '''

    retstring = courseslist[0]
    i = 1
    while i < len(courseslist):
        retstring += ('#' + courseslist[i])
        i += 1
    return retstring

def randomdropclass(student, classlist, c):
    clist = coursestringtolist(classlist)
    i = random.randint(0, len(clist))
    return clist[i]


def participationdropclass(student, classlist, c):
    print 'in participationdropclass for student =', student
    cmd = 'Select * from source where user_id = "' + student + '"'
    c.execute(cmd)
    studentrecords = c.fetchall()
    todrop = studentrecords[0]
    i = 1
    while i < len(studentrecords):
        comprec = studentrecords[i]
        if todrop[4] > comprec[4]:
            todrop = comprec
        elif todrop[5] > comprec[5]:
            todrop = comprec
        elif todrop[6] > comprec[6]:
            todrop = comprec
        i += 1

    print 'Decided to drop', todrop[0]
    return todrop[0]

def dropfromlist(todrop, oldlist):
    clist = coursestringtolist(oldlist)
    clist.remove(todrop)
    return courselisttostring(clist)



def dropClass(classlist, studentlist, classdict, c):
    print 'entering dropClass with student list', studentlist
    if len(classdict[classlist]) > 4:
        return
    finddropclass = participationdropclass
    for student in studentlist:
        dropclass = finddropclass(student, classlist, c)
        print 'dropping course', dropclass, 'for student', student
        cmd = 'Delete from source where user_id = ' + '"' + student +'"' + 'AND course_id = ' + '"' + dropclass + '"'
        c.execute(cmd)
        print len(classdict[classlist])
        if len(classdict[classlist]) > 1:
            classdict[classlist].remove(student)
        newlist = dropfromlist(dropclass, classlist)
        if '#' in newlist:
            if newlist in classdict:
                classdict[newlist].append(student)
            if len(classdict[newlist]) < 5:
                dropClass(newlist, {student}, classdict, c)

    return


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
            dropClass(classlist, cdict[classlist], cdict, c)
    print count
    dbClose(c)