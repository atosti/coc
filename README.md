## Circle of Competence
A program to web-scrape stock data, and analyze symbols based on various criteria discussed in Benjamin Graham's __The Intelligent Investor__. The goal is to quickly analyze a stock and determine its rough intrinsic value.

As with all investing tools, use it at your own risk. ;)

## The 7 Criteria
This program examines Market Capitalization, P/E Ratio, Current Ratio, EPS, EPS Growth, Assets, and Liabilities. It analyzes them based on the following criteria, where an answer of TRUE is viewed as healthy.
1. Does the company have over $700M in annual sales? 
2. Does it have a current ratio of at least 200%?
3. Has it not missed any dividends in the last 20 years?
4. Has it not had an earnings deficit in the last 10 years?
5. Does it have earnings growth of at least 2.9% annually for the last 10 years?
6. Does it have cheap assets?
	* Is Market Capitalization < (Assets - Liabilities) * 1.5
7. Does it have cheap earnings?
	* Is its P/E ratio < 15?
8. Graham Number
	* The Graham Number is a calculation to determine a fair value for a company's shares. Purchasing at or below this value is seen as ideal.
	* It is calculated as the sqrt(22.5 * EPS * BVPS).

Currently, it checks for everything except for #3 (dividends). Also, it only checks with the last 5 years of data instead of the last 10 or 20 as some criteria specify. This is to be fixed in coming updates.

## Instructions to Run on your system
1. Clone the repository
2. Run the `redux.py` file in `/backend/redux/`
3. Enter a NYSE stock symbol you wish to analyze.
4. View the score (out of 7) for the symbol's health, as well as its Graham Num.
5. Repeat the above as necessary.
6. Type 'exit' to quit

## Usable Flags
Note that flags can be combined into strings prepended with a dash, so "-dx" would run both "-d" and "-x".

1. "-d"
	* Debug mode, prints all available fetched data for a symbol.
2. "-x"
	* Excel update. Appends the currently run symbol to an excel file for future reference.

## To Do List
1. Output the analysis results to an Excel document.
2. Fetch 10, or 20 years for EPS and dividends respectively.
3. Determine a symbol's industry/sector/sub-sector and output that information with its score.
	* FinViz has this information, see what other sites might as well.
4. Check additional criteria:
	* Annual and YoY growth of a company's revenue.
5. Add/use helper functions to convert larger numbers to use M/B/T abbreviations for millions, billions, etc.
	* This would improve readability of some output and prevent misreading large numbers by the user.
6. Fetch a subset of Stock symbols to check for the day.
	* E.g. scraping a FinViz search and checking the symbols that are returned.

## Symbols that return bad values
1. FHI
2. DKNG
