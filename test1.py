'''
Created on Jan 2, 2015

@author: waldo
'''
from de_id_functions import *

if __name__ == '__main__':
    testFile = 'maskedPersonCourse.csv'
    db = 'test2.db'
    c = dbOpen(db)
    sourceLoad(c,testFile,"source")
#    idGen(c, 'source', 'user_id', 'MHxPC13')
    c.execute('CREATE TABLE original AS SELECT * from source')
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print c.fetchall()
    
'''    c.execute("DELETE FROM source WHERE (roles = 'instructor' or roles = 'staff')")
    c.execute("DELETE FROM original WHERE (roles = 'instructor' or roles = 'staff')")
    c.execute("Pragma table_info (source)")
    varList = c.fetchall()
    print varList
    c.execute("Pragma table_info (original)")
    varList = c.fetchall()
    print varList
    '''

    
    
