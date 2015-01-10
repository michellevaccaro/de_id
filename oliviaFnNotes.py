Log:
    In De-identification.ipynb and de-identification.py:
        -Changed line from "if row[0] >= 5" to "if row[0] >= k", to ensure k-anonymity rather than always 5-anonymity
        -Updated kkey.append() lines in order to reflect corrected QI variable indices

In de_id_functions.py:
	# Simple SQL commands as functions
	addColumn(cursor, tableName, varName):
		adds blank column named "varName" to "tableName"
	selUnique(cursor, tableName, varName):
		return database with number of varName and number of rows with each value of varName
	simpleUpdate(cursor, tableName, varName, value):
		replace all values of given column "varName" in table "tableName" with "value"
	varIndex(cursor,tableName, varName):
		in "tableName", create index on column "varName" called "varName_idx" in order to help find data more quickly/efficiently (not viewable by user)
	dbOpen(db):
        connect to database "db" and return cursor for that database
	dbClose(cursor, closeFlag=True):
        Vacuums (copies the contents into a temporary database file and then overwrites the original with the temporary file) and closes current database

    # Functions that need to be done for a new dataset, but not thereafter
    sourceLoad(cursor, fname, tableName):
        Takes a .csv file named "fname" and reads it into a sqlite database defined by the cursor object. Deletes any existing table with the same name. Adds column called "Count" that is equal to 1.
    countryNamer(cursor, tableName, countryCode):
        Takes a variable, finds the unique instances of country codes, generates map to country names, then updates the country codes to country names where possible.    
    contImport(cursor, tableName, inFileName, varName1, varName2='continent'):
        Reads pickled dictionary from file, and then maps it to the specified country variable, loading it into a variable called "continent", unless otherwise specified
    sortHash(inWord):
        Creates a salted hash (hash + adding additional string to make original text harder to reverse) of a string input, returns hash      
    idGen(cursor, tableName, varName, prefix):
        takes usernames or userIDs and then sorts them by a 
        salted hash of the usernames (to prevent replicable sorting) and then creates
        sequential IDs for de-identification of the format course name + sequential number
        e.g. "MITx147300937" and adds these IDs to the table

    # Recreate country_continent file
    contExport(cursor, tableName, varName1, varName2, outFileName):
        outputs the mapping of country to continent to a pickled file, for later import as country_continent file

    # Functions for generalizing
    contSwap(cursor, tableName, varName1, varName2, th):
        Creates new variable that combines the values from the continent column and the country column, inserting continents where the n in a country is lower than th (generalizing to continents in order to maintain k-anonymity)
    tailFinder(cursor, tableName, varName, catSize):
        Specify upper and loewr tail for certain variable, set anything above upper tail or below lower tail equal to the tail value
    numBinner(cursor, tableName, varName, bw=5):
        Bin numbers into bins of specified width. Helpful to use tailFinder first to cut total range of values down to a multiple of the bin width. Bins are labeled "low-high".
    dateSplit(cursor, tableName, varName):
        Takes date/time stamps formatted "MM/DD/YYYYTxxxxxx" and strips out the date. Requires the T to denote beginning of the time
    
    # Diagnostic functions
    nullMarker(cursor, tableName, varList):
        Takes list of variables and then generates one column per variable with values 1 or 0 to denote if that record has missing or null values for the corresponding variable (inserts a new column named columnname_NF)
    nullWrap(cursor, tableName):
        a wrapper function, prompts user to select variables (the quasi-identifier columns), then creates dummy variables of form 'varname_NF' (0/1) that say whether a record has valid values for that variable
    ****iterKcheck(cursor, tableName, k, nullFlag = True):
        iteratively checks for k-anonymity, first with one variable, then two etc. and then as variables are checked, records with null values for the other variables are excluded from future checks
    *kkeyUpdate(cursor, tableName, varList, var="kkey"):
        takes the QI variables identified by varList and concatenates into kkey, where kkey is NULL if any of the QIs are null
    qiPicker(cursor, tableName):
        takes a cursor in a db, and then asks the user to specify the QI columns    
    grainSize(cursor, tableName, qiName):
        calls to table specified by cursor and tableName, then examines values, returns a float, "grain size" as given by n of categories/n of items, smaller value means less granular, bigger "grains" (aka more values per bucket)
    genPicker(cursor, tableName, varList):
        wrapper function to check the grain size of all of the QI variables. Returns string name of variable to generalize next
    *isTableKanonymous(cursor, tableName, k):
        takes sqlite table that contains column called kkey which is concatenation of QI variables, checks for k-anonymity, returns bool and supression required for k-anonymity (float btw. 0,1)
    kAnonWrap(cursor, tableName, k):
        wrapper function, gets list of variables from user input, updates kkey, checks for k-anonymity
    *userKanon(cursor, tableName, userVar, courseVar, k):
        Creates a unique row record that is combo of courseid and userid, and then creates another variable that says which courses someone has taken then checks for unique count of courses taken and unique combinations of courses. 
    courseComboUpdate(cursor, tableName, userVar, courseVar):
        Creates a row, course_combo, that contains the combination of courses that a given user has taken
    userKCheckTable(cursor, tableName, userVar, records='all'):
        creates a temporary-use table called "userkcheck" that holds unique course_combo values by userid. records option allows 'all', 'True', or 'False'
    courseUserQry(cursor, tableName, userVar, records='all'):
        wrapper, creates a temp table of unique course combo records, returns a qry with the course combo and number of unique users as the result, option allows for just getting users with "unique" (i.e. n<k) course combo values
    uniqUserCheck(cursor,tableName,userVar,k):
        used to check if there are unique combos of courses by user; returns percent of course combinations thare are unique (i.e. N < K), list of unique combos of courses, list of nonunique combos of courses
    uniqUserFlag(cursor, tableName, uniqueList):
        creates column uniqUserFlag that is boolean in order to indicate whether a user is taking a unique combination of courses
    shannonEntropy(itemList):
        determine shannon entropy for a given item
    optimumDrop(cursor, tableName, userVar, k, nonUniqueList, nComb=1):
        iteratively tries 'dropping' one course for all of the records that are flagged as having a unique combo of courses, then measures the entropy of the resulting group, and returns the position in courseList of the course to drop, along with the course_combo values that will benefit from the drop
    courseDropper(cursor, tableName, courseVar, courseName, changeVals, courseDict={}):
        drops course record where course equals courseName AND uniqUserFlag = "True"

    # Functions for censoring run after doing all generalizing
    contCensor(cursor, tableName, varName1, varName2):
        generalizes countries to continents if the number of countries is less than an integer, th, (similar to contSwap), only does it for all rows with a "False" export_flag
    censor(cursor, tableName, varName, value=""):
        sets value of given variable to specified value, for rows with export_flag = 'False'

    # Misc. Helper functions    
    dataUpdate(cursor,tableName,varName,catMap, newVar=False, newVarName = ''):
        either update an existing variable or set a new variable equal to values as specified by "catMap"
    colToList(queryResult):
        returns a list of the values outside of a tuple
    
    # Functions for exporting de-identified file    
    csvExport(cursor, tableName, outFileName):
        Asks user to specify columns in the database to export to a .csv file under the specified name in the cwd

In de-identification.py itself:
    General overview
    1. Define variables/names of locations of tables/etc.
    2. Load data into SQLite database (sourceLoad()), both as a "source" table and an "original" table for reference
    3. Converts "start_time" and "last_event" from date-time objects to only date objects
    4. 







