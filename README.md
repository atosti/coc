## Circle of Competence

This is a webscraping tool designed to analyze stock symbols according to criteria discussed in Benjamin Graham's __The Intelligent Investor__. It allows a user to quickly analyze a publicly-traded company, and roughly determine its intrinsic value.

As with all investing tools, use it at your own risk. ;)

## Running CoC on your system

0. Have Python 3+ installed on your system.
1. Clone the repository
2. Run the `main.py` file.
3. Enter a NYSE stock symbol (or series of symbols) you wish to analyze as well as any accompanying flags.
4. Wait for it to scrape the data (this can take a few seconds per symbol).
5. View the score (out of 7) and output in the console.
6. Repeat the above as necessary.
7. Type 'exit' or 'quit' to quit

### Running the Tests

1. From the main directory run `python -m pytest`.

### Running the formatter

This project uses Black. Simply run `black`. from the base directory.

## Usable Flags

Note that flags can be combined into strings prepended with a dash, so "-dx" would run both "-d" and "-x".

1. "-d" **Debug Mode**
   * Debug mode, prints all available fetched data for a symbol.
2. "-j" **JSON Output**
   * Generates and prints a JSON string for all the symbols given.
3. "-s" **Silent Mode**
   * Silent mode, hides all console output for each symbol. Best when used in combination with JSON generation.
4. "-x" **Excel Update/Creation**
   * Appends the symbol to a generated excel file, `coc.xlsx`. If the symbol already exists in file, then its row is overwritten with fresh data.

## Understanding The 7 Criteria

CoC examines a variety of key datapoints for a symbol, such as Market Capitalization, P/E Ratio, Current Ratio, EPS, EPS Growth, Assets, Liabilities, etc. in order to score a symbol out of 7 points.

It analyzes symbols based on the following criteria, where a value of **True** is viewed as relative strength, and **False** is viewed as relative weakness.

### The 7 Scoring Criteria

1. Does the company have over $700M(USD) in annual sales?
2. Does it have a current ratio of at least 2.0?
   * This determines whether the company's underlying assets are worth at least twice its short-term debts (those owed in one year).
3. If it pays a dividend, has it not missed or reduced its dividend payments in the last 5 years?
4. Has it not had an earnings deficit in the last 5 years?
   * Essentially, were there any years where it lost money?
5. Does it have earnings growth of at least 2.9% annually for the last 5 years?
   * This equates to approx. 15% total growth over 5 yrs.
6. Does it have cheap assets?
   * This is calculated as the following:
     * Is Market Capitalization < (Assets - Liabilities) * 1.5?
   * Essentially, is the value of all its outstanding shares less than 1.5x the assets leftover after paying all its debts.
7. Does it have cheap earnings?
   * This is calculated as the following:
     * Is its Price-to-Earnings Ratio <= 15?
   * Essentially, is it priced no greater than 15x its annual earnings.

### Additional Criteria

1. Weaknesses
   * A list of which criteria a symbol is weak in, and a brief description of why. Meant to better inform users of a company's risks.
2. Graham Number
   * The [Graham number](https://en.wikipedia.org/wiki/Graham_number) is a calculation to determine a fair value for a company's shares. Purchasing at or below this value is seen as ideal.
   * It is calculated as the sqrt(22.5 * EPS * BVPS).
     * Sometimes CoC returns a negative value for the Graham number. This means that either the EPS, the BVPS, or both are negative.
       * This is considered a Weakness in the symbol, and indicates a need for manually examining these two values further.
3. Dividend Yield
   * Relative to the currently traded price, what percentage of profits are payed out annually by the company.
4. Sector
   * A descriptor of which industry the company does business in.

## To Do List

1. Fetch more years of data for Dividends and EPS.
   * Dividends req. 20 years of data.
   * EPS req. 10 years of data, as does EPS growth.
   * FinViz has this information, see what other sites might as well.
2. Check additional criteria:
   * Annual and YoY growth of a company's revenue.
3. Fetch a subset of Stock symbols to check for the day.
   * E.g. scraping a FinViz search and checking the symbols that are returned.
4. Some symbols on Yahoo (e.g. YYY) fetch a different format page.
   * Adjust methods to handle either version of the page
   * https://finance.yahoo.com/quote/YYY vs https://finance.yahoo.com/quote/BGS demonstrates the difference.
   * This is because YYY is an ETF and not a company. Funds have different data about them entirely, figure a way to analyze these.
5. Implement a way to print out which years dividends were missed/reduced in a symbols weaknesses.
6. Add the dividend Payout Ratio to the console logs.
7.  Add a helper function to adjust urls to either use `.` or `-`as required by a website for scraping.
8.  Setup test coverage tools on the repo.
9.  Design around handling non-US companies and fetched values. Test with ASUSTeK, which is 2357 on TW(Taiwanese exchange)
10. Use Log scale for color gradient. Could use percentage deviations as well. Could also weight based on where the weakness is (how many years ago).
11. Create a method for checking completeness of data. If something's missing, attempt to find from other sources.
   * Start with Marketwatch -> Yahoo Finance for data present on both, such as price. I think Curr Ratio exists as well.
   * Build in a decoupled way, so any data stream can be swapped in/out.
12. Create a way to fetch large batches of data, but then update a dict with only singular values at a time.
   * And do this cleanly/concisely.
13. Add output to a local DB with creation dates for symbols. Update them periodically (as new annual reports emerge).
   * As part of the logs/JSON, include the creation date for the data fetch.
15. Hook up to a screener to get a list of desireable stocks of the day to check.
16. Add the ability to fetch quarterly data, and use rolling data for the last 5 years worth of quarters of data (as opposed to annual data).
   * This would allow for less gaps between 2019 data and 2020 at the begining of 2021, for example.