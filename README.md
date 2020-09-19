## Circle of Competence
A program to web-scrape stock data, and analyze symbols based on various criteria discussed in Warren Buffett's The Intelligent Investor. The goal is to quickly analyze a stock and determine its rough intrinsic value.

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

## Instructions to Run on your system
1. Clone the repository
2. Run the `redux.py` file in `/backend/redux/`
3. Enter a US stock symbol you wish to analyze.
4. View the score (out of 7) for the symbol's health in your console.
5. Repeat the above as necessary.
6. Type 'exit' to quit

## To Do List
### General tasks
1. Add error handling for invalid stock symbols.
2. Output the analysis results to an Excel document.
