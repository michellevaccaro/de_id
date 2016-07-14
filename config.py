# Currently configured for HarvardX data

# Needed for Step 1: buildDB
csvFileIn = "../person_course_harvardxdb+mitxdb_2014_01_17a.csv"
databaseFile = "Test1DB"
countryTableFileName = "countrygentable"
# Needed for Step 2: classSupress lists generation
k_value = 5
outname = "ClassSuppress"
# anonymise by P for preferring dropping by participation 
# and R indicates anonymizing by random drops.
anonymise_by = "P"
# Needed for Step 3: Generate bin files for numeric quasi-identifiers 
# (in particular, YoB and Forum Posts)
yearBinFileName = "yearBinFile"
postBinFilename = "postBinFile"
YoB_bin_size = 5000
Post_bin_size = 5000
# Needed for Step 4: build country generalization files
# Not needed for data without geographic info
outputCountryGeneralizeFilename = "CountryGeneralizeOutput"
country_to_continent_file = "country_continent"
# want table produced of the mappings produced? put a p below
table_mappings_show = p
# Needed for Step 5: Building the full suppression set
NewSuppress = "GeneralSuppressionFile"
# Needed for Step 6: Building the final de-identified CSV data set
CSV_fileout = "FinalTest1CSV"

### Global Variables
geo_binsize = 5000