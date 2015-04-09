#!/usr/bin/env python

__author__ = 'waldo'

from de_id_functions import *
import sys
import random

def buildCDict(ulist):
    """
    Build a dictionary of all course combinations taken by students.

    The dictionary produced by this routine will be keyed by the concatenation of the names
    of the courses taken by some student, in canonical order and separated by the '#' character.
    The value of any dictionary entry will be a list of the students taking that combination of
    courses. Note that the dictionary only contains entries for course combinations that are being
    taken by some student.

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
    sorted order separated by '#'. This is used to re-order a string that is the concatenation
    of the courses taken by a student into a canonical form.

    :param coursestring: a string of terms (course names) separated by '#'
    :return: a string of terms (course names) in order, separated by '#'
    '''
    clist = coursestringtolist(coursestring)
    clist.sort()
    return courselisttostring(clist)

def coursestringtolist(coursestring):
    """
    Create a list of courses from a string that contains the course names separated by the '#' character

    Parses a string into a list of sub-strings. The sub-strings are assumed to be separated by the
    '#' character, which is dropped in the list. The order of the strings in the list is not
    guaranteed.

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

    Given a list of strings, return a single string that is the concatenation of the strings
    separated by the '#' character. Note that the string returned is ordered by the default
    order of the list; if a particular order is required that needs to be imposed on the
    list prior to calling this function.

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
    """
    Given a set of classes taken by a student, randomly return one of those classes.

    Note that this routine does not use either the student or c parameter; these are included
    to give the same signature as partipationdropclass.

    :param student: the student who is taking this collection of classes
    :param classlist: the names of the classes taken by the student, as a string with the class names
    separated by the '#' character
    :param c:  a cursor into the database
    :return: the name of a class in classlist
    """
    clist = coursestringtolist(classlist)
    i = random.randint(0, len(clist)-1)
    return clist[i]


def participationdropclass(student, classlist, c):
    """
    Return a course associated with the given student in which the student did the least.

    Goes through the multiple courses that are associated with a particular student, and
    returns a course with the minimal participation for that student. Participation is based
    on the registered, viewed, explored, and certified flags.

    Note that classlist is not used in this routine at this point. However, it could be used
    to insure that the classlist and the list of courses returned by the Select statement are
    the same; if they are not then something may be wrong with the database. It is included
    now to give this the same signature as randomdropclass.

    :param student: the student whose classes are of interest
    :param classlist: A string containing the concatenation of the course names for this student,
    separated by '#'
    :param c: a cursor into the database
    :return: the name of a class in classlist
    """
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

    return todrop[0]

def dropfromlist(todrop, oldlist):
    """
    Given a string that contains some set of classnames separated by the character '#',
    drop the class indicated and return a new string, also using '#' as a name separator.

    :param todrop: the name of the class to drop
    :param oldlist: The original list of class names separated by the '#' character
    :return: A string with the set of class names remaining after removing todrop, separated by '#'
    """
    if todrop not in oldlist:
        return oldlist
    clist = coursestringtolist(oldlist)
    clist.remove(todrop)
    return courselisttostring(clist)


def dropClass(classlist, studentlist, classdict, c):
    """
    Given a set of classes and the students identified by that list, drop some records so that the
    students are no longer identified by the set of classes.

    Note that one of two selection functions can be set; one will prefer to drop classes that the
    student has done the least in, while the other will choose randomly.

    :param classlist: a string containing a list of class names, separated by '#'
    :param studentlist: a list of students who are identified by that set of classes
    :param classdict: the dictionary of class combinations and students taking that combination of classes
    :param c: a cursor into the database
    :return: None
    """
    if len(classdict[classlist]) > 4:
        return
    finddropclass = participationdropclass
    for student in studentlist:
        dropclass = finddropclass(student, classlist, c)
        print 'dropping course', dropclass, 'for student', student
        cmd = 'Delete from source where user_id = ' + '"' + student +'"' + 'AND course_id = ' + '"' + dropclass + '"'
        c.execute(cmd)
        newlist = dropfromlist(dropclass, classlist)
        if '#' in newlist:
            if newlist in classdict:
                classdict[newlist].append(student)
                if len(classdict[newlist]) < 5:
                    dropClass(newlist, {student}, classdict, c)
            else:
                dropClass(newlist, {student}, classdict, c)

    return

if __name__ == '__main__':
    dbName = sys.argv[1]
    c = dbOpen(dbName)
    c.execute('SELECT user_id, course_id FROM source ORDER BY user_id')
    ulist = c.fetchall()
    print len(ulist)
    cdict = buildCDict(ulist)
    #print cdict
    count = 0
    for classlist in cdict:
        if len(cdict[classlist]) < 5:
            count += 1
            dropClass(classlist, cdict[classlist], cdict, c)
    print count
    dbClose(c)