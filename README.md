## Circle of Competence

This is a webscraping tool designed to analyze stock symbols according to criteria discussed in Benjamin Graham's __The Intelligent Investor__. It allows a user to quickly analyze a publicly-traded company, and roughly determine its intrinsic value.

As with all investing tools, use it at your own risk. ;)

## Running CoC on your system

0. Have Python 3+ installed on your system.
1. Clone the repository
2. Run the `main.py` file.
3. Enter a NYSE stock symbol you wish to analyze and any accompany flags.
4. Wait for it to scrape the data (this can take a few seconds).
5. View the score (out of 7) output into the
6. Repeat the above as necessary.
7. Type 'exit' to quit

### Running the Tests

1. From the main directory run `python -m pytest`.

### Running the formatter

This project uses Black. Simply run `black .` from the base directory.

## Usable Flags

Note that flags can be combined into strings prepended with a dash, so "-dx" would run both "-d" and "-x".

1. "-d" **Debug Mode**
   * Debug mode, prints all available fetched data for a symbol.
2. "-x" **Excel Update/Creation**
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
3. Add/use helper functions to convert larger numbers to use M/B/T abbreviations for millions, billions, etc.
   * This would improve readability of some output and prevent misreading large numbers by the user.
4. Fetch a subset of Stock symbols to check for the day.
   * E.g. scraping a FinViz search and checking the symbols that are returned.
5. Some symbols on Yahoo (e.g. YYY) fetch a different format page.
   * Adjust methods to handle either version of the page
   * https://finance.yahoo.com/quote/YYY vs https://finance.yahoo.com/quote/BGS demonstrates the difference.
   * This is because YYY is an ETF and not a company. Funds have different data about them entirely, figure a way to analyze these.
6. Add unit tests for the `handler.py` methods.
   * Check handling of Nonetypes, Ints/Floats, String nums, numbers with commas, etc. are handled well.
7. Implement a way to print out which years dividends were missed/reduced in a symbols weaknesses.
8. Add the dividend Payout Ratio to the console logs.
9. Add a description of whether BVPS or EPS is higher to the console logs for the Graham number.
10. Add a helper function to adjust urls to either use `.` or `-`as required by a website for scraping.
11. Setup test coverage tools on the repo.
12. Add the criteria number that a symbol is weak in to allow for easier manual review.
13. Reformat the console output to be clearer and more aesthetic. Also add some color.
14. Design around handling non-US companies and fetched values. Test with ASUSTeK, which is 2357 on TW(Taiwanese exchange))
15. Use Log scale for color gradient. Could use percentage deviations as well. Could also weight based on where the weakness is (how many years ago).
16. Apply color gradient to each Criteria passing/failing.
17. Add a inverse of str_to_num method for appending B/M/T to large numbers. This will assist in readability of output.