__author__ = 'olivia'

import sys
import numpy as np
import pandas as pd

"""
Reads in a CSV of de-identified data that has been binned but not suppressed,
and performs suppression in one of four ways:


1) Marginal.  From the column's values in the original data set, independently
draw each column value randomly.
2) Marginal mean. From the column's values in the original data set, independently
draw each column value as the mean of 5 random choices.
3) Joint.  From the column's values for records with identical quasi-identifier
values, randomly draw each column value, with additive noise to mask which rows
are fake.
4) Joint mean.  From the column's values for records with identical quasi-identifier
values, equate column value to their mean, with additive noise to mask which rows
are fake.
"""

K_VALUE = 5

# Fields in the original dataset of interest. This includes the quasi-identifiers
# and the numeric field for which bias is desired to be minimized which, in this
# case, is grade.
QIs = ["Location",
       "Level of Education",
       "Year of Birth",
       "Gender",
       "Mean Number of Forum Posts"]
fields_of_interest = QIs + ['Grade']

def read_input_data(filename):
    """
    Read and format the csv of binned but not yet suppressed data.

    This only reads the fields of interest, and formats data fields
    into the correct format, setting null values appropriately.
    """

    df = pd.read_csv(filename, low_memory = False)

    # Only take columns of interest.
    df = df[fields_of_interest]
    df['Count'] = 1

    # Fill NA values appropriately.
    df['Year of Birth'] = df['Year of Birth'].astype(str)
    df[['Location', 'Level of Education', 'Year of Birth', 'Gender']].fillna("NA")
    df[['Grade', 'Mean Number of Forum Posts']] = \
        df[['Grade', 'Mean Number of Forum Posts']].fillna(0)
    return df
    
def create_base_dataframes(df, k=K_VALUE):
    """
    Creates dataframes corresponding to the rows that need to be suppressed.

    It accomplishes this by finding unique combinations of quasi-identifiers and
    the number of times that these combinations occur, and then identifying rows
    where combinations occur less than k times.
    """
    # Count how many times each unique combination of quasi-identifiers occur
    combos = df[QIs+['Count']].groupby(QIs, as_index=False).agg(np.sum)
    # Calculate (1) Rows that need to be suppressed (i.e. count is less than k), and
    # (2) Dataframe containing all original rows
    supp = pd.merge(df[fields_of_interest], combos[combos['Count'] < k], on=QIs, how='inner')
    total = pd.merge(df[fields_of_interest], combos, on=QIs, how='inner')
    return supp, total

def duplicate_anon_violating_rows(supp, k=K_VALUE):
    """
    Takes in a dataframe of rows that are anonymity-violating and then
    duplicates each row the necessary number of times by repeating rows
    until they are present k times.
    """
    to_dupe = supp[QIs + ['Count']].drop_duplicates()
    duped = to_dupe[to_dupe['Count']==(k-1)]
    for i in range(k-2, 0, -1):
        to_repeat = supp[supp['Count']==i]
        duped = duped.append(pd.concat([to_repeat]*(k-i), ignore_index=True))
    return duped

def create_marginal_df(supp, total, values, outname, noise = False):
    """
    From a given column's values in the original data set, independently
    draw each column value randomly and add to data set to make it k-anonymous.
    """
    # Identify quasi-identifier rows that have to be duplicated.
    duped = duplicate_anon_violating_rows(supp)
    # Add normally-distributed noise if desired.
    if noise:
        noise_to_add = np.random.normal(loc=0, scale=np.std(values), size=n_add)
    else:
        noise_to_add = 0
    # Set the value of the numeric column to the new randomly drawn values.
    duped['Grade'] = list(np.random.choice(values,size=len(duped)) + noise_to_add)
    # Ensure no grade is greater than 1 or less than 0.
    duped.Grade[duped.Grade>1] = 1
    duped.Grade[duped.Grade<0] = 0
    # Append newly drawn values to dataset and write to csv.
    df_marginal_anon = total.append(duped[total.columns])
    df_marginal_anon.to_csv(outname)

def create_marginal_df_mean(supp, total, values, outname, noise=False):
    """
    From a given column's values in the original data set, independently
    draw each column value as the mean of 5 random choices and add to data
    set to make it k-anonymous.
    """
    # Identify quasi-identifier rows that have to be duplicated.
    duped = duplicate_anon_violating_rows(supp)

    n_add = len(duped)
    # Generate vector that has 5 random choices of grade per row that needs to be added (s).
    s = pd.Series(np.random.choice(values,size=n_add*5+1))
    s_means = ((s + s.shift(-1) + s.shift(-3) + s.shift(-4) + s.shift(-5)) / 5)[::5]
    # Add normally-distributed noise if desired.
    if noise:
        noise_to_add = np.random.normal(loc=0, scale=np.std(values), size=n_add)
    else:
        noise_to_add = 0
    # Set the value of the numeric column to the new randomly drawn values.
    duped = duped.drop('Grade', 1)
    duped['Grade'] = list(s_means[:n_add] + noise_to_add)
    # Ensure no grade is greater than 1 or less than 0.
    duped.Grade[duped.Grade>1] = 1
    duped.Grade[duped.Grade<0] = 0

    # Append newly drawn values to dataset and write to csv.
    df_marginal_anon_mean = total.append(duped[total.columns])
    df_marginal_anon_mean.to_csv(outname)

def create_joint_df_no_mean(supp, total, values, outname, noise=False):
    """
    From a given column's values for records with identical quasi-identifier
    values, randomly draw each column value, with additive noise to mask
    which rows are fake.
    """
    # Identify quasi-identifier rows that have to be duplicated.
    to_dupe = pd.DataFrame(supp[fields_of_interest+['Count']].groupby(QIs)['Grade'].apply(list)).reset_index()
    to_dupe['Count'] = to_dupe[0].apply(len)
    to_dupe.columns = QIs + ['Grade Choices','Count']
    duped = duplicate_anon_violating_rows(to_dupe)
    # Merge back in the possible grade choices.
    duped = pd.merge(duped[QIs], to_dupe[QIs+['Grade Choices', 'Count']], on=QIs)
    
    # Add normally-distributed noise if desired.
    if noise:
        noise_to_add = np.random.normal(loc=0, scale=np.std(values), size=len(duped))
    else:
        noise_to_add = 0
    # Set the value of the numeric column to the new randomly drawn values.
    duped['Grade'] = list(duped['Grade Choices'].apply(np.random.choice) + noise_to_add)

    # Ensure no grade is greater than 1 or less than 0.
    duped.Grade[duped.Grade>1] = 1
    duped.Grade[duped.Grade<0] = 0
    
    # Append newly drawn values to dataset and write to csv.
    df_joint_anon_no_mean = total.append(duped[total.columns])    
    df_joint_anon_no_mean.to_csv(outname)

def create_joint_df(supp, total, values, outname, noise=True):
    """
    From the column's values for records with identical quasi-identifier
    values, equate column value to their mean, with additive noise to mask which rows
    are fake.
    """
    # Identify quasi-identifier rows that have to be duplicated.
    to_dupe = supp[QIs+['Grade','Count']].groupby(QIs,as_index=False).mean()
    to_dupe.columns = QIs + ['Mean Grade','Count']
    duped = duplicate_anon_violating_rows(to_dupe)
    # Merge back in the possible grade choices.
    duped = pd.merge(duped[QIs], to_dupe[QIs+['Mean Grade', 'Count']], on=QIs)

    # Add normally-distributed noise if desired.
    if noise:
        noise_to_add = np.random.normal(loc=0, scale=np.std(values), size=len(duped))
    else:
        noise_to_add = 0
    # Set the value of the numeric column to the new randomly drawn values.
    duped['Grade'] = list(duped['Mean Grade'] + noise_to_add)

    # Ensure no grade is greater than 1 or less than 0.
    duped.Grade[duped.Grade>1] = 1
    duped.Grade[duped.Grade<0] = 0

    # Append newly drawn values to dataset and write to csv.
    df_joint_anon = total.append(duped[total.columns])
    df_joint_anon.to_csv(outname)

def main(inname, outname, method):
    """
    The main routine that will create and write the final de-identified data set
    with improved suppression methods.
    This method will open a csv that has been generlized but not suppressed, and
    then write a .csv file with the name supplied that achieves k-anonymity via
    the addition of rows using one of four methods.
    """

    df = read_input_data(inname)
    supp, total = create_base_dataframes(df, k=K_VALUE)
    if method == 1:
        create_marginal_df(supp, total, df['Grade'], outname)
    elif method == 2:
        create_marginal_df_mean(supp, total, df['Grade'], outname)
    elif method == 3:
        create_joint_df_no_mean(supp, total, df['Grade'], outname)
    elif method == 4:
        create_joint_df(supp, total, df['Grade'], outname)

if __name__ == '__main__':
    """
    The main routine, that will take as input the binned but not suppressed csv file,
    and output a CSV file that is suppressed using one of the four methods.
    Usage: python suppressAndBuildDeidentifiedCSV_v2.py CSVfileIn CSVfileOut method
    where method 1 = Marginal, 2 = Marginal Mean, 3 = Joint, 4 = Joint Mean
    """
    if len(sys.argv) < 4:
        print 'Usage: python suppressAndBuildDeidentifiedCSV_v2.py CSVfileIn CSVfileOut method'
        sys.exit(1)

    inname = sys.argv[1]
    outname = sys.argv[2]
    method = int(sys.argv[3])

    main(inname, outname, method)
