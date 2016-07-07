# Needed for Step 1: buildDB
csvFileIn = ?
databaseFile = ?
countryTableFileName = ?
# Needed for Step 2: classSupress lists generation
k_value = 5
outname = "ClassSuppress"
# anonymise by P for preferring dropping by participation 
# and R indicates anonymizing by random drops.
anonymise_by = P/R
# Needed for Step 3: Generate bin files for numeric quasi-identifiers 
# (in particular, YoB and Forum Posts)
yearBinFileName = ?
postBinFilename = ?
YoB_bin_size = ?
Post_bin_size = ?
# Needed for Step 4: build country generalization files
# Not needed for data without geographic info
outputCountryGeneralizeFilename = ?
country_to_continent_file = ?
# want table produced of the mappings produced? put a p below
table_mappings_show = p
# Needed for Step 5: Building the full suppression set
NewSuppress = ?
# Needed for Step 6: Building the final de-identified CSV data set
CSV_fileout = ?

### Global Variables
geo_binsize = 5000