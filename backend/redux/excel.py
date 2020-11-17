import pandas as pd
import openpyxl
import os.path
from openpyxl import Workbook, load_workbook

# Fetch the next alphabetical symbol in 'coc.xlsx'
def getNextSymbol():
    prevSymbol = ''
    for row in ws.iter_rows(ws.max_row, ws.max_row):
        prevSymbol = row[0].value
    symbol = ''
    f = open("backend/tickers.txt", "r")
    lines = f.readlines()
    print("Prevsymbol: " + str(prevSymbol))
    for i in range (0, len(lines)):
        items = lines[i].split('|')
        if items[1] == prevSymbol:
            # Get next as long as it's not OOB
            if (i + 1) < len(lines):
                symbol = lines[i+1].split('|')[1]
            break;
    f.close()
    return symbol

# Adds a new row for this symbol to the end of the excel file
def update(symbol, dataDict):
    dest_filename = 'coc.xlsx'
    if os.path.isfile(dest_filename):
        wb = load_workbook(filename = dest_filename)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = 'Analysis'
        ws.append(['', 'Score', 'Graham Num.', 'Price',
            'Sales > $700M', 'Curr. Ratio >= 2', 
            'No Missed Dividend(5yrs)', 'No Earnings Deficit(5yrs)', 
            'EPS avg > 33%(5yrs)', 'Cheap Assets', 'P/E < 15'])
    ws.append([dataDict['symbol'].upper(), dataDict['score'], dataDict['grahamNum'],
        dataDict['price'], dataDict['goodSales'], dataDict['goodCurrRatio'],
        dataDict['goodDividend'], dataDict['goodEps'], 
        dataDict['goodEpsGrowth'], dataDict['goodAssets'],
        dataDict['goodPeRatio']
    ])
    wb.save(filename = dest_filename)
    return