import pandas as pd
import openpyxl
import os.path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Color, PatternFill

# Fetch the next alphabetical symbol in 'coc.xlsx'
def get_next_symbol():
    prev_symbol = ''
    for row in ws.iter_rows(ws.max_row, ws.max_row):
        prev_symbol = row[0].value
    symbol = ''
    f = open('backend/tickers.txt', 'r')
    lines = f.readlines()
    print('prev_symbol: ' + str(prev_symbol))
    for i in range (0, len(lines)):
        items = lines[i].split('|')
        if items[1] == prev_symbol:
            # Get next as long as it's not OOB
            if (i + 1) < len(lines):
                symbol = lines[i+1].split('|')[1]
            break;
    f.close()
    return symbol


# Color codes columns G through M with green/red for true/false
def color_code_row(row_num, ws):
    # Fills True/False cells Green/Red in new row for readability
    green_fill = PatternFill(fill_type='solid', start_color='3CB371', 
    end_color='3CB371')
    red_fill = PatternFill(fill_type='solid', start_color='CD5C5C', 
        end_color='CD5C5C')
    for alpha in range(ord('G'), ord('M') + 1):
        curr_cell = ws[chr(alpha) + str(row_num)]
        if curr_cell.value:
            curr_cell.fill = green_fill
        else:
            curr_cell.fill = red_fill
    

# Adds a new row for this symbol to the end of the excel file
def update(symbol, data_dict):
    dest_filename = 'coc.xlsx'
    overwrite_row = None
    if os.path.isfile(dest_filename):
        wb = load_workbook(filename = dest_filename)
        ws = wb.active
        for idx in range(2, ws.max_row + 1):
            curr_symbol = ws['A' + str(idx)].value
            if curr_symbol.lower() == symbol.lower():
                overwrite_row = idx
                break;
    else:
        wb = Workbook()
        ws = wb.active
        # Initializes the sheet name and header row
        ws.title = 'Analysis'
        ws.append(['', 'Score', 'Sector', 'Graham Num.', 'Price', 'Div. Yield',
            'Sales > $700M', 'Curr. Ratio >= 2', 'No Missed Dividend(5yrs)', 
            'No Earnings Deficit(5yrs)', 'EPS avg > 33%(5yrs)', 'Cheap Assets', 
            'P/E < 15'])
        # Resize column widths to show full column titles. Skips (empty) Col A.
        for alpha in range(ord('B'), ord('M') + 1):
            curr_char = chr(alpha)
            title_width = len(ws[curr_char + '1'].value)
            if title_width > 12:
                ws.column_dimensions[curr_char].width = title_width
            else:
                ws.column_dimensions[curr_char].width = 12
        # Freezes the top row of the excel file
        wb['Analysis'].freeze_panes = 'A2'
    # Stores the row being added
    new_row = [data_dict['symbol'].upper(), data_dict['score'],
        data_dict['sector'], data_dict['graham_num'], data_dict['price'], 
        data_dict['div_yield'], data_dict['good_sales'], data_dict['good_curr_ratio'], 
        data_dict['good_dividend'], data_dict['good_eps'], 
        data_dict['good_eps_growth'], data_dict['good_assets'], 
        data_dict['good_pe_ratio']
    ]
    # Either overwrites the row for the symbol or adds a new row for it
    if overwrite_row != None:
        for col, val in enumerate(new_row, start=1):
            ws.cell(row=overwrite_row, column=col).value = val
            color_code_row(overwrite_row, ws)
    else:
        ws.append(new_row)
        color_code_row(ws.max_row, ws)
    wb.save(filename = dest_filename)
    return