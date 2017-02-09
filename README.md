de_id
=====

De-identification scripts from first year of MITx and HarvardX courses
---

*******************************************
*Technology required to run these scripts:*
*******************************************

Python 2.7
iPython Notebook
sqlite3

**********************************
*Inputs required for this process*
**********************************

1) A .csv (comma-delimited text file) version of the Person-Course
dataset. 

+Person-course is a secondary dataset that is generated
based upon registration data and activity data, so is a merge of
the edX tracking logs and student-level demographics. The original
incarnation included such values as the number of courseware 
interactions, the number of video play events, and the number
of forum posts. The year two dataset includes more computed
values, so care should be taken with these scripts that it is not
run blindly, please do evaluate which columns are quasi-identifiers
and make sure that any new columns are either included or not
based upon informed choices.

2) A determination of which columns are quasi-identifiers. 

+In the first two years, we used gender, country, year of birth, level of 
education, and number of forum posts. We also used the set of courses that a
single student took, since that could be used to re-identify the student.
Care should be taken to 
choose variables that could reasonably be used to re-identify,
but also don't choose so many that the dataset is completely
obliterated.

3) A file that maps countries into continents. 

+A pickled dictionary of mapping is included here.


*********************
*Useful Definitions *
*********************

1) Utility values
   This term is taken from a Cynthia Dwork (then Microsoft Research, now Harvard)
   paper. The general idea is to have some key variables that 
   you monitor while you make changes to the dataset. For the
   purposes of this project, I chose to take the mean, SD, 
   and the entropy. The Utility Matrix is basically just a
   table of these values for columns specified to that 
   function. 

2) Entropy
   Suggestion for this as a measure of change from Ike Chuang
   (MIT). Using the e-based definition. Just a measure of 
   "information." Look at Wikipedia for more info, very simple
   formula.

3) K-anonymity
   See Latanya Sweeney's work. A dataset is k-anonymous if 
   you cannot distinguish any one record from k-1 other records
   based on identifiers or quasi-identifiers.

4) L-diversity
   Even if a dataset is k-anonymous, if it is not l-diverse then
   sensitive information can still be disclosed. Within a k-anonymous
   block, even if you cannot distinguish any individual record from
   another based on quasi-identifiers, if the value of any sensitive
   variable is uniform, then you know the value for all individuals
   matching that set of quasi-identifiers.

5) Quasi-identifier
   A variable that alone may not identify an individual, but in combiation
   with other information may prove uniquely identifying. Example is gender
   or country of origin.

*********************
*General User Manual*
*********************

This is intended as a VERY broad overview of the process as it was designed.
For more information, read the documents accompanying the data release, read
the comments in the code, or email waldo@g.harvard.edu.

Step 1: Generate the database file
----------------

The first step in the process is to convert the person/course database supplied from HarvardX and MITx into a
sqlite database. This is accomplished by running the program buildDB.py using the command line

>    python buildDB.py csvFileIn databaseFileOut countryTableFileName {verbose}

The countryTableFileName is the name of a file that maps country codes to country names. Note that there is a
new field in the year 2 combined data that is the country name; I've checked and the names in that differ from
the names obtained from the countryTable only in terms of spelling and completeness, not in terms of what
country is indicated, so this may be a step that we can get rid of in the future.

There are different variations of the database that can be obtained with the current version of the program, 
based on the participation levels of the students in the resulting database. So we can now generate databases
for all of the students, for the students who at least viewed content, for the students who explored (i.e., 
looked at at least half of the content), or the students who were certified in the course. Each of these steps
cuts down the number of students in the database.

Note that there is still some strange code that I don't particularly understand in this program. High on this 
list is the code that creates the source table and the way types are assigned to the values; this makes things 
somewhat more complex in some of the other steps and would be good to revisit at some point.

Step 2: Generate the classSuppress lists
-----------

The classSuppress lists are files containing a set of user_id/course_id combinations that need to be suppressed
to insure that users are not identified by the set of classes they are taking. There are two ways of generating
these lists at this time:

    * Randomly picking a class, and repeating until the right level of anonymity is reached for the user
    
    * Picking classes in which the user has participated less than others, and deleting those until the right
    level of anonymity has been reached
    
Either of these is done with the program courseSetDeIdentify.py, which is run using the command line

>   courseSetDeidentify.py dbname k-value {P,R}

where dbname is the name of the database file containing the records, k-value is the level of anonymization needed,
and P indicates anonymize by preferring dropping by participation and R indicates anonymizing by random drops. 

Running this program will produce a file named classSuppressX{P,R} where X is the level of anonymity (the value passed
in as k-value) and P/R indicates if the suppression was by participation or random. The file produced will be a pickled
version of the set of user_id/course_id combinations that will need to be suppressed.

Step 3: Generate bin files for numeric quasi-identifiers (in particular, YoB and Forum Posts)
------------

Next comes the step of generating binning information for the numeric quasi-identifiers. This is done with the program
numeric_generalization.py, which is run with the command line

>   python numeric_generalization.py dbName yearBinFileName postBinFilename YoB-bin-size Post-bin-size

where dbName is the filename of the database, yearBinFileName and postBinFilename are the names of the files that
will be produced, and YoB-bin-size and Post-bin-size are integer values for the minimum size of the bins to be 
produced. The files produced will be pickled versions of dictionaries from values being generalized to the pair of
the range of the generalization and the mean of the values that were generalized.

Step 4: Build the country generalization file
-----------------

Next comes generalizing those records where the k-anonymity of the user is revealed by their location. This is done
by running

>   python buildcountrygeneralizer dbfile outputFile country_to_continent_file {p}

where dbfile is the name of the database file, outputFile is the file to produce, and country_to_contenent_file is a 
file mapping from particular countries to regions. If 'p' is added, a table showing the mappings used will be produced.
The output file will be a pickled version of a dictionary that will map from countries to the form that can be
used without revealing the user; if the count of users in a particular country is high enough it will be the 
country, otherwise it will be a region.

Step 5: Building the full suppression set
-----------

The next step builds all of the records that need to be suppressed even after binning. To build this set, use the
command

>   python buildFullSuppressionSet.py databaseFile classSuppress geoSuppress yobFile forumFile NewSuppress k-anonValue

where databaseFile is the name of the database, classSuppress is the name of a file produced during step 2, geoSuppress
is the name of the file generated in step 4, yobFile and forumfile are the files produced in step 3, NewSuppress is the
name of the general suppression file to be created, and k-anon is the level of anonymity for the result. Running
this will produce a pickled set containing all of the user-id/course-id combinations that need to be suppressed
for the appropriate level of anonymity.

Step 6: Building the final, de-identified CSV file
-------------

The final step is to build the de-identified csv file; this is done with the command

>   python buildDeIdentifiedCSV databaseIn CSVfileOut recordSuppressFile countryGeneralizationFile YoBbinfile postbinfile

where databaseIn is the database file, CSVfileOut is the de-identified file to be produced, recordSuppressFile is the
file produced in step 5, countryGeneralizationFile is the file produced in step 4, and Yobbinfile and postbinfile are
the files produced in step 3. 




Good luck!