__author__ = 'alex'

import sys, pickle
import config
import de_id_functions
# import needed files
import buildDB
from courseSetDeIdentify import main as courseSetDeIdentifyMain
import numeric_generalization_v2
import buildcountrygeneralizer
import buildFullSuppressionSet
import buildDeIdentifiedCSV
"""
Take dbname, k value, bin size as overall arguments
"""
def main():
    # Step 1 creates the database file
    db = de_id_functions.dbOpen(config.databaseFile)
    # buildDB config.csvFileIn config.databaseFileOut config.countryTableFileName
    ccodes = buildDB.sourceLoad(db, fromFileName, 'source')
    pf = open(config.countryTableFileName, 'w')
    pickle.dump(ccodes, pf)
    pf.close()

    # Step 2 generates the classSuppress lists
    try:
        db.execute("Create Index user_id_idx on source ('user_id')")
    except:
        pass
    db.execute('SELECT user_id, course_id FROM source ORDER BY user_id')
    user_class_list = db.fetchall()
    courseSetDeIdentifyMain(user_class_list, config.k_value, config.anonymise_by, config.outname)

    # Step 3 generates bin files for quasi-identifiers
    year_bin_file = open(config.yearBinFileName, 'w')
    post_bin_file = open(config.postBinFilename, 'w')
    # need to close the above?
    numeric_generalization_v2.main(db, year_bin_file)

    # Step 4 builds the country generalization files; 
    # q: how to make this step optional?
    db.execute('Select cc_by_ip from source')
    cc_list = db.fetchall()
    buildcountrygeneralizer.main(cc_list, config.outputCountryGeneralizeFilename, config.country_to_continent_file, config.table_mappings_show, config.binsize)
    
    # Step 5 builds the full suppression set
    buildFullSuppressionSet.main(db, config.outname, config.outputCountryGeneralizeFilename, config.yearBinFileName, config.postBinFilename, config.NewSuppress, config.k_value)
    
    # Step 6 builds the final de-identified CSV dataset
    db.execute(build_select_string('source'))
    full_list = db.fetchall()
    buildDeIdentifiedCSV.main(full_list, config.CSV_fileout, config.NewSuppress, config.outputCountryGeneralizeFilename, config.yearBinFileName, config.postBinFilename)

main()