import pandas as pd
import openpyxl

# TODO - Check for the symbol, then overwrite it in the excel document
# https://pythonbasics.org/write-excel/

def update(symbol, dataDict):
    # Index = Symbol names
    # Columns = Criteria
    df = pd.DataFrame(
        [[11, 21, 31],
        [12, 22, 32],
        [31, 32, 33]],
        index=['one', 'two', 'three'],
        columns=['', 'b', 'c'])
    df.to_excel('coc.xlsx', sheet_name='Criteria')
    return