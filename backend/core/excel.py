import pandas as pd
import openpyxl
import os.path
from backend.core import alg
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Color, PatternFill

# Fetch the next alphabetical symbol in 'coc.xlsx'
def get_next_symbol():
    prev_symbol = ""
    for row in ws.iter_rows(ws.max_row, ws.max_row):
        prev_symbol = row[0].value
    symbol = ""
    f = open("backend/tickers.txt", "r")
    lines = f.readlines()
    print("prev_symbol: " + str(prev_symbol))
    for i in range(0, len(lines)):
        items = lines[i].split("|")
        if items[1] == prev_symbol:
            # Get next as long as it's not OOB
            if (i + 1) < len(lines):
                symbol = lines[i + 1].split("|")[1]
            break
    f.close()
    return symbol


# Color codes criteria columns with green/red for if they pass/fail
def color_code_row(row_num, ws, criterion):
    green_fill = PatternFill(
        fill_type="solid", start_color="3CB371", end_color="3CB371"
    )
    red_fill = PatternFill(fill_type="solid", start_color="CD5C5C", end_color="CD5C5C")
    # Only color the cells relative to the Criteria (hard-coded for G thru M)
    idx = 0
    for alpha in range(ord("H"), ord("N") + 1):
        curr_cell = ws[chr(alpha) + str(row_num)]
        if criterion[idx]:
            curr_cell.fill = green_fill
        else:
            curr_cell.fill = red_fill
        idx += 1

# Adds a new row for this symbol to the end of the excel file
def update(symbol, data_dict):
    dest_filename = "coc.xlsx"
    overwrite_row = None
    if os.path.isfile(dest_filename):
        wb = load_workbook(filename=dest_filename)
        ws = wb.active
        for idx in range(2, ws.max_row + 1):
            curr_symbol = ws["A" + str(idx)].value
            if curr_symbol.lower() == symbol.lower():
                overwrite_row = idx
                break
    else:
        wb = Workbook()
        ws = wb.active
        # Initializes the sheet name and header row
        ws.title = "Analysis"
        ws.append(
            [
                "",
                "Score",
                "Sector",
                "Price",
                "Graham Num (vs. price)",
                "BVPS (vs. price)",
                "Div. Yield",
                "Criteria 1 (Strength of Sales)",
                "Criteria 2 (Current Ratio)",
                "Criteria 3 (Dividend Reliability)",
                "Criteria 4 (Earnings Deficits)",
                "Criteria 5 (Annual EPS Growth)",
                "Criteria 6 (Market Cap vs. Net Asset Value)",
                "Criteria 7 (Cheapness of Earnings)",
            ]
        )
        # Resize column widths to show full column titles. Skips (empty) Col A.
        for alpha in range(ord("B"), ord("M") + 1):
            curr_char = chr(alpha)
            title_width = len(ws[curr_char + "1"].value)
            if title_width > 12:
                ws.column_dimensions[curr_char].width = title_width
            else:
                ws.column_dimensions[curr_char].width = 12
        # Freezes the top row of the excel file
        wb["Analysis"].freeze_panes = "A2"
    health_result = alg.health_check(
        data_dict["mkt_cap"],
        data_dict["sales"],
        data_dict["pe_ratio"],
        data_dict["curr_ratio"],
        data_dict["eps_list"],
        data_dict["dividend"],
        data_dict["dividend_list"],
        data_dict["assets"],
        data_dict["liabilities"],
        data_dict["div_yield"],
    )
    # Create array of color-codes for Criteria columns
    criterion = []
    for criteria in health_result:
        if "green" in criteria:
            criterion.append(True)
        else:
            criterion.append(False)
    for i in range(0, len(health_result)):
        health_result[i] = health_result[i].replace("[green]", "").replace("[/green]", "").replace("[red]", "").replace("[/red]", "")
        health_result[i] = health_result[i][3:] # Removes the "CX: " prefix
    # Stores the row being added
    new_row = [
        data_dict["symbol"].upper(),
        str(data_dict["score"]),
        data_dict["sector"],
        str(data_dict["price"]),
        str(data_dict["graham_num"]) + " (" + str(round(data_dict["graham_num"]/data_dict["price"], 2)) + ")",
        str(data_dict["bvps"]) + " (" + str(round(data_dict["bvps"]/data_dict["price"], 2)) + ")",
        data_dict["div_yield"],
        health_result[0],
        health_result[1],
        health_result[2],
        health_result[3],
        health_result[4],
        health_result[5],
        health_result[6],
    ]
    # Either overwrites the row for the symbol or adds a new row for it
    idx = 0
    if overwrite_row != None:
        for col, val in enumerate(new_row, start=1):
            ws.cell(row=overwrite_row, column=col).value = val
            color_code_row(overwrite_row, ws, criterion)
    else:
        ws.append(new_row)
        color_code_row(ws.max_row, ws, criterion)
    wb.save(filename=dest_filename)
    return
