#!/usr/bin/env python

__author__ = 'waldo'

from de_id_functions import *
import sys

def courseDropper2(cursor, tableName, courseVar, courseName, changeVals, courseDict={}):
    """
    courseName: string, name of course to be dropped
    changeVals: list of strings, values of course_combo to drop
    courseDict: dictionary of courses and running tally of rows dropped
    drops course record where course equals courseName
    AND uniqUserFlag = "True"
    """
    delCount = 0
    for val in changeVals:
        cursor.execute("SELECT SUM(Count) FROM "+tableName+" WHERE ("+courseVar+" = '"+courseName+"' AND uniqUserFlag = 'True' AND course_combo = '"+val+"')")
        qry = cursor.fetchall()
        #print "changeVal qry length:"+str(len(qry))
        if (qry[0][0]): delCount += qry[0][0]
    print "delCount: "+str(delCount)
    if delCount == 0:
        return courseDict
    if courseName in courseDict.keys():
        courseDict[courseName] += delCount
    else:
        courseDict[courseName] = delCount
    for val in changeVals:
        cursor.execute("DELETE FROM "+tableName+" WHERE ("+courseVar+" = '"+courseName+"' AND uniqUserFlag = 'True' AND course_combo = '"+val+"')")

    return courseDict

def optimumDrop2(cursor, tableName, userVar, k, nonUniqueList, nComb=1):
    """
    cursor: sqlite3 cursor object
    tableName: string, name of main table
    userVar: string, name of userid var
    k: int, minimum cell size
    nonUniqueList: list of course_combo values already cleared for k-anonymity
    nComb: int, number of courses to try to drop, default 1
    iteratively tries 'dropping' one course for all of the records
    that are flagged as having a unique combo of courses
    then measures the entropy of the resulting group, and
    returns the position in courseList of the course to drop, along with the
    course_combo values that will benefit from the drop
    """
    qry = courseUserQry(cursor, tableName, userVar, 'True')
    if len(qry)==0:
        return qry
    posLen = len(qry[0][0]) #assumes first variable in each tuple is the course combo, finds num of positions to change
    preList = qry[:]
    preCombos = []
    for i in preList:
        preCombos.append(i[0])
    preEntropy = shannonEntropy(preList)
    postEntList = []
    preCount = 0
    for n in qry:
        preCount += n[1]
    print preCount
    iterTemp = itertools.combinations(range(posLen),nComb)
    dropCombos = []
    while True:
        try: dropCombos.append(iterTemp.next())
        except: break
    for i in dropCombos:
        postList = []
        tmpList = qry[:]
        for j in tmpList:
            newString = ""
            for l in range(posLen):
                if l in i:
                    newString+="0"
                else:
                    newString+=j[0][l]
            postList.append((newString,j[1]))
        try:
            cursor.execute("DROP TABLE coursedrop")
            cursor.execute("CREATE TABLE coursedrop (course_combo text, Count integer)")
        except:
            cursor.execute("CREATE TABLE coursedrop (course_combo text, Count integer)")
        cursor.executemany("INSERT INTO coursedrop VALUES (?,?)",postList)
        cursor.execute("SELECT course_combo, SUM(Count) FROM coursedrop GROUP BY course_combo")
        postQry = cursor.fetchall()
        postEntropy = shannonEntropy(postQry)
        postCount = 0
        for item in postQry:
            postCount += item[1]
        changeVals = []
        for k in range(len(i)):
            oldSpots = []
            iterTemp = itertools.combinations(i,k+1)
            while True:
                try: oldSpots.append(iterTemp.next())
                except: break
            for l in oldSpots:
                for m in postQry:
                    mList = list(m[0])
                    for n in l:
                        mList[n] = '1'
                    oldString = ''
                    for p in mList:
                        oldString+=p
                    if m[1]>=k and oldString in preCombos:
                        changeVals.append(oldString)
                    elif (m[0] in nonUniqueList) and oldString in preCombos:
                        changeVals.append(oldString)
        #print "Length of ChangeVals: "+str(len(changeVals))
        if len(changeVals)>0:
            postEntList.append((i,preEntropy-postEntropy,changeVals))
    if len(postEntList) == 0:
        return []
    first = True
    low = (99,99,[])
    for n in postEntList:
        if n[1]<low[1] and n[1] > 0.0:
            low = n
    return low

def userKanon2(cursor, tableName, userVar, courseVar, k):
    """
    cursor: sqlite cursor object
    tableName: string, name of table
    userVar: string, name of userid variable
    courseVar: string, name of course variable
    k: minimum group size
    creates a unique row record that is combo of
    courseid and userid, and then creates another variable
    that says which courses someone has taken
    then checks for unique count of courses taken
    and unique combinations of courses
    """
    courseList = courseComboUpdate(cursor,tableName,userVar,courseVar)
    value, uniqueList, nonUniqueList = uniqUserCheck(cursor,tableName,userVar,k)
    uniqUserFlag(cursor, tableName, uniqueList)
    dropNum = 1
    courseDrops = {}
    while value != 0.0 and dropNum != 16:
        print "DropNum: "+str(dropNum)
        print "non-anon value: "+str(value)
        courseTup = optimumDrop2(cursor, tableName, userVar, k, nonUniqueList,dropNum)
        #print "courseTup returned from OptimumDrop:"
        if len(courseTup) == 0 or len(courseTup[2])==0:
            dropNum +=1
            print "no more changes can be made, trying "+str(dropNum)+" courses at a time"
            return courseDrops
        courseNums = courseTup[0]
        changeVals = courseTup[2]
        print "length of changeVals"
        print len(changeVals)
        for i in courseNums:
            courseName = courseList[i]
            print "dropping courseName:"
            print courseName
            courseDrops = courseDropper2(cursor, tableName, courseVar, courseName, changeVals, courseDrops)
        courseList = courseComboUpdate(cursor,tableName,userVar,courseVar)
        value, uniqueList, nonUniqueList = uniqUserCheck(cursor,tableName,userVar,k)
        uniqUserFlag(cursor, tableName, uniqueList)
    return courseDrops

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: oldClassCombTest.py databaseFile"
        sys.exit(1)

    c = dbOpen(sys.argv[1])
    courseDrops = userKanon2(c, 'source', 'user_id', 'course_id', '5')
    for course in courseDrops.keys():
        print 'Dropped ' + str(courseDrops[course]) + ' rows for course ' + course

    c.execute("SELECT SUM(Count) FROM source")
    print (c.fetchall())
